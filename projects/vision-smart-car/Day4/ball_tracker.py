# -*- coding: utf-8 -*-
"""Standalone HSV/Hough ping-pong ball tracker."""

from tracker_app import main_cli


if __name__ == "__main__":
    raise SystemExit(main_cli(default_mode="ball", fused=False))

