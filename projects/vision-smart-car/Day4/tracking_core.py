# -*- coding: utf-8 -*-
"""Shared perception, target-lock and safe-follow logic for Day4."""

import math

import cv2
import numpy as np


DEFAULT_HSV = (0, 179, 0, 255, 159, 255)


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def scaled_px(reference_pixels, image_width, reference_width=640):
    return max(1, int(round(float(reference_pixels) * image_width / reference_width)))


def normalize_hsv(values=None):
    values = DEFAULT_HSV if values is None else tuple(int(v) for v in values)
    if len(values) != 6:
        raise ValueError("HSV limits must contain six values")
    h_min, h_max, s_min, s_max, v_min, v_max = values
    h_min, h_max = sorted((int(clamp(h_min, 0, 179)), int(clamp(h_max, 0, 179))))
    s_min, s_max = sorted((int(clamp(s_min, 0, 255)), int(clamp(s_max, 0, 255))))
    v_min, v_max = sorted((int(clamp(v_min, 0, 255)), int(clamp(v_max, 0, 255))))
    return h_min, h_max, s_min, s_max, v_min, v_max


def detect_ball(frame, hsv_values=None, hough_param1=120, hough_param2=28):
    """Return a cleaned HSV mask and circular target candidates.

    Hough circles are the primary detector. A circular-contour fallback keeps
    the color target usable when a particular OpenCV build misses a weak edge.
    """
    height, width = frame.shape[:2]
    h_min, h_max, s_min, s_max, v_min, v_max = normalize_hsv(hsv_values)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array((h_min, s_min, v_min), dtype=np.uint8),
        np.array((h_max, s_max, v_max), dtype=np.uint8),
    )
    scale = width / 640.0
    kernel_size = max(3, int(round(5 * scale)))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    blurred = cv2.GaussianBlur(cleaned, (9, 9), 2)

    min_radius = max(5, int(round(10 * scale)))
    min_distance = max(16, int(round(120 * scale)))
    param1 = int(clamp(hough_param1, 20, 300))
    param2 = int(clamp(hough_param2, 8, 150))
    found = []
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min_distance,
        param1=param1,
        param2=param2,
        minRadius=min_radius,
        maxRadius=0,
    )
    if circles is not None:
        for cx, cy, radius in circles[0]:
            radius = float(radius)
            if radius >= min_radius and 0 <= cx < width and 0 <= cy < height:
                found.append({
                    "x": float(cx), "y": float(cy), "metric": radius,
                    "score": math.pi * radius * radius, "shape": "circle",
                })

    contours_result = cv2.findContours(
        cleaned.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = contours_result[0] if len(contours_result) == 2 else contours_result[1]
    min_area = math.pi * min_radius * min_radius * 0.45
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < min_area:
            continue
        perimeter = float(cv2.arcLength(contour, True))
        if perimeter <= 0:
            continue
        circularity = 4.0 * math.pi * area / (perimeter * perimeter)
        x, y, box_w, box_h = cv2.boundingRect(contour)
        aspect = box_w / float(max(1, box_h))
        if circularity < 0.48 or not 0.55 <= aspect <= 1.8:
            continue
        (cx, cy), radius = cv2.minEnclosingCircle(contour)
        if radius < min_radius:
            continue
        candidate = {
            "x": float(cx), "y": float(cy), "metric": float(radius),
            "score": area * max(0.25, min(1.0, circularity)),
            "shape": "circle",
        }
        if not any(math.hypot(candidate["x"] - item["x"], candidate["y"] - item["y"])
                   < max(10.0, min(candidate["metric"], item["metric"]) * 0.55)
                   for item in found):
            found.append(candidate)

    found.sort(key=lambda item: item["score"], reverse=True)
    return cleaned, found


class FaceDetector:
    """Open a supplied Haar cascade and return face-rectangle candidates."""

    def __init__(self, cascade_path, scale_factor=1.1, min_neighbors=4):
        if not hasattr(cv2, "CascadeClassifier"):
            raise RuntimeError(
                "This OpenCV build has no CascadeClassifier API. Install an "
                "OpenCV 4.x build (Day4 requirements pin opencv-python < 5)."
            )
        self.cascade_path = str(cascade_path)
        self.scale_factor = max(1.01, float(scale_factor))
        self.min_neighbors = max(1, int(min_neighbors))
        self.cascade = cv2.CascadeClassifier(self.cascade_path)
        if self.cascade.empty():
            raise RuntimeError(
                "Could not load the Haar cascade at " + self.cascade_path
                + ". Confirm face.xml is the frontal-face cascade and is copied to Day4."
            )

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        height, width = gray.shape[:2]
        min_side = max(30, scaled_px(36, width))
        rectangles = self.cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=(min_side, min_side),
        )
        candidates = []
        for x, y, box_w, box_h in rectangles:
            candidates.append({
                "x": float(x + box_w / 2.0),
                "y": float(y + box_h / 2.0),
                "metric": float(box_w),
                "score": float(box_w * box_h),
                "shape": "face",
                "box": (int(x), int(y), int(box_w), int(box_h)),
            })
        return gray, candidates


