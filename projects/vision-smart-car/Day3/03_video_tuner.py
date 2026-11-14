# -*- coding: utf-8 -*-
"""Live or recorded-video tuner with threshold trackbars."""

import argparse
from pathlib import Path

import cv2

from vision_utils import (
    make_montage,
    make_video_writer,
    open_video_source,
    parse_source,
    write_image,
)


def _noop(_value):
    pass


def main():
    parser = argparse.ArgumentParser(description="Tune threshold parameters on camera/video")
    parser.add_argument("--source", default="0", help="Camera index (0) or video file")
    parser.add_argument("--camera-backend", choices=("auto", "opencv", "picamera2"), default="auto")
    parser.add_argument("--camera-format", choices=("auto", "mjpg", "yuyv"), default="auto")
    parser.add_argument("--camera-width", type=int, default=640)
    parser.add_argument("--camera-height", type=int, default=480)
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--output", help="Optional side-by-side MP4 output path")
    parser.add_argument("--snapshot", default="results/03_video_tuning_snapshot.png")
    parser.add_argument("--headless", action="store_true", help="Process a video without opening windows")
    parser.add_argument("--threshold", type=int, default=110, help="Fixed threshold for headless processing")
    parser.add_argument("--blur-radius", type=int, default=2, help="Blur radius; kernel is 2*r+1")
    parser.add_argument("--normal-line", action="store_true", help="Use bright foreground instead of dark-line inverse threshold")
    parser.add_argument("--sweep-values", help="Optional comma-separated thresholds to compare on one source frame")
    parser.add_argument("--sweep-output", default="results/03_threshold_sweep.png")
    args = parser.parse_args()

    cap = open_video_source(
        parse_source(args.source),
        backend=args.camera_backend,
        pixel_format=args.camera_format,
        width=args.camera_width,
        height=args.camera_height,
        fps=args.camera_fps,
    )
    print(f"Capture backend ready: {cap.backend_name}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    writer = None
    try:
        if args.sweep_values:
            values = [max(0, min(255, int(value.strip()))) for value in args.sweep_values.split(",") if value.strip()]
            if not values:
                raise ValueError("--sweep-values must contain at least one threshold")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, sweep_frame = cap.read()
            if not ok:
                raise SystemExit("Could not read a frame for the threshold comparison")
            sweep_gray = cv2.cvtColor(sweep_frame, cv2.COLOR_BGR2GRAY)
            sweep_kernel = max(0, min(10, args.blur_radius)) * 2 + 1
            sweep_gray = cv2.GaussianBlur(sweep_gray, (sweep_kernel, sweep_kernel), 0)
            sweep_type = cv2.THRESH_BINARY if args.normal_line else cv2.THRESH_BINARY_INV
            comparison = []
            for value in values:
                _, mask = cv2.threshold(sweep_gray, value, 255, sweep_type)
                comparison.append((f"Threshold {value}", mask))
            write_image(args.sweep_output, make_montage(comparison, columns=min(3, len(comparison))))
            print(f"Threshold comparison saved: {Path(args.sweep_output).resolve()} (values={values})")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        if args.headless:
            threshold = max(0, min(255, args.threshold))
            radius = max(0, min(10, args.blur_radius))
            kernel_size = radius * 2 + 1
            inverse = not args.normal_line
            threshold_type = cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
                _, binary = cv2.threshold(blurred, threshold, 255, threshold_type)
                edges = cv2.Canny(blurred, max(10, threshold // 2), max(30, threshold))
                side_by_side = cv2.hconcat(
                    [frame, cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR), cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)]
                )
                cv2.putText(
                    side_by_side,
                    f"OFFLINE threshold={threshold} inverse={int(inverse)} blur={kernel_size}",
                    (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA,
                )
                if count == 0:
                    write_image(args.snapshot, side_by_side)
                if args.output and writer is None:
                    writer = make_video_writer(args.output, fps, (side_by_side.shape[1], side_by_side.shape[0]))
                if writer:
                    writer.write(side_by_side)
                count += 1
            print(f"Offline frames processed: {count}; threshold={threshold}; inverse={int(inverse)}; blur={kernel_size}")
            print(f"Snapshot saved: {Path(args.snapshot).resolve()}")
            if args.output and writer:
                print(f"Processed video saved: {Path(args.output).resolve()}")
            return

        cv2.namedWindow("Controls", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Binary mask", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Canny edges", cv2.WINDOW_NORMAL)
        cv2.createTrackbar("Threshold", "Controls", 110, 255, _noop)
        cv2.createTrackbar("Dark line (inverse)", "Controls", 1, 1, _noop)
        cv2.createTrackbar("Blur radius", "Controls", 2, 10, _noop)
        snapshot_saved = False

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Video ended or camera frame unavailable.")
                break
            threshold = cv2.getTrackbarPos("Threshold", "Controls")
            inverse = cv2.getTrackbarPos("Dark line (inverse)", "Controls") == 1
            blur_value = cv2.getTrackbarPos("Blur radius", "Controls")
            kernel_size = max(1, blur_value * 2 + 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
            threshold_type = cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY
            _, binary = cv2.threshold(blurred, threshold, 255, threshold_type)
            edges = cv2.Canny(blurred, max(10, threshold // 2), max(30, threshold))
            cv2.imshow("Original", frame)
            cv2.imshow("Binary mask", binary)
            cv2.imshow("Canny edges", edges)
            side_by_side = cv2.hconcat(
                [frame, cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR), cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)]
            )
            cv2.putText(
                side_by_side,
                f"threshold={threshold} inverse={int(inverse)} blur={kernel_size}",
                (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            if args.output and writer is None:
                writer = make_video_writer(
                    args.output,
                    fps,
                    (side_by_side.shape[1], side_by_side.shape[0]),
                )
            if writer:
                writer.write(side_by_side)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("s"):
                write_image(args.snapshot, side_by_side)
                snapshot_saved = True
                print(f"Snapshot saved: {Path(args.snapshot).resolve()}")
            elif key == ord("q") or key == 27:
                break
        if args.output and writer:
            print(f"Processed video saved: {Path(args.output).resolve()}")
        if not snapshot_saved:
            print("Press s during playback to save a tuning screenshot.")
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
