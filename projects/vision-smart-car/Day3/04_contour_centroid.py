# -*- coding: utf-8 -*-
"""Detect the dark lane contour, calculate its centroid and classify direction."""

import argparse
from pathlib import Path

import cv2

from vision_utils import (
    add_decision_overlay,
    classify_centroid,
    demo_lane_image,
    open_video_source,
    parse_source,
    process_lane_frame,
    read_image,
    write_image,
)


def main():
    parser = argparse.ArgumentParser(description="Run contour and centroid detection on one frame")
    parser.add_argument("--image", help="Input image path")
    parser.add_argument("--source", help="Camera index or video file; optionally select --frame-index")
    parser.add_argument("--camera-backend", choices=("auto", "opencv", "picamera2"), default="auto")
    parser.add_argument("--camera-format", choices=("auto", "mjpg", "yuyv"), default="auto")
    parser.add_argument("--camera-width", type=int, default=640)
    parser.add_argument("--camera-height", type=int, default=480)
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--frame-index", type=int, default=0, help="Frame number to read when --source is a video")
    parser.add_argument("--demo", action="store_true", help="Use a synthetic lane image")
    parser.add_argument("--threshold", type=int, default=110)
    parser.add_argument("--roi-top", type=float, default=0.45, help="Top of ROI as a frame fraction")
    parser.add_argument("--min-area", type=float, default=120)
    parser.add_argument("--invert", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--deadband", type=float, default=0.10, help="Center deadband as half-width fraction")
    parser.add_argument("--output-dir", default="results/04_contour_centroid")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    if args.image and args.source:
        parser.error("Choose only one of --image and --source")
    if args.image:
        frame = read_image(args.image)
        source_label = Path(args.image).name
    elif args.source:
        capture = open_video_source(
            parse_source(args.source),
            backend=args.camera_backend,
            pixel_format=args.camera_format,
            width=args.camera_width,
            height=args.camera_height,
            fps=args.camera_fps,
        )
        if args.frame_index > 0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, args.frame_index)
        ok, frame = capture.read()
        source_backend = capture.backend_name
        capture.release()
        if not ok:
            raise SystemExit(f"Could not read frame {args.frame_index} from: {args.source}")
        source_label = f"{Path(args.source).name} frame {args.frame_index}"
        print(f"Capture backend: {source_backend}")
    elif args.demo:
        frame = demo_lane_image()
        source_label = "synthetic demonstration"
    else:
        parser.error("Provide --image <path> or explicitly request --demo")

    result = process_lane_frame(
        frame,
        threshold=args.threshold,
        roi_top=args.roi_top,
        min_area=args.min_area,
        invert=args.invert,
    )
    centroid = result["centroid"]
    if centroid is None:
        decision = "LOST"
        print("No valid contour / zero-area moment: STOP")
    else:
        decision = classify_centroid(centroid[0], frame.shape[1], args.deadband)
        print(f"Source={source_label}; area={result['area']:.1f}; centroid={centroid}; decision={decision}")

    overlay = add_decision_overlay(result["overlay"], decision)
    output_dir = Path(args.output_dir)
    write_image(output_dir / "centroid_overlay.png", overlay)
    write_image(output_dir / "binary_roi.png", result["binary"])
    if args.show:
        cv2.imshow("Contour and centroid", overlay)
        cv2.imshow("Binary ROI", result["binary"])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print(f"Saved centroid outputs to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