class TargetLock:
    """Choose a stable target and smooth its position across frames."""

    def __init__(self, smoothing=0.55):
        self.smoothing = float(clamp(smoothing, 0.05, 1.0))
        self.target = None
        self.stable_frames = 0

    def reset(self):
        self.target = None
        self.stable_frames = 0

    def update(self, candidates, frame_width, frame_height):
        if not candidates:
            self.reset()
            return None

        previous = self.target
        diagonal = math.hypot(frame_width, frame_height)
        max_jump = max(frame_width * 0.35, diagonal * 0.22)
        selected = None
        continuing = False
        if previous is not None:
            compatible = []
            for candidate in candidates:
                distance = math.hypot(
                    candidate["x"] - previous["x"],
                    candidate["y"] - previous["y"],
                )
                if distance <= max_jump:
                    size_ratio = candidate["metric"] / max(1.0, previous["metric"])
                    score = distance / max(1.0, diagonal) - 0.035 * min(size_ratio, 3.0)
                    compatible.append((score, candidate))
            if compatible:
                selected = min(compatible, key=lambda pair: pair[0])[1]
                continuing = True
        if selected is None:
            selected = max(candidates, key=lambda item: item["score"])

        if continuing and previous is not None:
            alpha = self.smoothing
            x = previous["x"] * (1.0 - alpha) + selected["x"] * alpha
            y = previous["y"] * (1.0 - alpha) + selected["y"] * alpha
            metric = previous["metric"] * (1.0 - alpha) + selected["metric"] * alpha
            self.stable_frames += 1
        else:
            x, y, metric = selected["x"], selected["y"], selected["metric"]
            self.stable_frames = 1

        target = dict(selected)
        target.update({
            "x": float(x), "y": float(y), "metric": float(metric),
            "stable_frames": self.stable_frames,
        })
        if target.get("shape") == "face":
            box_w, box_h = selected["box"][2:]
            target["box"] = (
                int(round(x - box_w / 2.0)),
                int(round(y - box_h / 2.0)),
                box_w,
                box_h,
            )
        self.target = target
        return target


