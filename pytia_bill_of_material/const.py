"""
    Constants for the pytia bill of material app.
"""

import os
from enum import Enum
from pathlib import Path

__version__ = "0.6.0"

PYTIA = "pytia"
PYTIA_BILL_OF_MATERIAL = "pytia_bill_of_material"

APP_NAME = "PYTIA Bill Of Material"
APP_VERSION = __version__

LOGON = str(os.environ.get("USERNAME"))
CNEXT = "win_b64\\code\\bin\\CNEXT.exe"
TEMP = str(os.environ.get("TEMP"))
TEMP_EXPORT = Path(TEMP, PYTIA_BILL_OF_MATERIAL, "export")
TEMP_TEMPLATES = Path(TEMP, PYTIA_BILL_OF_MATERIAL, "templates")
APPDATA = Path(str(os.environ.get("APPDATA")), PYTIA, PYTIA_BILL_OF_MATERIAL)
LOGS = f"{APPDATA}\\logs"
LOG = "app.log"
PID = os.getpid()
PID_FILE = f"{TEMP}\\{PYTIA_BILL_OF_MATERIAL}.pid"
VENV = f"\\.env\\{APP_VERSION}"
VENV_PYTHON = Path(VENV, "Scripts\\python.exe")
VENV_PYTHONW = Path(VENV, "Scripts\\pythonw.exe")
PY_VERSION = Path(APPDATA, "pyversion.txt")
EXCEL_EXE = "EXCEL.EXE"
EXPLORER = os.path.join(str(os.getenv("WINDIR")), "explorer.exe")

CONFIG_APPDATA = "config.json"
CONFIG_SETTINGS = "settings.json"
CONFIG_DEPS = "dependencies.json"
CONFIG_KEYWORDS = "keywords.json"
CONFIG_PROPS = "properties.json"
CONFIG_PROPS_DEFAULT = "properties.default.json"
CONFIG_BOM = "bom.json"
CONFIG_BOM_DEFAULT = "bom.default.json"
CONFIG_FILTERS = "filters.json"
CONFIG_FILTERS_DEFAULT = "filters.default.json"
CONFIG_INFOS = "information.json"
CONFIG_INFOS_DEFAULT = "information.default.json"
CONFIG_USERS = "users.json"
CONFIG_DOCKET = "docket.json"
CONFIG_PROPERTIES = "properties.json"

PROP_DRAWING_PATH = "pytia.drawing_path"

TEMPLATE_DOCKET = "docket.CATDrawing"

WEB_PIP = "https://www.pypi.org"

BOM = "bom"
DOCKETS = "dockets"
DRAWINGS = "drawings"
STPS = "steps"
STLS = "stls"

X000D = "_x000D_\n"
KEEP = "Keep"


class Status(Enum):
    OK = "ok"
    FAILED = "failed"
    SKIPPED = "skipped"


os.makedirs(TEMP_EXPORT, exist_ok=True)
os.makedirs(TEMP_TEMPLATES, exist_ok=True)
