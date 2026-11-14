# -*- coding: utf-8 -*-
"""Interactive camera/video runner used by the Day4 command-line programs."""

import argparse
from datetime import datetime
from pathlib import Path
import sys
import time

import cv2

from tracking_core import (
    DEFAULT_HSV,
    FaceDetector,
    SafetyController,
    TargetLock,
    detect_ball,
    draw_overlay,
)
from vision_utils import make_video_writer, open_video_source, parse_source, write_image


BASE_DIR = Path(__file__).resolve().parent
WINDOW_MAIN = "Day4 Visual Tracker"
WINDOW_HSV = "HSV Controls"
WINDOW_MASK = "HSV Mask"


def _noop(_value):
    return None


def open_hsv_controls():
    cv2.namedWindow(WINDOW_HSV, cv2.WINDOW_NORMAL)
    initial = DEFAULT_HSV
    sliders = (
        ("H min", initial[0], 179), ("H max", initial[1], 179),
        ("S min", initial[2], 255), ("S max", initial[3], 255),
        ("V min", initial[4], 255), ("V max", initial[5], 255),
    )
    for name, value, maximum in sliders:
        cv2.createTrackbar(name, WINDOW_HSV, int(value), int(maximum), _noop)
    cv2.namedWindow(WINDOW_MASK, cv2.WINDOW_NORMAL)


def read_hsv_controls():
    names = ("H min", "H max", "S min", "S max", "V min", "V max")
    return tuple(cv2.getTrackbarPos(name, WINDOW_HSV) for name in names)


def build_parser(default_mode="ball", fused=False):
    parser = argparse.ArgumentParser(
        description="Day4 OpenCV ball/face visual tracking; GPIO stays disabled unless --drive is supplied."
    )
    parser.add_argument("--source", default="0", help="camera index (0, 1, ...) or video file")
    if fused:
        parser.add_argument("--mode", choices=("ball", "face"), default=default_mode,
                            help="initial mode; press 1/2 to switch while running")
    parser.add_argument("--drive", action="store_true",
                        help="enable Raspberry Pi GPIO motor output; camera source only")
    parser.add_argument("--speed", type=int, default=35, help="forward PWM percentage (0-100)")
    parser.add_argument("--ball-stop-radius", type=float, default=100,
                        help="stop when tracked ball radius reaches this many pixels at 640px width")
    parser.add_argument("--face-stop-width", type=float, default=100,
                        help="stop when face width reaches this many pixels at 640px width")
    parser.add_argument("--deadband", type=float, default=30,
                        help="horizontal target deadband in pixels at 640px width")
    parser.add_argument("--turn-gain", type=float, default=1.45,
                        help="differential steering gain; tune in preview before enabling GPIO")
    parser.add_argument("--hough-param1", type=int, default=120, help="Hough Canny edge threshold")
    parser.add_argument("--hough-param2", type=int, default=28,
                        help="Hough accumulator threshold; lower values detect weaker circles")
    parser.add_argument("--cascade", default=str(BASE_DIR / "face.xml"),
                        help="Haar cascade XML used by face mode")
    parser.add_argument("--face-scale-factor", type=float, default=1.1)
    parser.add_argument("--face-min-neighbors", type=int, default=4)
    parser.add_argument("--camera-backend", choices=("auto", "opencv", "picamera2"), default="auto")
    parser.add_argument("--camera-format", choices=("auto", "mjpg", "yuyv"), default="auto")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--output-dir", default=str(BASE_DIR / "results"))
    parser.add_argument("--output-video", help="write every annotated frame to this video file")
    parser.add_argument("--record-on-start", action="store_true",
                        help="start recording immediately (otherwise press r)")
    parser.add_argument("--max-frames", type=int, default=0,
                        help="stop after this many frames; 0 means until camera/video ends")
    parser.add_argument("--no-window", action="store_true",
                        help="run without GUI windows; useful for offline conversion or SSH")
    parser.add_argument("--no-trackbars", action="store_true",
                        help="use taskbook HSV defaults instead of opening six sliders")
    parser.add_argument("--print-interval", type=float, default=0.5,
                        help="seconds between terminal status lines")
    return parser


def _face_detector(args, cache):
    if cache[0] is None:
        cache[0] = FaceDetector(
            args.cascade,
            scale_factor=args.face_scale_factor,
            min_neighbors=args.face_min_neighbors,
        )
    return cache[0]


def _recording_path(output_dir, mode, requested=None):
    if requested:
        return Path(requested)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(output_dir) / "day4_{}_{}.mp4".format(mode, stamp)


