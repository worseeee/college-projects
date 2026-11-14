# -*- coding: utf-8 -*-
"""Compare four filters and binary morphology operations."""

import argparse
from pathlib import Path

import cv2
import numpy as np

from vision_utils import demo_lane_image, make_montage, read_image, resize_longest_side, write_image


def main():
    parser = argparse.ArgumentParser(description="Compare filtering and morphology results")
    parser.add_argument("--image", help="Input image path")
    parser.add_argument("--demo", action="store_true", help="Use a synthetic lane image")
    parser.add_argument("--threshold", type=int, default=110, help="Threshold for dark-line mask")
    parser.add_argument("--kernel", type=int, default=5, help="Odd morphology kernel size")
    parser.add_argument("--max-dimension", type=int, default=1600, help="Downscale large inputs for compact results; 0 keeps original dimensions")
    parser.add_argument("--output-dir", default="results/02_filter_morphology")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    if args.image:
        image = read_image(args.image)
    elif args.demo:
        image = demo_lane_image()
    else:
        parser.error("Provide --image <path> or explicitly request --demo")

    image = resize_longest_side(image, args.max_dimension)

    kernel_size = max(1, args.kernel)
    if kernel_size % 2 == 0:
        kernel_size += 1
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filters = {
        "mean_blur": cv2.blur(image, (5, 5)),
        "gaussian_blur": cv2.GaussianBlur(image, (5, 5), 0),
        "median_blur": cv2.medianBlur(image, 5),
        "bilateral_filter": cv2.bilateralFilter(image, 9, 75, 75),
    }
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(
        cv2.GaussianBlur(gray, (5, 5), 0),
        max(0, min(255, args.threshold)),
        255,
        cv2.THRESH_BINARY_INV,
    )
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    morphology = {
        "binary_dark_foreground": binary,
        "erode": cv2.erode(binary, kernel, iterations=1),
        "dilate": cv2.dilate(binary, kernel, iterations=1),
        "opening": cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel),
        "closing": cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel),
    }

    for name, result in {**filters, **morphology}.items():
        write_image(output_dir / f"{name}.png", result)
    filter_grid = make_montage(
        [("Original", image)] + [(name.replace("_", " "), value) for name, value in filters.items()],
        columns=3,
    )
    morphology_grid = make_montage(
        [(name.replace("_", " "), value) for name, value in morphology.items()],
        columns=3,
    )
    write_image(output_dir / "filter_comparison.png", filter_grid)
    write_image(output_dir / "morphology_comparison.png", morphology_grid)
    if args.show:
        cv2.imshow("Filter comparison", filter_grid)
        cv2.imshow("Morphology comparison", morphology_grid)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print(f"Kernel={kernel_size}x{kernel_size}; threshold={args.threshold}")
    print(f"Saved filter and morphology results to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
