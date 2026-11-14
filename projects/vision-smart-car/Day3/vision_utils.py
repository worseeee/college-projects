# -*- coding: utf-8 -*-
"""Shared image/video helpers for the Day3 OpenCV exercises."""

from pathlib import Path
import sys

import cv2
import numpy as np


def read_image(path):
    """Read an image path, including paths containing non-ASCII characters."""
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to decode image: {path}")
    return image


def write_image(path, image):
    """Write an image path, including paths containing non-ASCII characters."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix or ".png"
    ok, encoded = cv2.imencode(suffix, image)
    if not ok:
        raise OSError(f"Unable to encode image as {suffix}")
    encoded.tofile(str(path))
    return path


def find_contours(binary, mode=None, method=None):
    """Return contours across OpenCV 3.x and 4.x Python signatures."""
    mode = cv2.RETR_EXTERNAL if mode is None else mode
    method = cv2.CHAIN_APPROX_SIMPLE if method is None else method
    result = cv2.findContours(binary.copy(), mode, method)
    return result[0] if len(result) == 2 else result[1]


def parse_source(value):
    """Interpret an integer-like source as a camera index, otherwise a path."""
    text = str(value)
    return int(text) if text.isdigit() else text


class BufferedCapture:
    """Capture adapter that preserves the first frame used during camera probing."""

    def __init__(self, capture, first_frame, backend_name, picamera2=False, fps=30.0):
        self.capture = capture
        self.first_frame = first_frame
        self.backend_name = backend_name
        self.picamera2 = picamera2
        self.fps = float(fps)
        self.released = False

    def read(self):
        if self.released:
            return False, None
        if self.first_frame is not None:
            frame = self.first_frame
            self.first_frame = None
            return True, frame
        if self.picamera2:
            try:
                frame = self.capture.capture_array("main")
            except Exception:
                return False, None
            return frame is not None, frame
        return self.capture.read()

    def get(self, prop):
        if prop == cv2.CAP_PROP_FPS and self.picamera2:
            return self.fps
        return self.capture.get(prop)

    def set(self, prop, value):
        # Seeking discards a probed frame, which is important for video sweeps.
        self.first_frame = None
        if self.picamera2:
            return False
        return self.capture.set(prop, value)

    def release(self):
        if self.released:
            return
        self.released = True
        if self.picamera2:
            try:
                self.capture.stop()
            finally:
                self.capture.close()
        else:
            self.capture.release()


def _ensure_bgr(frame):
    if frame is None:
        return None
    if frame.ndim == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    if frame.ndim == 3 and frame.shape[2] == 4:
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    if frame.ndim == 3 and frame.shape[2] == 3:
        return frame
    return None


def _open_opencv_camera(index, width, height, fps, pixel_format):
    """Try common V4L2 formats, then OpenCV's default camera backend."""
    candidates = []
    v4l2 = getattr(cv2, "CAP_V4L2", None) if sys.platform.startswith("linux") else None
    formats = [pixel_format] if pixel_format != "auto" else ["MJPG", "YUYV"]
    resolutions = [(width, height)]
    if (width, height) != (320, 240):
        resolutions.append((320, 240))

    if v4l2 is not None:
        for fmt in formats:
            for size in resolutions:
                candidates.append((v4l2, fmt, size))
        candidates.append((v4l2, None, (width, height)))
    candidates.append((getattr(cv2, "CAP_ANY", 0), None, (width, height)))

    failures = []
    tried = set()
    for backend, fmt, size in candidates:
        key = (backend, fmt, size)
        if key in tried:
            continue
        tried.add(key)
        legacy_api_fallback = False
        try:
            if backend == getattr(cv2, "CAP_ANY", 0):
                capture = cv2.VideoCapture(index)
            else:
                try:
                    capture = cv2.VideoCapture(index, backend)
                except TypeError:
                    # Some Raspberry Pi OpenCV builds expose only VideoCapture(index).
                    capture = cv2.VideoCapture(index)
                    legacy_api_fallback = True
        except Exception as exc:
            failures.append(
                f"backend={backend}, format={fmt or 'default'}, open error: {exc}"
            )
            continue
        if not capture.isOpened():
            capture.release()
            failures.append(f"backend={backend}, format={fmt or 'default'}, open failed")
            continue

        if fmt:
            code = cv2.VideoWriter_fourcc(*fmt)
            capture.set(cv2.CAP_PROP_FOURCC, code)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
        if fps > 0:
            capture.set(cv2.CAP_PROP_FPS, fps)
        if hasattr(cv2, "CAP_PROP_BUFFERSIZE"):
            capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        ok, frame = capture.read()
        frame = _ensure_bgr(frame) if ok else None
        if frame is not None:
            if legacy_api_fallback:
                backend_name = f"OpenCV/default legacy API {size[0]}x{size[1]}"
            else:
                backend_name = f"OpenCV/V4L2 {fmt or 'native'} {size[0]}x{size[1]}"
            return BufferedCapture(capture, frame, backend_name), failures
        capture.release()
        failures.append(f"backend={backend}, format={fmt or 'default'}, no decodable frame")

    return None, failures


