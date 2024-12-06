import os

import toml

from pytia_bill_of_material.const import APP_VERSION

VERSION = "0.13.2"

directory = os.path.dirname(os.path.realpath("__file__"))
with open(os.path.join(directory, "pyproject.toml"), "r") as f:
    pyproject = dict(toml.load(f)["tool"]["poetry"])


def test_version():
    assert APP_VERSION == VERSION
    assert pyproject["version"] == VERSION
