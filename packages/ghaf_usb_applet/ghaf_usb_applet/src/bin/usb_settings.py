# Copyright 2022-2025 TII (SSRC) and the Ghaf contributors
# SPDX-License-Identifier: Apache-2.0

import argparse

from ghaf_usb_applet.settings import SettingsMenu
from ghaf_usb_applet.logger import setup_logger

def build_parser():
    p = argparse.ArgumentParser(description="USB Device Settings")
    p.add_argument(
        "--port", type=int, default=2000, help="Host vsock listen port (default 7000)"
    )
    p.add_argument("--loglevel", type=str, default="info", help="Log level")
    return p.parse_args()

def main():
    args = build_parser()
    setup_logger(args.loglevel)
    app = SettingsMenu(args.port)
    raise SystemExit(app.run())

if __name__ == "__main__":
    main()

