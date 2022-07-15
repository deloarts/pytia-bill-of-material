"""
    Loads the content from config files.

    Important: Do not import third party modules here. This module
    must work on its own without any other dependencies!
"""

import atexit
import importlib.resources
import json
import os
import tkinter.messagebox as tkmsg
from dataclasses import asdict, dataclass, field
from json.decoder import JSONDecodeError
from pathlib import Path

from const import APP_VERSION, APPDATA, CONFIG_APPDATA, CONFIG_SETTINGS


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsRestrictions:
    """Dataclass for restrictive settings."""

    allow_all_users: bool
    allow_all_editors: bool
    allow_unsaved: bool
    allow_outside_workspace: bool
    enable_information: bool


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsPaths:
    """Dataclass for paths (settings.json)."""

    catia: Path
    local_dependencies: Path
    release: Path


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsFiles:
    """Dataclass for files (settings.json)."""

    app: str
    launcher: str
    workspace: str


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsUrls:
    """Dataclass for urls (settings.json)."""

    help: str | None


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsMails:
    """Dataclass for mails (settings.json)."""

    admin: str


@dataclass(slots=True, kw_only=True)
class Settings:  # pylint: disable=R0902
    """Dataclass for settings (settings.json)."""

    title: str
    debug: bool
    restrictions: SettingsRestrictions
    files: SettingsFiles
    paths: SettingsPaths
    urls: SettingsUrls
    mails: SettingsMails

    def __post_init__(self) -> None:
        self.restrictions = SettingsRestrictions(**dict(self.restrictions))  # type: ignore
        self.files = SettingsFiles(**dict(self.files))  # type: ignore
        self.paths = SettingsPaths(**dict(self.paths))  # type: ignore
        self.urls = SettingsUrls(**dict(self.urls))  # type: ignore
        self.mails = SettingsMails(**dict(self.mails))  # type: ignore


@dataclass(slots=True, kw_only=True)
class AppData:
    """Dataclass for appdata settings."""

    version: str = field(default=APP_VERSION)
    counter: int = 0
    disable_volume_warning: bool = False

    def __post_init__(self) -> None:
        self.version = (
            APP_VERSION  # Always store the latest version in the appdata json
        )
        self.counter += 1


class Resources:  # pylint: disable=R0902
    """Class for handling resource files."""

    __slots__ = (
        "_settings",
        "_appdata",
    )

    def __init__(self) -> None:
        self._read_settings()
        self._read_appdata()

        atexit.register(self._write_appdata)

    @property
    def settings(self) -> Settings:
        """settings.json"""
        return self._settings

    @property
    def appdata(self) -> AppData:
        """Property for the appdata config file."""
        return self._appdata

    def _read_settings(self) -> None:
        """Reads the settings json from the resources folder."""
        with importlib.resources.open_binary("resources", CONFIG_SETTINGS) as f:
            self._settings = Settings(**json.load(f))

    def _read_appdata(self) -> None:
        """Reads the json config file from the appdata folder."""
        if os.path.exists(appdata_file := f"{APPDATA}\\{CONFIG_APPDATA}"):
            with open(appdata_file, "r", encoding="utf8") as f:
                try:
                    value = AppData(**json.load(f))
                except JSONDecodeError:
                    value = AppData()
                    tkmsg.showwarning(
                        title="Configuration warning",
                        message="The AppData config file has been corrupted. \
                            You may need to apply your preferences again.",
                    )
                self._appdata = value
        else:
            self._appdata = AppData()

    def _write_appdata(self) -> None:
        """Saves appdata config to file."""
        os.makedirs(APPDATA, exist_ok=True)
        with open(f"{APPDATA}\\{CONFIG_APPDATA}", "w", encoding="utf8") as f:
            json.dump(asdict(self._appdata), f)


resource = Resources()
