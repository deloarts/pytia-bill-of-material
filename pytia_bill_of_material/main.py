#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Main module for the app.
"""

import atexit
import os

from const import APP_VERSION, LOG, LOGS, PID, PID_FILE
from dependencies import deps
from resources import resource


def main() -> None:
    """Application entry point."""

    # For the apps auto-install-feature, all required dependencies must be
    # imported after they have been checked.
    # So: First check if all required dependencies are installed.
    # Afterwards import those modules which depend on third party modules.
    deps.install_dependencies()

    from pytia.log import log  # pylint: disable=C0415

    from app.main_ui import MainUI  # pylint: disable=C0415

    with open(PID_FILE, "w") as f:
        f.write(str(PID))
    atexit.register(lambda: os.remove(PID_FILE))

    os.makedirs(LOGS, exist_ok=True)
    if resource.settings.debug:
        log.set_level_debug()
    log.add_stream_handler()
    log.add_file_handler(folder=LOGS, filename=LOG)
    log.info(f"Running PYTIA Bounding Box {APP_VERSION}, PID={PID}")

    gui = MainUI()
    gui.run()


if __name__ == "__main__":
    main()
