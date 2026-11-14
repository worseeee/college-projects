# -*- coding: utf-8 -*-
"""Create clearly labeled offline ball-detection outputs from supplied assets."""

import argparse
from pathlib import Path

import cv2
import numpy as np

from tracking_core import DEFAULT_HSV, SafetyController, TargetLock, detect_ball, draw_overlay
from vision_utils import make_video_writer, open_video_source, write_image


BASE_DIR = Path(__file__).resolve().parent


def process_image(path, output_dir, args):
    frame = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError("Could not read image: {}".format(path))
    height, width = frame.shape[:2]
    mask, candidates = detect_ball(frame, DEFAULT_HSV, args.hough_param1, args.hough_param2)
    lock = TargetLock()
    target = lock.update(candidates, width, height)
    safety = SafetyController()
    decision, left, right = safety.command("ball", target, width, args.speed)
    overlay = draw_overlay(frame, "ball", target, decision, left, right,
                           args.speed, drive_enabled=False, source_label="still image")
    cv2.putText(overlay, "OFFLINE SAMPLE - NO GPIO", (12, height - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 170, 255), 2, cv2.LINE_AA)
    mask_view = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    cv2.putText(mask_view, "HSV mask: H12-37 S96-255 V186-255", (12, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
    image_output = output_dir / "ball_detection_annotated.png"
    mask_output = output_dir / "ball_detection_mask.png"
    write_image(image_output, overlay)
    write_image(mask_output, mask_view)
    print("Image output: {}".format(image_output))
    print("Mask output: {}".format(mask_output))
    print("Image candidates: {}".format(len(candidates)))


def process_video(path, output_dir, args):
    capture = open_video_source(str(path), backend="opencv")
    writer = None
    lock = TargetLock()
    safety = SafetyController()
    frame_number = 0
    saved_still = False
    video_output = output_dir / "ball_tracking_annotated.mp4"
    still_output = output_dir / "ball_tracking_frame.png"
    try:
        fps = capture.get(cv2.CAP_PROP_FPS) or 20.0
        ok, first_frame = capture.read()
        if not ok or first_frame is None:
            raise RuntimeError("Could not read first video frame: {}".format(path))
        height, width = first_frame.shape[:2]
        writer = make_video_writer(video_output, fps, (width, height))
        frame = first_frame
        while True:
            frame_number += 1
            height, width = frame.shape[:2]
            mask, candidates = detect_ball(frame, DEFAULT_HSV, args.hough_param1, args.hough_param2)
            target = lock.update(candidates, width, height)
            decision, left, right = safety.command("ball", target, width, args.speed)
            overlay = draw_overlay(frame, "ball", target, decision, left, right,
                                   args.speed, drive_enabled=False, source_label="supplied video")
            cv2.putText(overlay, "OFFLINE VIDEO - NO GPIO", (12, height - 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 170, 255), 2, cv2.LINE_AA)
            writer.write(overlay)
            if not saved_still and target is not None and target.get("stable_frames", 0) >= 3:
                write_image(still_output, overlay)
                saved_still = True
            if frame_number % 100 == 0:
                print("Processed {} frames; latest decision={}".format(frame_number, decision))
            ok, frame = capture.read()
            if not ok or frame is None:
                break
    finally:
        if writer is not None:
            writer.release()
        capture.release()
    print("Video output: {} ({} frames)".format(video_output, frame_number))
    if saved_still:
        print("Tracking still: {}".format(still_output))
    else:
        print("No stable target found in supplied video; no tracking still was created.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default=str(BASE_DIR / "ball_detection.jpg"))
    parser.add_argument("--video", default=str(BASE_DIR / "ball_tracking.mp4"))
    parser.add_argument("--output-dir", default=str(BASE_DIR / "results"))
    parser.add_argument("--speed", type=int, default=35)
    parser.add_argument("--hough-param1", type=int, default=120)
    parser.add_argument("--hough-param2", type=int, default=28)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = Path(args.image)
    video_path = Path(args.video)
    if image_path.exists():
        process_image(image_path, output_dir, args)
    else:
        print("Image asset not found, skipped: {}".format(image_path))
    if video_path.exists():
        process_video(video_path, output_dir, args)
    else:
        print("Video asset not found, skipped: {}".format(video_path))


if __name__ == "__main__":
    main()