def run(args, fused=False, fixed_mode="ball"):
    source = parse_source(args.source)
    if args.drive and not isinstance(source, int):
        raise ValueError("--drive is accepted only with a live camera index; video files are preview-only")
    args.speed = max(0, min(100, int(args.speed)))
    args.width = max(1, int(args.width))
    args.height = max(1, int(args.height))
    args.max_frames = max(0, int(args.max_frames))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Probe the camera/video before GPIO initialization. This avoids leaving the
    # motor controller active when a camera is busy or unsupported.
    capture = open_video_source(
        source,
        backend=args.camera_backend,
        width=args.width,
        height=args.height,
        fps=args.camera_fps,
        pixel_format=args.camera_format,
    )
    car = None
    writer = None
    recording = False
    recording_pending = bool(args.output_video or args.record_on_start)
    frames_seen = 0
    last_print = 0.0
    lock = TargetLock()
    safety = SafetyController(
        ball_stop_radius=args.ball_stop_radius,
        face_stop_width=args.face_stop_width,
        deadband_pixels=args.deadband,
        turn_gain=args.turn_gain,
    )
    mode = args.mode if fused else fixed_mode
    detector_cache = [None]
    show_windows = not args.no_window
    trackbars_open = False
    paused = False
    source_label = "camera:{}".format(source) if isinstance(source, int) else Path(source).name
    fps = capture.get(cv2.CAP_PROP_FPS) or args.camera_fps

    try:
        if args.drive:
            try:
                from common.motor import Car
            except Exception as exc:
                raise RuntimeError(
                    "Cannot import Day4/common/motor.py. Run on the Raspberry Pi with "
                    "RPi.GPIO installed and keep the Day4/common folder beside this script."
                ) from exc
            car = Car()
            car.stop()
            print("GPIO drive enabled at {}% PWM. Keep the car on a clear test area.".format(args.speed))
        else:
            print("Preview only: no motor commands will be sent. Use --drive on the Raspberry Pi for GPIO control.")

        if show_windows:
            cv2.namedWindow(WINDOW_MAIN, cv2.WINDOW_NORMAL)
            if mode == "ball" and not args.no_trackbars:
                open_hsv_controls()
                trackbars_open = True
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                break
            frames_seen += 1
            height, width = frame.shape[:2]
            hsv_values = DEFAULT_HSV
            mask = None
            if mode == "ball":
                if show_windows and trackbars_open:
                    hsv_values = read_hsv_controls()
                mask, candidates = detect_ball(
                    frame,
                    hsv_values=hsv_values,
                    hough_param1=args.hough_param1,
                    hough_param2=args.hough_param2,
                )
            else:
                detector = _face_detector(args, detector_cache)
                _gray, candidates = detector.detect(frame)

            target = lock.update(candidates, width, height)
            decision, left_pwm, right_pwm = safety.command(
                mode, target, width, args.speed, paused=paused
            )
            if car is not None:
                if left_pwm or right_pwm:
                    car.set_wheels(left_pwm, right_pwm)
                else:
                    car.stop()

            overlay = draw_overlay(
                frame, mode, target, decision, left_pwm, right_pwm,
                args.speed, drive_enabled=(car is not None), paused=paused,
                recording=recording, source_label=source_label,
            )
            if not args.drive:
                cv2.putText(overlay, "NO GPIO OUTPUT", (max(8, width - 170), 24),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 210, 255), 1, cv2.LINE_AA)
            if recording_pending and writer is None:
                path = _recording_path(output_dir, mode, args.output_video)
                path.parent.mkdir(parents=True, exist_ok=True)
                writer = make_video_writer(path, fps, (width, height))
                recording = True
                recording_pending = False
                print("Recording annotated output to {}".format(path))
            if writer is not None:
                writer.write(overlay)
            if show_windows:
                cv2.imshow(WINDOW_MAIN, overlay)
                if mask is not None and trackbars_open:
                    cv2.imshow(WINDOW_MASK, mask)

            now = time.monotonic()
            if now - last_print >= max(0.1, args.print_interval):
                target_description = "none" if target is None else "({:.0f},{:.0f}) size={:.1f}".format(
                    target["x"], target["y"], target["metric"]
                )
                output_kind = "GPIO" if car is not None else "PREVIEW"
                print("mode={} decision={} target={} PWM_TARGET=L{}/R{} output={}".format(
                    mode.upper(), decision, target_description, left_pwm, right_pwm, output_kind
                ))
                last_print = now

            if args.max_frames and frames_seen >= args.max_frames:
                break
            if show_windows:
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
                if key == ord(" "):
                    paused = not paused
                    print("Safety pause {}".format("enabled" if paused else "released"))
                elif key == ord("s"):
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    still_path = output_dir / "{}_{}.png".format(mode, stamp)
                    write_image(still_path, overlay)
                    if mask is not None:
                        write_image(output_dir / "{}_{}_mask.png".format(mode, stamp), mask)
                    print("Saved screenshot: {}".format(still_path))
                elif key == ord("r"):
                    if writer is not None:
                        writer.release()
                        writer = None
                        recording = False
                        print("Recording stopped.")
                    else:
                        path = _recording_path(output_dir, mode)
                        writer = make_video_writer(path, fps, (width, height))
                        recording = True
                        print("Recording started: {}".format(path))
                elif fused and key in (ord("1"), ord("2")):
                    new_mode = "ball" if key == ord("1") else "face"
                    if new_mode != mode:
                        if car is not None:
                            car.stop()
                        lock.reset()
                        safety.reset(new_mode)
                        mode = new_mode
                        if mode == "face":
                            _face_detector(args, detector_cache)
                            if trackbars_open:
                                cv2.destroyWindow(WINDOW_HSV)
                                cv2.destroyWindow(WINDOW_MASK)
                                trackbars_open = False
                        elif not args.no_trackbars:
                            open_hsv_controls()
                            trackbars_open = True
                        print("Switched to {} mode; target lock reset and motors stopped.".format(mode))

        return 0
    finally:
        if car is not None:
            try:
                car.stop()
            finally:
                car.cleanup()
        if writer is not None:
            writer.release()
        capture.release()
        if show_windows:
            cv2.destroyAllWindows()


def main_cli(default_mode="ball", fused=False, argv=None):
    parser = build_parser(default_mode=default_mode, fused=fused)
    args = parser.parse_args(argv)
    try:
        return run(args, fused=fused, fixed_mode=default_mode)
    except KeyboardInterrupt:
        print("Interrupted; stopping and releasing resources.")
        return 130
    except Exception as exc:
        print("Day4 tracker error: {}".format(exc), file=sys.stderr)
        return 1

