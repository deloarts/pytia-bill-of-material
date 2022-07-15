"""
    Constants for the pytia bill of material app.
"""

import os

__version__ = "0.1.0"

PYTIA = "pytia"
PYTIA_BILL_OF_MATERIAL = "pytia_bill_of_material"

APP_NAME = "PYTIA Bill Of Material"
APP_VERSION = __version__

CNEXT = "win_b64\\code\\bin\\CNEXT.exe"
TEMP = str(os.environ.get("TEMP"))
APPDATA = f"{str(os.environ.get('APPDATA'))}\\{PYTIA}\\{PYTIA_BILL_OF_MATERIAL}"
LOGS = f"{APPDATA}\\logs"
LOG = "app.log"
PID = os.getpid()
PID_FILE = f"{TEMP}\\{PYTIA_BILL_OF_MATERIAL}.pid"
VENV = f"\\.env\\{APP_VERSION}"
VENV_PYTHON = VENV + "\\Scripts\\python.exe"
VENV_PYTHONW = VENV + "\\Scripts\\pythonw.exe"
PY_VERSION = APPDATA + "\\pyversion.txt"

CONFIG_APPDATA = "config.json"
CONFIG_SETTINGS = "settings.json"
CONFIG_DEPS = "dependencies.json"

WEB_PIP = "www.pypi.org"
