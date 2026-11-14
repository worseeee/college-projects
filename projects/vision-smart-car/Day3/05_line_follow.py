# -*- coding: utf-8 -*-
"""Preview visual line following or drive the Raspberry Pi car with auto gimbal."""

import argparse
from collections import deque
from pathlib import Path
import time

import cv2

from vision_utils import (
    add_decision_overlay,
    make_video_writer,
    open_video_source,
    parse_source,
    process_lane_frame,
    write_image,
)


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def normalized_x_error(cx, width):
    """Return line error in [-1, 1]; positive means the line is to the right."""
    if width <= 0:
        raise ValueError("width must be positive")
    return clamp((float(cx) - width / 2.0) / (width / 2.0), -1.0, 1.0)


def classify_error(error, deadband):
    if error is None:
        return "LOST"
    if error < -deadband:
        return "LEFT"
    if error > deadband:
        return "RIGHT"
    return "STRAIGHT"


def calculate_wheel_speeds(
    error,
    speed,
    steering_gain,
    min_drive_pwm,
    pivot_threshold=0.72,
    pivot_strength=1.0,
):
    """Convert lane error to differential PWM, tightening sharp turns smoothly."""
    speed = int(clamp(int(speed), 0, 100))
    min_drive_pwm = int(clamp(int(min_drive_pwm), 0, 100))
    gain = float(clamp(float(steering_gain), 0.0, 1.0))
    pivot_threshold = float(clamp(float(pivot_threshold), 0.0, 0.99))
    pivot_strength = float(clamp(float(pivot_strength), 0.0, 1.0))
    if error is None or speed == 0:
        return 0, 0

    # Keep the calibrated start PWM as the baseline and outer-wheel floor.
    # The inner wheel must be allowed to slow below that floor to turn tightly.
    base = max(speed, min_drive_pwm)
    error = clamp(float(error), -1.0, 1.0)
    magnitude = abs(error)
    correction = magnitude * base * gain
    inner = base - correction
    outer = base + correction

    # At large errors, blend the inner wheel smoothly through zero and into
    # reverse so the chassis can pivot into a corner instead of driving wide.
    if magnitude > pivot_threshold:
        pressure = (magnitude - pivot_threshold) / max(1e-6, 1.0 - pivot_threshold)
        pressure *= pivot_strength
        inner = inner * (1.0 - pressure) - min_drive_pwm * pressure

    if error > 0:
        left, right = outer, inner
    else:
        left, right = inner, outer

    # The car's calibrated minimum PWM is also the minimum useful reverse
    # command; below it the inner wheel would hum without turning.
    if error > 0 and right < 0:
        right = -max(min_drive_pwm, abs(right))
    elif error < 0 and left < 0:
        left = -max(min_drive_pwm, abs(left))

    peak = max(abs(left), abs(right))
    if peak > 100:
        scale = 100.0 / peak
        left *= scale
        right *= scale

    return (
        int(round(clamp(left, -100.0, 100.0))),
        int(round(clamp(right, -100.0, 100.0))),
    )


def apply_drive_command(car, error, speed, steering_gain, min_drive_pwm,
                        pivot_threshold=0.72, pivot_strength=1.0):
    left_pwm, right_pwm = calculate_wheel_speeds(
        error, speed, steering_gain, min_drive_pwm,
        pivot_threshold=pivot_threshold,
        pivot_strength=pivot_strength,
    )
    if error is None or (left_pwm == 0 and right_pwm == 0):
        car.stop()
    else:
        car.set_wheels(left_pwm, right_pwm)
    return left_pwm, right_pwm


def run_motor_test(car, speed_levels):
    """Run an explicit, confirmed, forward-only motor test with wheels raised."""
    levels = sorted({int(clamp(level, 20, 40)) for level in speed_levels})
    print("Motor self-test: raise the drive wheels and keep clear of moving parts.")
    try:
        answer = input("Confirm the wheels are raised; type YES to continue: ").strip()
    except EOFError:
        answer = ""
    if answer != "YES":
        print("Motor self-test cancelled.")
        return False

    try:
        for level in levels:
            for name, wheels in (("left", (level, 0)), ("right", (0, level))):
                print(f"Motor self-test: {name} wheel forward at PWM {level}%")
                car.set_wheels(*wheels)
                time.sleep(0.35)
                car.stop()
                time.sleep(0.25)
    finally:
        car.stop()
    return True