def _open_picamera2(index, width, height, fps):
    """Open a CSI camera through Raspberry Pi's libcamera-based Picamera2 API."""
    try:
        from picamera2 import Picamera2
    except ImportError as exc:
        raise RuntimeError("Picamera2 is not installed in this Python interpreter") from exc

    camera = Picamera2(camera_num=int(index))
    try:
        # Picamera2's RGB888 byte layout is [B, G, R], as OpenCV expects.
        configuration = camera.create_video_configuration(
            main={"size": (int(width), int(height)), "format": "RGB888"}
        )
        camera.configure(configuration)
        camera.start()
        frame = _ensure_bgr(camera.capture_array("main"))
        if frame is None:
            raise RuntimeError("Picamera2 returned an unsupported frame shape")
        return BufferedCapture(camera, frame, "Picamera2/libcamera", picamera2=True, fps=fps)
    except Exception:
        try:
            camera.stop()
        except Exception:
            pass
        camera.close()
        raise


def open_video_source(source, backend="auto", width=640, height=480, fps=30,
                      pixel_format="auto"):
    """Open a file or camera and verify that at least one usable frame is available.

    For Raspberry Pi camera index sources, ``backend='auto'`` tries V4L2/OpenCV
    first, then Picamera2 for CSI cameras. Camera index sources are probed before
    the caller initializes GPIO, so camera startup failures cannot leave motors on.
    """
    if backend not in ("auto", "opencv", "picamera2"):
        raise ValueError("backend must be auto, opencv, or picamera2")
    if pixel_format not in ("auto", "mjpg", "yuyv"):
        raise ValueError("pixel_format must be auto, mjpg, or yuyv")
    width = max(1, int(width))
    height = max(1, int(height))
    fps = max(1, int(fps))

    if not isinstance(source, int):
        if backend == "picamera2":
            raise ValueError("Picamera2 backend requires a numeric camera index")
        capture = cv2.VideoCapture(source)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Could not open video file: {source}")
        ok, frame = capture.read()
        frame = _ensure_bgr(frame) if ok else None
        if frame is None:
            capture.release()
            raise RuntimeError(f"Video file opened but produced no usable frame: {source}")
        source_fps = capture.get(cv2.CAP_PROP_FPS) or fps
        return BufferedCapture(capture, frame, "OpenCV/video", fps=source_fps)

    if backend == "picamera2":
        return _open_picamera2(source, width, height, fps)

    selected_format = pixel_format.upper()
    if selected_format == "AUTO":
        selected_format = "auto"
    capture, failures = _open_opencv_camera(
        source, width, height, fps, selected_format
    )
    if capture is not None:
        return capture
    if backend == "opencv":
        detail = "; ".join(failures)
        busy_hint = (
            f" Close other camera apps and check `fuser -v /dev/video{source}`."
            if sys.platform.startswith("linux") else ""
        )
        raise RuntimeError(
            f"OpenCV could not read camera index {source} ({detail}). "
            "The camera may be busy or using an unsupported pixel format."
            f"{busy_hint}"
        )

    if sys.platform.startswith("linux"):
        try:
            return _open_picamera2(source, width, height, fps)
        except Exception as exc:
            raise RuntimeError(
                f"No usable camera frame from index {source}. OpenCV attempts: "
                f"{'; '.join(failures)}. Picamera2 attempt: {exc}. "
                "Close other camera apps first. For a CSI camera use Picamera2; "
                "for a USB camera try --camera-backend opencv --camera-format mjpg "
                f"or yuyv. On Linux check `fuser -v /dev/video{source}`."
            ) from exc

    raise RuntimeError(
        f"OpenCV could not read camera index {source} ({'; '.join(failures)}). "
        "Check that the camera is connected and not open in another application."
    )


