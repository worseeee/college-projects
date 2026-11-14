# -*- coding: utf-8 -*-
"""Combined, key-switchable ball/face visual tracker."""

from tracker_app import main_cli


if __name__ == "__main__":
    raise SystemExit(main_cli(default_mode="ball", fused=True))