class SafetyController:
    """Translate target position/size to safe, differential wheel commands."""

    def __init__(self, ball_stop_radius=50, face_stop_width=150,
                 deadband_pixels=30, turn_gain=1.45):
        self.ball_stop_radius = float(ball_stop_radius)
        self.face_stop_width = float(face_stop_width)
        self.deadband_pixels = float(deadband_pixels)
        self.turn_gain = float(clamp(turn_gain, 0.25, 2.5))
        self.mode = None
        self.near_latched = False

    def reset(self, mode=None):
        self.mode = mode
        self.near_latched = False

    def command(self, mode, target, width, speed, paused=False):
        speed = int(clamp(int(speed), 0, 100))
        if mode != self.mode:
            self.reset(mode)
        if paused:
            return "PAUSED", 0, 0
        if target is None:
            self.near_latched = False
            return "LOST_STOP", 0, 0
        if target.get("stable_frames", 0) < 3:
            self.near_latched = False
            return "ACQUIRE_STOP", 0, 0

        scale = width / 640.0
        if mode == "ball":
            enter = self.ball_stop_radius * scale
        else:
            enter = self.face_stop_width * scale
        release = enter * 0.90
        metric = float(target["metric"])
        if self.near_latched:
            if metric < release:
                self.near_latched = False
        elif metric >= enter:
            self.near_latched = True
        if self.near_latched:
            return "TOO_NEAR_STOP", 0, 0

        if speed == 0:
            return "SPEED_ZERO", 0, 0
        center_x = float(target["x"])
        offset = center_x - width / 2.0
        deadband = self.deadband_pixels * scale
        if abs(offset) <= deadband:
            return "FORWARD", speed, speed

        direction = "LEFT" if offset < 0 else "RIGHT"
        normalized = min(1.0, abs(offset) / max(1.0, width / 2.0))
        deadband_normalized = min(0.8, deadband / max(1.0, width / 2.0))
        strength = (normalized - deadband_normalized) / max(0.05, 1.0 - deadband_normalized)
        turn = min(1.75, max(0.0, strength * self.turn_gain))
        inner = speed * (1.0 - turn)
        outer = speed
        if direction == "LEFT":
            left, right = inner, outer
        else:
            left, right = outer, inner
        return direction, int(round(clamp(left, -speed * 0.75, speed))), int(round(clamp(right, -speed * 0.75, speed)))


def draw_overlay(frame, mode, target, decision, left_pwm, right_pwm,
                 speed, drive_enabled, paused=False, recording=False,
                 source_label=""):
    image = frame.copy()
    height, width = image.shape[:2]
    middle = width // 2
    cv2.line(image, (middle, 0), (middle, height - 1), (255, 180, 0), 1)
    if target is not None:
        x = int(round(target["x"]))
        y = int(round(target["y"]))
        if target.get("shape") == "circle":
            radius = max(3, int(round(target["metric"])))
            cv2.circle(image, (x, y), radius, (0, 255, 0), 2)
            cv2.circle(image, (x, y), 4, (0, 0, 255), -1)
            size_label = "r={:.1f}px".format(target["metric"])
        else:
            box = target.get("box")
            if box:
                bx, by, box_w, box_h = box
                cv2.rectangle(image, (bx, by), (bx + box_w, by + box_h), (255, 0, 0), 2)
            cv2.circle(image, (x, y), 4, (0, 0, 255), -1)
            size_label = "w={:.1f}px".format(target["metric"])
        cv2.putText(image, size_label, (max(8, x + 8), max(22, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.56, (0, 255, 0), 2, cv2.LINE_AA)
        target_line = "target x={} stable={}/3 {}".format(
            x, min(3, target.get("stable_frames", 0)), size_label
        )
    else:
        target_line = "target=NONE"

    panel_h = min(106, height)
    cv2.rectangle(image, (0, 0), (width - 1, panel_h), (18, 25, 35), -1)
    status_color = (80, 220, 110) if decision in ("FORWARD", "LEFT", "RIGHT") else (0, 185, 255)
    cv2.putText(image, "DAY4 {}  {}".format(mode.upper(), "PAUSED" if paused else decision),
                (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.62, status_color, 2, cv2.LINE_AA)
    cv2.putText(image, target_line, (12, 51), cv2.FONT_HERSHEY_SIMPLEX,
                0.50, (235, 240, 245), 1, cv2.LINE_AA)
    drive_label = "GPIO DRIVE" if drive_enabled else "PREVIEW ONLY"
    rec_label = "REC" if recording else "LIVE"
    cv2.putText(image, "{} speed={} PWM L={}/R={}  {} {}".format(
        drive_label, speed, left_pwm, right_pwm, rec_label, source_label
    ), (12, 77), cv2.FONT_HERSHEY_SIMPLEX, 0.47, (235, 240, 245), 1, cv2.LINE_AA)
    cv2.putText(image, "space pause/resume | s screenshot | r record | 1 ball | 2 face | q quit",
                (12, min(height - 8, 100)), cv2.FONT_HERSHEY_SIMPLEX,
                0.40, (210, 220, 230), 1, cv2.LINE_AA)
    return image

