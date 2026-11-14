# -*- coding: utf-8 -*-
"""Standalone Haar-cascade face tracker."""

from tracker_app import main_cli


if __name__ == "__main__":
    raise SystemExit(main_cli(default_mode="face", fused=False))