class GimbalTracker:
    """Rate-limited pan/tilt tracker using the Day3 PCA9685 gimbal interface."""

    def __init__(self, pan_sign=-1, tilt_sign=1, update_interval=0.10,
                 pan_deadband=0.10, tilt_deadband=0.04,
                 pan_gain=8.0, max_pan_step=2, search_step=1):
        from common import car_config as cfg
        from common.gimbal import Gimbal

        self.cfg = cfg
        self.gimbal = Gimbal()
        self.pan = int(cfg.PAN_CENTER)
        self.tilt = int(cfg.TILT_LEVEL)
        self.pan_min = int(cfg.PAN_LEFT)
        self.pan_max = int(cfg.PAN_RIGHT)
        self.tilt_min = int(cfg.TILT_DOWN)
        self.tilt_max = int(cfg.TILT_UP)
        self.pan_sign = int(pan_sign)
        self.tilt_sign = int(tilt_sign)
        self.update_interval = max(0.03, float(update_interval))
        self.pan_deadband = max(0.0, float(pan_deadband))
        self.tilt_deadband = max(0.0, float(tilt_deadband))
        self.pan_gain = max(0.1, float(pan_gain))
        self.max_pan_step = max(1, int(max_pan_step))
        self.search_step = max(1, int(search_step))
        self.last_update = 0.0
        # On the current car, decreasing the pan angle points the camera right.
        # After a brief line loss, search in the last corrective direction.
        self.search_direction = self.pan_sign
        self.search_min = max(self.pan_min, self.pan - 30)
        self.search_max = min(self.pan_max, self.pan + 30)
        self.gimbal.set_angles(self.pan, self.tilt)

    def _write(self):
        self.gimbal.set_angles(self.pan, self.tilt)

    def update(self, centroid, width, height, roi_top, now=None, target_row=None,
               target_x=None):
        """Adjust aim toward the line; on line loss, search only while car is stopped."""
        now = time.monotonic() if now is None else float(now)
        if now - self.last_update < self.update_interval:
            return self.pan, self.tilt
        self.last_update = now

        if centroid is None:
            next_pan = self.pan + self.search_direction * self.search_step
            if next_pan >= self.search_max:
                next_pan = self.search_max
                self.search_direction = -1
            elif next_pan <= self.search_min:
                next_pan = self.search_min
                self.search_direction = 1
            if next_pan != self.pan:
                self.pan = next_pan
                self._write()
            return self.pan, self.tilt

        cx = centroid[0] if target_x is None else target_x
        cy = centroid[1]
        x_error = normalized_x_error(cx, width)
        corrective_pan = self.pan_sign * x_error
        if abs(x_error) > self.pan_deadband:
            self.search_direction = 1 if corrective_pan > 0 else -1
        target_y_fraction = (
            (roi_top + 1.0) / 2.0 if target_row is None else float(target_row)
        )
        target_y = int(height * clamp(target_y_fraction, 0.0, 1.0))
        y_error = clamp((target_y - float(cy)) / max(1.0, height), -0.5, 0.5)

        # Limit movement per update to avoid servo chatter and abrupt camera jumps.
        pan_step = 0
        if abs(x_error) > self.pan_deadband:
            pan_step = int(
                round(
                    clamp(
                        corrective_pan * self.pan_gain,
                        -self.max_pan_step,
                        self.max_pan_step,
                    )
                )
            )
        tilt_step = 0
        if abs(y_error) > self.tilt_deadband:
            tilt_step = int(
                round(clamp(self.tilt_sign * y_error * 24.0, -2.0, 2.0))
            )
        self.pan = int(clamp(self.pan + pan_step, self.pan_min, self.pan_max))
        self.tilt = int(clamp(self.tilt + tilt_step, self.tilt_min, self.tilt_max))
        if pan_step or tilt_step:
            self._write()
        return self.pan, self.tilt