def demo_lane_image(width=640, height=480):
    """Create a clearly synthetic dark-line frame for software-only exercises."""
    image = np.full((height, width, 3), 232, dtype=np.uint8)
    points = np.array(
        [
            [int(width * 0.57), height - 1],
            [int(width * 0.55), int(height * 0.78)],
            [int(width * 0.50), int(height * 0.58)],
            [int(width * 0.43), int(height * 0.36)],
            [int(width * 0.39), int(height * 0.15)],
            [int(width * 0.40), 0],
        ],
        dtype=np.int32,
    )
    cv2.polylines(image, [points], False, (24, 24, 24), max(18, width // 24))
    cv2.rectangle(image, (35, 60), (110, 120), (180, 180, 180), -1)
    cv2.circle(image, (int(width * 0.78), int(height * 0.32)), 23, (55, 55, 55), -1)
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 2.0, image.shape).astype(np.int16)
    return np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def resize_longest_side(image, max_dimension=1600):
    """Downscale very large photographs while preserving their aspect ratio."""
    max_dimension = max(0, int(max_dimension))
    height, width = image.shape[:2]
    longest = max(height, width)
    if max_dimension == 0 or longest <= max_dimension:
        return image
    scale = max_dimension / float(longest)
    return cv2.resize(
        image,
        (max(1, int(round(width * scale))), max(1, int(round(height * scale)))),
        interpolation=cv2.INTER_AREA,
    )


def make_montage(items, columns=3, tile_size=(360, 240)):
    """Return a labeled image grid. Labels use ASCII for OpenCV font support."""
    if not items:
        raise ValueError("At least one image is required for a montage")
    tile_w, tile_h = tile_size
    rows = (len(items) + columns - 1) // columns
    canvas = np.full((rows * tile_h, columns * tile_w, 3), 248, dtype=np.uint8)
    for index, (label, source) in enumerate(items):
        if source.ndim == 2:
            source = cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
        image_h, image_w = source.shape[:2]
        scale = min((tile_w - 12) / image_w, (tile_h - 36) / image_h)
        resized = cv2.resize(
            source,
            (max(1, int(image_w * scale)), max(1, int(image_h * scale))),
            interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR,
        )
        row, col = divmod(index, columns)
        x0, y0 = col * tile_w, row * tile_h
        cv2.putText(
            canvas,
            str(label)[:42],
            (x0 + 8, y0 + 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (30, 47, 68),
            1,
            cv2.LINE_AA,
        )
        y = y0 + 30 + (tile_h - 34 - resized.shape[0]) // 2
        x = x0 + (tile_w - resized.shape[1]) // 2
        canvas[y : y + resized.shape[0], x : x + resized.shape[1]] = resized
    return canvas


def make_video_writer(path, fps, frame_size):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fps = float(fps) if fps and fps > 1 else 20.0
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, frame_size
    )
    if not writer.isOpened():
        raise OSError(f"Unable to open video writer: {path}")
    return writer


def process_lane_frame(
    frame,
    threshold=110,
    roi_top=0.30,
    min_area=120,
    invert=True,
    kernel_size=3,
    threshold_mode="fixed",
    near_row=0.82,
    lookahead_row=0.62,
    near_reference_x=None,
    lookahead_reference_x=None,
):
    """Find a dark track and sample its near and lookahead positions.

    Returns an overlay, binary ROI, centroid in full-frame coordinates,
    near/lookahead points, contour area, and the ROI's vertical offset.
    """
    height, width = frame.shape[:2]
    roi_top = min(0.9, max(0.0, float(roi_top)))
    y0 = min(height - 1, max(0, int(height * roi_top)))
    roi = frame[y0:, :]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    threshold_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    threshold_mode = str(threshold_mode).lower()
    if threshold_mode == "fixed":
        _, binary = cv2.threshold(
            blurred, int(threshold), 255, threshold_type
        )
    elif threshold_mode == "otsu":
        _, binary = cv2.threshold(
            blurred, 0, 255, threshold_type | cv2.THRESH_OTSU
        )
    else:
        raise ValueError("threshold_mode must be 'fixed' or 'otsu'")
    kernel_size = max(1, int(kernel_size))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, y0), (width - 1, height - 1), (255, 180, 0), 1)
    contours = find_contours(binary)
    contours = [c for c in contours if cv2.contourArea(c) >= float(min_area)]
    if not contours:
        cv2.putText(
            overlay,
            "LINE LOST - STOP",
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
        return {
            "overlay": overlay,
            "binary": binary,
            "centroid": None,
            "near_point": None,
            "lookahead_point": None,
            "area": 0.0,
            "roi_y": y0,
        }

    # Prefer the previous track neighborhood when contours compete. This
    # reduces jumps to floor marks or another dark region at a junction.
    reference_x = near_reference_x
    if reference_x is None:
        contour = max(contours, key=cv2.contourArea)
    else:
        def contour_score(candidate):
            area = max(1.0, float(cv2.contourArea(candidate)))
            x, _y, box_width, _height = cv2.boundingRect(candidate)
            right = x + box_width - 1
            distance = max(float(x) - float(reference_x), 0.0,
                           float(reference_x) - float(right))
            return np.log1p(area) - 4.5 * distance / max(1.0, float(width))

        contour = max(contours, key=contour_score)
    moments = cv2.moments(contour)
    area = float(cv2.contourArea(contour))
    if abs(moments["m00"]) < 1e-9:
        centroid = None
        near_point = None
        lookahead_point = None
    else:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"]) + y0
        centroid = (cx, cy)
        contour_full = contour + np.array([[[0, y0]]], dtype=contour.dtype)
        cv2.drawContours(overlay, [contour_full], -1, (0, 200, 0), 2)
        cv2.circle(overlay, centroid, 6, (0, 0, 255), -1)

        # Limit row scans to the selected connected track. Scanning the full
        # threshold mask can otherwise jump to shadows or unrelated marks.
        track_mask = np.zeros_like(binary)
        cv2.drawContours(track_mask, [contour], -1, 255, thickness=cv2.FILLED)

        # Temporal references keep nearby dark marks from stealing the
        # target between frames.
        def sample_track_row(row_fraction, reference_x=None):
            row_fraction = max(0.0, min(1.0, float(row_fraction)))
            target_y = int(round(height * row_fraction))
            if target_y < y0 or target_y >= height:
                return None
            local_y = target_y - y0
            radius = max(2, int(round(height * 0.015)))
            y1 = max(0, local_y - radius)
            y2 = min(binary.shape[0], local_y + radius + 1)
            band = track_mask[y1:y2, :]
            if band.size == 0:
                return None
            counts = np.count_nonzero(band, axis=0)
            required = max(1, int(round((y2 - y1) * 0.18)))
            active = np.flatnonzero(counts >= required)
            if active.size == 0:
                return None
            runs = np.split(active, np.flatnonzero(np.diff(active) > 1) + 1)

            def run_score(values):
                center_x = (int(values[0]) + int(values[-1])) / 2.0
                run_width = int(values[-1]) - int(values[0]) + 1
                support = float(np.sum(counts[values[0] : values[-1] + 1]))
                width_fraction = run_width / max(1.0, float(width))
                score = float(np.log1p(support))
                score -= max(0.0, width_fraction - 0.18) * 5.0
                if reference_x is not None:
                    score -= abs(center_x - float(reference_x)) / max(1.0, width) * 3.0
                return score

            run = max(runs, key=run_score)
            return int(round((int(run[0]) + int(run[-1])) / 2.0)), target_y

        near_point = sample_track_row(near_row, near_reference_x)
        lookahead_reference = (
            lookahead_reference_x
            if lookahead_reference_x is not None
            else near_reference_x
        )
        lookahead_point = sample_track_row(lookahead_row, lookahead_reference)
        if near_point is not None:
            cv2.circle(overlay, near_point, 6, (255, 0, 255), -1)
            cv2.putText(
                overlay, "STEER", (near_point[0] + 8, near_point[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 0, 255), 1, cv2.LINE_AA,
            )
        if lookahead_point is not None:
            cv2.circle(overlay, lookahead_point, 6, (255, 255, 0), -1)
            cv2.putText(
                overlay, "AIM", (lookahead_point[0] + 8, lookahead_point[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 0), 1, cv2.LINE_AA,
            )
        cv2.putText(
            overlay,
            f"cx={cx} cy={cy} area={area:.0f}",
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (30, 60, 210),
            2,
            cv2.LINE_AA,
        )
    return {
        "overlay": overlay,
        "binary": binary,
        "centroid": centroid,
        "near_point": near_point,
        "lookahead_point": lookahead_point,
        "area": area,
        "roi_y": y0,
    }


def classify_centroid(cx, width, deadband=0.10):
    """Map normalized centroid position to the taskbook's three directions."""
    if width <= 0:
        raise ValueError("width must be positive")
    normalized_error = (float(cx) - width / 2.0) / (width / 2.0)
    deadband = max(0.0, min(0.8, float(deadband)))
    if normalized_error < -deadband:
        return "LEFT"
    if normalized_error > deadband:
        return "RIGHT"
    return "STRAIGHT"


def add_decision_overlay(image, decision):
    colors = {
        "LEFT": (255, 120, 0),
        "RIGHT": (255, 120, 0),
        "STRAIGHT": (0, 160, 0),
        "LOST": (0, 0, 255),
    }
    cv2.putText(
        image,
        f"Decision: {decision}",
        (12, 58),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.68,
        colors.get(decision, (30, 47, 68)),
        2,
        cv2.LINE_AA,
    )
    return image
