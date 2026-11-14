# -*- coding: utf-8 -*-
"""Day3 subtask 1: image I/O, pixels, ROI, geometry, color and edges."""

import argparse
from pathlib import Path

import cv2
import numpy as np

from vision_utils import demo_lane_image, make_montage, read_image, resize_longest_side, write_image


def main():
    parser = argparse.ArgumentParser(description="Run the Day3 image basics exercise")
    parser.add_argument("--image", help="Input image path")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use a generated synthetic image when no real input is available",
    )
    parser.add_argument(
        "--output-dir", default="results/01_image_basics", help="Result directory"
    )
    parser.add_argument("--max-dimension", type=int, default=1600, help="Downscale large inputs for compact results; 0 keeps original dimensions")
    parser.add_argument("--show", action="store_true", help="Display result windows")
    args = parser.parse_args()

    if args.image:
        image = read_image(args.image)
        source_label = Path(args.image).name
    elif args.demo:
        image = demo_lane_image()
        source_label = "SYNTHETIC DEMO - not camera footage"
    else:
        parser.error("Provide --image <path> or explicitly request --demo")

    original_shape = image.shape
    image = resize_longest_side(image, args.max_dimension)
    height, width = image.shape[:2]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Input: {source_label}")
    print(f"Original BGR shape={original_shape}; working shape={image.shape}, size={image.size}, dtype={image.dtype}, ndim={image.ndim}")

    y, x = min(height - 1, height // 2), min(width - 1, width // 2)
    pixel_bgr = image[y, x].tolist()
    edited = image.copy()
    edited[y, x] = (0, 0, 255)
    print(f"Pixel at (y={y}, x={x}) in BGR order: {pixel_bgr}")

    y1, y2 = height // 4, max(height // 4 + 1, 3 * height // 4)
    x1, x2 = width // 4, max(width // 4 + 1, 3 * width // 4)
    roi = image[y1:y2, x1:x2].copy()
    write_image(output_dir / "roi.png", roi)

    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.line(canvas, (25, 25), (610, 455), (0, 255, 0), 3)
    cv2.rectangle(canvas, (70, 70), (245, 205), (255, 0, 0), 3)
    cv2.circle(canvas, (440, 285), 85, (0, 255, 255), 3)
    cv2.putText(canvas, "OpenCV drawing", (70, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, 45, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
    scaled_15 = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    scaled_05 = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)
    _, simple = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    min_side = min(gray.shape)
    block_size = min(11, min_side if min_side % 2 else min_side - 1)
    if block_size < 3:
        raise ValueError("Image must be at least 3x3 for adaptive thresholding")
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 2
    )
    otsu_value, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    print(f"Gray shape={gray.shape}, ndim={gray.ndim}; HSV shape={hsv.shape}; Otsu threshold={otsu_value:.1f}")

    images = {
        "input": image,
        "pixel_edit": edited,
        "roi": roi,
        "drawings": canvas,
        "rotate_45": rotated,
        "scale_1_5": scaled_15,
        "scale_0_5": scaled_05,
        "gray": gray,
        "hue": hue,
        "saturation": saturation,
        "value": value,
        "threshold_simple": simple,
        "threshold_adaptive": adaptive,
        "threshold_otsu": otsu,
        "canny": edges,
    }
    for name, result in images.items():
        write_image(output_dir / f"{name}.png", result)

    basics = make_montage(
        [
            ("Input - " + source_label[:24], image),
            ("Pixel edit (red BGR)", edited),
            ("ROI crop", roi),
            ("Drawing primitives", canvas),
            ("Rotate 45 degrees", rotated),
            ("Scale x1.5", scaled_15),
            ("Scale x0.5", scaled_05),
            ("Gray", gray),
            ("HSV hue", hue),
            ("HSV saturation", saturation),
            ("HSV value", value),
        ],
        columns=3,
    )
    thresholds = make_montage(
        [("Gray", gray), ("Simple 127", simple), ("Adaptive Gaussian", adaptive), ("Otsu", otsu), ("Canny 50/150", edges)],
        columns=3,
    )
    write_image(output_dir / "image_basics_comparison.png", basics)
    write_image(output_dir / "threshold_canny_comparison.png", thresholds)
    if args.show:
        cv2.imshow("Image basics", basics)
        cv2.imshow("Threshold and Canny", thresholds)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print(f"Saved image basics results to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