def draw_telemetry(image, cx, cy, track_error, control_error,
                   left_pwm, right_pwm, pan, tilt, driving):
    """Add compact and readable drive/gimbal telemetry to the camera window."""
    height, width = image.shape[:2]
    center_x = width // 2
    center_color = (0, 255, 255)
    cv2.line(image, (center_x, 0), (center_x, height - 1), center_color, 2)
    cv2.putText(
        image,
        f"FRAME CENTER x={center_x}",
        (min(max(4, width - 190), center_x + 5), height - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        center_color,
        2,
        cv2.LINE_AA,
    )
    pwm_label = "PWM output" if driving else "PWM target only"
    lines = [
        f"Line: cx={cx if cx is not None else '---'} cy={cy if cy is not None else '---'}",
        f"Err: image={track_error:+.2f} control={control_error:+.2f}"
        if track_error is not None and control_error is not None
        else "Err: image=--- control=---",
        f"{pwm_label}: L={left_pwm:02d}% R={right_pwm:02d}%",
        "GPIO MOTOR CONTROL ACTIVE" if driving
        else "MOTORS DISABLED - restart with --drive",
    ]
    if pan is not None and tilt is not None:
        lines.append(f"Gimbal: pan={pan} deg tilt={tilt} deg")
    for index, line in enumerate(lines):
        color = (0, 0, 255) if not driving and index == 3 else (30, 60, 210)
        cv2.putText(
            image,
            line,
            (12, 112 + index * 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2 if index == 3 else 1,
            cv2.LINE_AA,
        )
    return image


def main():
    parser = argparse.ArgumentParser(
        description="Follow a dark lane from a live camera, optionally driving a Raspberry Pi car"
    )
    parser.add_argument("--source", default="0", help="Camera index or video file")
    parser.add_argument("--camera-backend", choices=("auto", "opencv", "picamera2"),
                        default="auto", help="Camera API; auto falls back to Picamera2 on Linux")
    parser.add_argument("--camera-format", choices=("auto", "mjpg", "yuyv"),
                        default="auto", help="V4L2 format to try for a USB camera")
    parser.add_argument("--camera-width", type=int, default=640)
    parser.add_argument("--camera-height", type=int, default=480)
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--output", help="Optional processed MP4 output path")
    parser.add_argument("--snapshot", default="results/05_line_follow_snapshot.png")
    parser.add_argument("--snapshot-frame", type=int, default=0, help="Frame index to save in headless mode")
    parser.add_argument("--threshold", type=int, default=110,
                        help="Gray threshold used only with --threshold-mode fixed")
    parser.add_argument("--threshold-mode", choices=("otsu", "fixed"), default="otsu",
                        help="Per-frame Otsu threshold adapts to new light-background tracks")
    parser.add_argument("--roi-top", type=float, default=0.30,
                        help="Top of the detection region as a frame fraction")
    parser.add_argument("--min-area", type=float, default=120)
    parser.add_argument("--near-row", type=float, default=0.70,
                        help="Image row fraction used for vehicle steering")
    parser.add_argument("--lookahead-row", type=float, default=0.62,
                        help="Image row fraction used to aim at upcoming track")
    parser.add_argument("--lookahead-weight", type=float, default=0.35,
                        help="Blend of far-track error used to begin turns earlier, 0-1")
    parser.add_argument("--morphology-kernel", type=int, default=3,
                        help="Noise cleanup kernel; keep small for narrow tape")
    parser.add_argument("--deadband", type=float, default=0.10)
    parser.add_argument("--smoothing-frames", type=int, default=3)
    parser.add_argument("--reacquire-frames", type=int, default=3)
    parser.add_argument("--speed", type=int, default=45, help="Requested cruise PWM, 0-100")
    parser.add_argument("--min-drive-pwm", type=int, default=35,
                        help="Minimum effective PWM while moving; calibrate on the car")
    parser.add_argument("--steering-gain", type=float, default=0.75,
                        help="Continuous differential steering strength, 0-1")
    parser.add_argument("--pivot-threshold", type=float, default=0.72,
                        help="Start tightening sharp turns above this normalized error")
    parser.add_argument("--pivot-strength", type=float, default=1.0,
                        help="Inner-wheel reverse strength for sharp turns, 0-1")
    parser.add_argument("--pan-compensation", type=float, default=0.65,
                        help="How much gimbal pan angle contributes to steering")
    parser.add_argument("--pan-sign", type=int, choices=(-1, 1), default=-1,
                        help="Current car uses -1; use 1 if the pan direction is reversed")
    parser.add_argument("--tilt-sign", type=int, choices=(-1, 1), default=1,
                        help="Use -1 if increasing tilt angle points the camera down")
    parser.add_argument("--gimbal-interval", type=float, default=0.10,
                        help="Minimum seconds between servo updates")
    parser.add_argument("--gimbal-pan-gain", type=float, default=8.0,
                        help="Pan response gain to horizontal lookahead error")
    parser.add_argument("--gimbal-max-step", type=int, default=2,
                        help="Maximum pan angle change per servo update, in degrees")
    parser.add_argument("--gimbal-search-step", type=int, default=1,
                        help="Pan scan step while the track is temporarily lost")
    parser.add_argument("--gimbal-pan-deadband", type=float, default=0.10,
                        help="Normalized horizontal image deadband for pan")
    parser.add_argument("--gimbal-tilt-deadband", type=float, default=0.04,
                        help="Normalized vertical image deadband for tilt")
    gimbal_group = parser.add_mutually_exclusive_group()
    gimbal_group.add_argument("--auto-gimbal", action="store_true",
                              help="Enable camera tracking without enabling motor output")
    gimbal_group.add_argument("--no-auto-gimbal", action="store_true",
                              help="Disable pan/tilt tracking while driving")
    parser.add_argument("--motor-test", action="store_true",
                        help="Run a confirmed forward-only motor test before following")
    parser.add_argument("--status-interval", type=float, default=0.5,
                        help="Seconds between terminal status updates")
    parser.add_argument("--drive", action="store_true", help="Enable Raspberry Pi GPIO motor output")
    parser.add_argument("--headless", action="store_true", help="Process a video without opening windows")
    args = parser.parse_args()

    args.speed = int(clamp(args.speed, 0, 100))
    args.min_drive_pwm = int(clamp(args.min_drive_pwm, 0, 100))
    args.steering_gain = float(clamp(args.steering_gain, 0.0, 1.0))
    args.pivot_threshold = float(clamp(args.pivot_threshold, 0.0, 0.99))
    args.pivot_strength = float(clamp(args.pivot_strength, 0.0, 1.0))
    args.pan_compensation = float(clamp(args.pan_compensation, 0.0, 2.0))
    args.deadband = float(clamp(args.deadband, 0.0, 0.8))
    args.roi_top = float(clamp(args.roi_top, 0.0, 0.9))
    args.near_row = float(clamp(args.near_row, 0.05, 0.98))
    args.lookahead_row = float(clamp(args.lookahead_row, 0.05, 0.95))
    args.lookahead_weight = float(clamp(args.lookahead_weight, 0.0, 0.8))
    args.morphology_kernel = max(1, int(args.morphology_kernel))
    args.gimbal_pan_gain = float(clamp(args.gimbal_pan_gain, 0.1, 30.0))
    args.gimbal_max_step = int(clamp(args.gimbal_max_step, 1, 5))
    args.gimbal_search_step = int(clamp(args.gimbal_search_step, 1, 5))
    args.reacquire_frames = max(1, int(args.reacquire_frames))
    args.status_interval = max(0.1, float(args.status_interval))

    source = parse_source(args.source)
    if args.drive and not isinstance(source, int):
        parser.error("--drive requires a live camera index; recorded files are preview-only")
    if args.motor_test and not args.drive:
        parser.error("--motor-test requires --drive")
    if args.no_auto_gimbal:
        auto_gimbal = False
    else:
        auto_gimbal = args.drive or args.auto_gimbal

    try:
        cap = open_video_source(
            source,
            backend=args.camera_backend,
            width=args.camera_width,
            height=args.camera_height,
            fps=args.camera_fps,
            pixel_format=args.camera_format,
        )
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(
            f"Camera startup failed before motor initialization.\n{exc}"
        ) from exc
    print(f"Camera backend ready: {cap.backend_name}")

    car = None
    gimbal = None
    writer = None
    fps = cap.get(cv2.CAP_PROP_FPS)
    centroids = deque(maxlen=max(1, args.smoothing_frames))
    gimbal_centroids = deque(maxlen=max(1, args.smoothing_frames))
    previous_near_x = None
    previous_lookahead_x = None
    lost_frames = 0
    decision_counts = {"LEFT": 0, "STRAIGHT": 0, "RIGHT": 0, "LOST": 0, "ACQUIRE": 0}
    frame_count = 0
    reacquire_count = 0
    snapshot_saved = False
    fallback_snapshot = None
    last_status_time = 0.0
    last_decision = None
    reported_pan = None

    try:
        if args.drive:
            try:
                from common.motor import Car
            except ImportError as exc:
                raise RuntimeError(
                    "GPIO motor output is available only on the Raspberry Pi environment"
                ) from exc
            car = Car()
            print("GPIO drive enabled; keep the car on a clear test lane.")
            if args.motor_test:
                if not run_motor_test(car, (20, 30, 40)):
                    print("Drive mode cancelled; no autonomous movement started.")
                    return

        if auto_gimbal:
            try:
                gimbal = GimbalTracker(
                    pan_sign=args.pan_sign,
                    tilt_sign=args.tilt_sign,
                    update_interval=args.gimbal_interval,
                    pan_deadband=args.gimbal_pan_deadband,
                    tilt_deadband=args.gimbal_tilt_deadband,
                    pan_gain=args.gimbal_pan_gain,
                    max_pan_step=args.gimbal_max_step,
                    search_step=args.gimbal_search_step,
                )
            except Exception as exc:
                if car:
                    car.stop()
                raise RuntimeError(
                    "Could not initialize the auto gimbal. Check PCA9685 wiring/library "
                    "or rerun with --no-auto-gimbal."
                ) from exc
            print(
                f"Auto gimbal enabled at pan={gimbal.pan} tilt={gimbal.tilt} "
                f"pan-sign={args.pan_sign}; "
                "use --no-auto-gimbal to disable."
            )
        if not args.drive:
            print("\n*** PREVIEW ONLY: GPIO MOTOR OUTPUT IS OFF ***")
            print(
                "On the Raspberry Pi run: "
                "python3 05_line_follow.py --source 0 --drive --speed 30"
            )

        while True:
            ret, frame = cap.read()
            if not ret:
                if car:
                    car.stop()
                print("Video ended or camera frame unavailable; motors stopped.")
                break

            height, width = frame.shape[:2]
            result = process_lane_frame(
                frame,
                threshold=args.threshold,
                roi_top=args.roi_top,
                min_area=args.min_area,
                invert=True,
                kernel_size=args.morphology_kernel,
                threshold_mode=args.threshold_mode,
                near_row=args.near_row,
                lookahead_row=args.lookahead_row,
                near_reference_x=previous_near_x,
                lookahead_reference_x=previous_lookahead_x,
            )

            control_point = result["near_point"] or result["centroid"]
            camera_point = result["lookahead_point"] or control_point
            if control_point is None:
                centroids.clear()
                gimbal_centroids.clear()
                reacquire_count = 0
                lost_frames += 1
                if lost_frames >= 12:
                    previous_near_x = None
                    previous_lookahead_x = None
                smoothed_centroid = None
                smoothed_gimbal_centroid = None
                near_error = None
                lookahead_error = None
                image_error = None
                decision = "LOST"
                # Stop before any gimbal I2C update or other per-frame work.
                if car:
                    car.stop()
            else:
                lost_frames = 0
                if result["near_point"] is not None:
                    previous_near_x = result["near_point"][0]
                if result["lookahead_point"] is not None:
                    previous_lookahead_x = result["lookahead_point"][0]
                centroids.append(control_point)
                gimbal_centroids.append(camera_point)
                smoothed_centroid = (
                    int(sum(point[0] for point in centroids) / len(centroids)),
                    int(sum(point[1] for point in centroids) / len(centroids)),
                )
                smoothed_gimbal_centroid = (
                    int(sum(point[0] for point in gimbal_centroids) / len(gimbal_centroids)),
                    int(sum(point[1] for point in gimbal_centroids) / len(gimbal_centroids)),
                )
                reacquire_count += 1
                near_error = normalized_x_error(smoothed_centroid[0], width)
                lookahead_error = normalized_x_error(
                    smoothed_gimbal_centroid[0], width
                )
                weight = args.lookahead_weight
                image_error = (
                    near_error * (1.0 - weight) + lookahead_error * weight
                )
                if car and reacquire_count < args.reacquire_frames:
                    decision = "ACQUIRE"
                else:
                    decision = "STRAIGHT"  # final direction is assigned after pan compensation

            if gimbal:
                pan, tilt = gimbal.update(
                    smoothed_centroid,
                    width,
                    height,
                    args.roi_top,
                    target_row=args.lookahead_row,
                    target_x=(
                        smoothed_gimbal_centroid[0]
                        if smoothed_gimbal_centroid is not None else None
                    ),
                )
            else:
                pan, tilt = None, None

            if image_error is None:
                control_error = None
            else:
                pan_error = 0.0
                if pan is not None:
                    pan_span = max(1.0, (gimbal.pan_max - gimbal.pan_min) / 2.0)
                    pan_error = args.pan_sign * (pan - gimbal.cfg.PAN_CENTER) / pan_span
                control_error = clamp(
                    image_error + args.pan_compensation * pan_error, -1.0, 1.0
                )
                if decision != "ACQUIRE":
                    decision = classify_error(control_error, args.deadband)

            if decision in ("LOST", "ACQUIRE"):
                left_pwm, right_pwm = (0, 0)
            else:
                drive_error = 0.0 if decision == "STRAIGHT" else control_error
                left_pwm, right_pwm = calculate_wheel_speeds(
                    drive_error,
                    args.speed,
                    args.steering_gain,
                    args.min_drive_pwm,
                    args.pivot_threshold,
                    args.pivot_strength,
                )
            if car:
                if decision in ("LOST", "ACQUIRE"):
                    car.stop()
                else:
                    car.set_wheels(left_pwm, right_pwm)

            decision_counts[decision] += 1
            overlay = add_decision_overlay(result["overlay"], decision)
            draw_telemetry(
                overlay,
                smoothed_centroid[0] if smoothed_centroid else None,
                smoothed_centroid[1] if smoothed_centroid else None,
                image_error,
                control_error,
                left_pwm,
                right_pwm,
                pan if gimbal else None,
                tilt if gimbal else None,
                bool(car),
            )

            if args.output and writer is None:
                writer = make_video_writer(args.output, fps, (width, height))
            if writer:
                writer.write(overlay)
            if args.headless and fallback_snapshot is None:
                fallback_snapshot = overlay.copy()
            if args.headless and not snapshot_saved and frame_count == max(0, args.snapshot_frame):
                write_image(args.snapshot, overlay)
                snapshot_saved = True

            now = time.monotonic()
            if decision != last_decision and decision in ("LOST", "ACQUIRE"):
                print(f"Line state: {decision}; motors {'stopped' if car else 'preview only'}.")
            if now - last_status_time >= args.status_interval:
                center_text = (
                    f"({smoothed_centroid[0]}, {smoothed_centroid[1]})"
                    if smoothed_centroid else "none"
                )
                aim_text = (
                    f"({smoothed_gimbal_centroid[0]}, {smoothed_gimbal_centroid[1]})"
                    if smoothed_gimbal_centroid else "none"
                )
                if gimbal:
                    pan_delta = 0 if reported_pan is None else pan - reported_pan
                    gimbal_text = (
                        f" aim={aim_text} pan={pan} dpan={pan_delta:+d} "
                        f"tilt={tilt} pan-sign={args.pan_sign}"
                    )
                    reported_pan = pan
                else:
                    gimbal_text = ""
                image_error_text = (
                    f"{image_error:.2f}" if image_error is not None else "none"
                )
                control_error_text = (
                    f"{control_error:.2f}" if control_error is not None else "none"
                )
                near_error_text = (
                    f"{near_error:.2f}" if near_error is not None else "none"
                )
                lookahead_error_text = (
                    f"{lookahead_error:.2f}" if lookahead_error is not None else "none"
                )
                mode_text = "DRIVE_ACTIVE" if car else "PREVIEW_ONLY"
                pwm_text = "PWM_OUTPUT" if car else "PWM_TARGET_ONLY"
                print(
                    f"mode={mode_text} decision={decision} line={center_text} "
                    f"near_error={near_error_text} lookahead_error={lookahead_error_text} "
                    f"image_error={image_error_text} control_error={control_error_text} "
                    f"{pwm_text}=L{left_pwm}/R{right_pwm}{gimbal_text}"
                )
                last_status_time = now
            last_decision = decision
            frame_count += 1

            if not args.headless:
                cv2.imshow("Day3 Visual Line Follow", overlay)
                cv2.imshow("Threshold ROI", result["binary"])
                key = cv2.waitKey(1) & 0xFF
                if key == ord("s"):
                    write_image(args.snapshot, overlay)
                    snapshot_saved = True
                    print(f"Snapshot saved: {Path(args.snapshot).resolve()}")
                elif key == ord("q") or key == 27:
                    if car:
                        car.stop()
                    break
    finally:
        if car:
            try:
                car.stop()
                car.cleanup()
            except Exception as exc:
                print(f"Motor cleanup warning: {exc}")
        cap.release()
        if writer:
            writer.release()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass

    if args.output:
        print(f"Processed video saved: {Path(args.output).resolve()}")
    print(f"Frames={frame_count}; decisions={decision_counts}")
    if args.headless and not snapshot_saved and fallback_snapshot is not None:
        write_image(args.snapshot, fallback_snapshot)
        snapshot_saved = True
    if args.headless and snapshot_saved:
        print(f"Snapshot saved: {Path(args.snapshot).resolve()}")


if __name__ == "__main__":
    main()
