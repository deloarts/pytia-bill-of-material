"""
    Loads the content from config files.

    Important: Do not import third party modules here. This module
    must work on its own without any other dependencies!
"""

import atexit
import importlib.resources
import json
import os
import re
import tkinter.messagebox as tkmsg
from dataclasses import asdict, dataclass, field, fields
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, List, Literal, Optional, Protocol

from const import (
    APP_VERSION,
    APPDATA,
    CONFIG_APPDATA,
    CONFIG_BOM,
    CONFIG_BOM_DEFAULT,
    CONFIG_DOCKET,
    CONFIG_FILTERS,
    CONFIG_FILTERS_DEFAULT,
    CONFIG_INFOS,
    CONFIG_INFOS_DEFAULT,
    CONFIG_KEYWORDS,
    CONFIG_PROPS,
    CONFIG_PROPS_DEFAULT,
    CONFIG_SETTINGS,
    CONFIG_USERS,
    LOGON,
)
from resources.utils import expand_env_vars


class DataclassProtocol(Protocol):
    __dataclass_fields__: Dict


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsExport:
    """Dataclass for export settings."""

    apply_username_in_bom: bool
    apply_username_in_docket: bool
    lock_drawing_views: bool
    jpg_views: List[List[float]]


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsRestrictions:
    """Dataclass for restrictive settings."""

    allow_all_users: bool
    allow_all_editors: bool
    allow_unsaved: bool
    allow_outside_workspace: bool
    strict_project: bool
    enable_information: bool


@dataclass(slots=True, kw_only=True)
class SettingsPaths:
    """Dataclass for paths (settings.json)."""

    catia: Path
    release: Path

    def __post_init__(self) -> None:
        self.catia = Path(expand_env_vars(str(self.catia)))
        self.release = Path(expand_env_vars(str(self.release)))


@dataclass(slots=True, kw_only=True, frozen=True)
class SettingsFiles:
    """Dataclass for files (settings.json)."""

    bom_export: str
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
    export: SettingsExport
    restrictions: SettingsRestrictions
    files: SettingsFiles
    paths: SettingsPaths
    urls: SettingsUrls
    mails: SettingsMails

    def __post_init__(self) -> None:
        self.export = SettingsExport(**dict(self.export))  # type: ignore
        self.restrictions = SettingsRestrictions(**dict(self.restrictions))  # type: ignore
        self.files = SettingsFiles(**dict(self.files))  # type: ignore
        self.paths = SettingsPaths(**dict(self.paths))  # type: ignore
        self.urls = SettingsUrls(**dict(self.urls))  # type: ignore
        self.mails = SettingsMails(**dict(self.mails))  # type: ignore


@dataclass(slots=True, kw_only=True, frozen=True)
class Props:
    """Dataclass for properties on the part (properties.json)."""

    project: str
    machine: str
    creator: str
    modifier: str

    @property
    def keys(self) -> List[str]:
        """Returns a list of all keys from the Props dataclass."""
        return [f.name for f in fields(self)]

    @property
    def values(self) -> List[str]:
        """Returns a list of all values from the Props dataclass."""
        return [getattr(self, f.name) for f in fields(self)]


@dataclass(slots=True, kw_only=True)
class KeywordElements:
    """Dataclass for keyword elements."""

    partnumber: str
    revision: str
    definition: str
    nomenclature: str
    source: str
    made: str
    bought: str
    description: str
    number: str
    type: str
    part: str
    assembly: str
    quantity: str
    bom: str
    summary: str


@dataclass
class AppliedKeywords(KeywordElements):
    ...


@dataclass(slots=True, kw_only=True)
class Keywords:
    """Dataclass for language specific keywords."""

    en: KeywordElements
    de: KeywordElements

    def __post_init__(self) -> None:
        self.en = KeywordElements(**dict(self.en))  # type: ignore
        self.de = KeywordElements(**dict(self.de))  # type: ignore


@dataclass(slots=True, kw_only=True)
class FilterElement:
    """Filters dataclass."""

    property_name: str
    criteria: str
    condition: Dict[str, str] | bool
    description: str


@dataclass(slots=True, kw_only=True)
class BOMSort:
    """Sort dataclass."""

    made: str
    bought: str


@dataclass(slots=True, kw_only=True)
class RequiredHeaderItems:
    """Required headers dataclass."""

    project: str
    machine: str
    partnumber: str
    revision: str
    quantity: str
    source: str

    @property
    def keys(self) -> List[str]:
        """Returns a list of all keys from the RequiredHeaderItems dataclass."""
        return [f.name for f in fields(self)]

    @property
    def values(self) -> List[str]:
        """Returns a list of all values from the RequiredHeaderItems dataclass."""
        return [getattr(self, f.name) for f in fields(self)]


@dataclass(slots=True, kw_only=True)
class BOMHeaderItems:
    """Header items dataclass."""

    summary: List[str]
    made: List[str] | None
    bought: List[str] | None


@dataclass(slots=True, kw_only=True)
class BOMFiles:
    """Files dataclass."""

    separate: bool
    summary: str
    made: str
    bought: str


@dataclass(slots=True, kw_only=True)
class BOM:
    """Bill of material dataclass."""

    header_row: int | None
    data_row: int
    files: BOMFiles
    header_items: BOMHeaderItems
    sort: BOMSort
    required_header_items: RequiredHeaderItems
    font: str
    size: int
    header_color: str
    header_bg_color: str
    data_color_1: str
    data_bg_color_1: str
    data_color_2: str
    data_bg_color_2: str

    def __post_init__(self) -> None:
        self.files = BOMFiles(**dict(self.files))  # type: ignore
        self.header_items = BOMHeaderItems(**dict(self.header_items))  # type: ignore
        self.sort = BOMSort(**dict(self.sort))  # type: ignore
        self.required_header_items = RequiredHeaderItems(**dict(self.required_header_items))  # type: ignore


@dataclass(slots=True, kw_only=True, frozen=True)
class User:
    """Dataclass a user (users.json)."""

    logon: str
    id: str
    name: str
    mail: str

    @property
    def keys(self) -> List[str]:
        """Returns a list of all keys from the User dataclass."""
        return [f.name for f in fields(self)]

    @property
    def values(self) -> List[str]:
        """Returns a list of all values from the User dataclass."""
        return [getattr(self, f.name) for f in fields(self)]


@dataclass(slots=True, kw_only=True, frozen=True)
class Info:
    """Dataclass for an info messages (information.json)."""

    counter: int
    msg: str


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

    def __init__(self) -> None:
        self._language_applied = False
        self._applied_keywords: AppliedKeywords

        self._read_settings()
        self._read_props()
        self._read_keywords()
        self._read_bom()
        self._read_filters()
        self._read_users()
        self._read_docket()
        self._read_infos()
        self._read_appdata()

        atexit.register(self._write_appdata)

    @property
    def settings(self) -> Settings:
        """settings.json"""
        return self._settings

    @property
    def props(self) -> Props:
        """properties.json"""
        return self._props

    @property
    def keywords(self) -> Keywords:
        """keywords.json"""
        return self._keywords

    @property
    def applied_keywords(self) -> AppliedKeywords:
        """Translated version of the keywords json."""
        if not self._language_applied:
            raise Exception("Language has not been applied to filters.json.")
        return self._applied_keywords

    @property
    def filters(self) -> List[FilterElement]:
        """filters.json"""
        if not self._language_applied:
            raise Exception("Language has not been applied to filters.json.")
        return self._filters

    @property
    def bom(self) -> BOM:
        """bom.json"""
        if not self._language_applied:
            raise Exception("Language has not been applied to filters.json.")
        return self._bom

    @property
    def users(self) -> List[User]:
        """users.json"""
        return self._users

    @property
    def docket(self) -> dict:
        """docket.json"""
        return self._docket

    @property
    def infos(self) -> List[Info]:
        """infos.json"""
        return self._infos

    @property
    def appdata(self) -> AppData:
        """Property for the appdata config file."""
        return self._appdata

    def _read_settings(self) -> None:
        """Reads the settings json from the resources folder."""
        with importlib.resources.open_binary("resources", CONFIG_SETTINGS) as f:
            self._settings = Settings(**json.load(f))

    def _read_props(self) -> None:
        """Reads the props json from the resources folder."""
        props_resource = (
            CONFIG_PROPS
            if importlib.resources.is_resource("resources", CONFIG_PROPS)
            else CONFIG_PROPS_DEFAULT
        )
        with importlib.resources.open_binary("resources", props_resource) as f:
            self._props = Props(**json.load(f))

    def _read_keywords(self) -> None:
        """Reads the keywords json from the resources folder."""
        with importlib.resources.open_binary("resources", CONFIG_KEYWORDS) as f:
            self._keywords = Keywords(**json.load(f))

    def _read_docket(self) -> None:
        """Reads the docket json from the resources folder."""
        with importlib.resources.open_binary("resources", CONFIG_DOCKET) as f:
            self._docket = json.load(f)

    def _read_bom(self) -> None:
        """Reads the export json from the resources folder."""
        bom_resource = (
            CONFIG_BOM
            if importlib.resources.is_resource("resources", CONFIG_BOM)
            else CONFIG_BOM_DEFAULT
        )
        with importlib.resources.open_binary("resources", bom_resource) as f:
            self._bom = BOM(**json.load(f))

    def _read_filters(self) -> None:
        """Reads the filters json from the resources folder."""
        filters_resource = (
            CONFIG_FILTERS
            if importlib.resources.is_resource("resources", CONFIG_FILTERS)
            else CONFIG_FILTERS_DEFAULT
        )
        with importlib.resources.open_binary("resources", filters_resource) as f:
            self._filters = [FilterElement(**i) for i in json.load(f)]

    def _read_users(self) -> None:
        """Reads the users json from the resources folder."""
        with importlib.resources.open_binary("resources", CONFIG_USERS) as f:
            self._users = [User(**i) for i in json.load(f)]

    def _read_infos(self) -> None:
        """Reads the information json from the resources folder."""
        infos_resource = (
            CONFIG_INFOS
            if importlib.resources.is_resource("resources", CONFIG_INFOS)
            else CONFIG_INFOS_DEFAULT
        )
        with importlib.resources.open_binary("resources", infos_resource) as f:
            self._infos = [Info(**i) for i in json.load(f)]

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

    def logon_exists(self, logon: Optional[str] = None) -> bool:
        """
        Returns wether the users logon exists in the dataclass, or not. Uses the logon-value of the
        current session if logon is omitted.

        Args:
            logon (str): The logon name to search for.

        Returns:
            bool: The user from the dataclass list that matches the provided logon name.
        """
        if logon is None:
            logon = LOGON

        for user in self._users:
            if user.logon == logon:
                return True
        return False

    def _apply_keywords_to_bom(self, language: Literal["en", "de"]) -> None:
        """
        Applies the keywords from the keywords.json to the bom.json's `header_items`.

        Detailed explanation:
            The bom.json contains a key named `header_items`, which contains the sub-keys
            `summary`, `made` and `bought`. Those sub-keys contain a list of keywords.
            Those keywords are used to create the header of the bill of material.
            Some of those keywords may represent CATIA standard properties, like `partnumber`,
            `source`, etc. Those names change with the UI language settings of CATIA
            (English: partnumber = "part number", German: partnumber = "Teilenummer", ...).

            It is therefor necessary to overwrite those `header_items` values with the
            corresponding names of the current UI language setting.
            All `header_items` that represent CATIA standard properties must be prefixed with
            a dollar sign `$`. Those names will be translated to the matching name of the
            keywords.json. Names without the dollar sign won't be changed.

            Example (bom.json -> German):
                original: "header_items": ["$number", "$partnumber", "Foo", "Bar"]
                translated: "header_items": ["Nummer", "Teilenummer", "Foo", "Bar"]

            Note: Not only the `header_items` values will be translated, but the `sort` items too.


        Args:
            language (Literal[&quot;en&quot;, &quot;de&quot;]): The language from which the \
                keywords will be applied to the bom.json config file.
        """
        keywords = asdict(self._keywords.en if language == "en" else self._keywords.de)

        def _apply_to_object(_item: DataclassProtocol):
            for object_fields in fields(_item):  # type: ignore
                object_item = getattr(_item, object_fields.name)
                assert isinstance(object_item, list) or isinstance(object_item, str)

                if isinstance(object_item, list):
                    for index, item in enumerate(object_item):
                        assert isinstance(item, str)
                        header_name = item.split(":")[0] + ":" if ":" in item else ""
                        if "$" in item and (key := item.split("$")[1]) in keywords:
                            object_item[index] = header_name + keywords[key]

                elif isinstance(object_item, str):
                    if (
                        "$" in object_item
                        and (key := object_item.split("$")[1]) in keywords
                    ):
                        header_name = (
                            object_item.split(":")[0] + ":"
                            if ":" in object_item
                            else ""
                        )
                        setattr(_item, object_fields.name, header_name + keywords[key])

        _apply_to_object(self._bom.header_items)
        _apply_to_object(self._bom.sort)
        _apply_to_object(self._bom.required_header_items)

    def _apply_keywords_to_filters(self, language: Literal["en", "de"]) -> None:
        """
        Applies the keywords from the keywords.json to the filters.json.

        Detailed explanation:
            The filters.json contains the `property_name` key and `conditions` with key-value pairs.
            Those filter items are used to verify the exported bill of material. A set of rules, if
            you will.
            
            Those property_names and condition-pairs may represent CATIA standard properties, like
            `partnumber`, `source`, ...,  that change their name with the CATIA UI language setting.

            It is therefor necessary to overwrite those names with the corresponding names that
            matches the CATIA language setting. All property_names and condition-pairs that 
            represent CATIA standard properties must be prefixed with a dollar sign `$`. Those
            names property names will be translated to the matching name of the keyword.json.
            Names without a dollar sign won't be translated.

            Example (filters.json -> German):
                original: {"property_name": "$number", "criteria": "^\\d+$", "condition": {"$type": "$part"}}
                translated: {"property_name": "Nummer", "criteria": "^\\d+$", "condition": {"Typ": "Teil"}}

        Args:
            language (Literal[&quot;en&quot;, &quot;de&quot;]): The language from which the \
                keywords will be applied to the filters.json config file.
        """
        keywords = asdict(self._keywords.en if language == "en" else self._keywords.de)
        for item in self._filters:
            # translate the `property_name` value.
            if (
                item.property_name.startswith("$")
                and (key := item.property_name.split("$")[1]) in keywords
            ):
                item.property_name = keywords[key]

            # translate the condition dict (can be a bool, so check type first)
            if isinstance(item.condition, dict):
                new_condition = {}
                for cond_key in item.condition:
                    # translate condition values
                    if (
                        item.condition[cond_key].startswith("$")
                        and (key := item.condition[cond_key].split("$")[1]) in keywords
                    ):
                        item.condition[cond_key] = keywords[key]

                    # translate condition keys
                    # since the keys can be translated as well, we need to create a new dict
                    # and overwrite the existing condition-dict with the new one.
                    if (
                        cond_key.startswith("$")
                        and (key := cond_key.split("$")[1]) in keywords
                    ):
                        new_condition[keywords[key]] = item.condition[cond_key]
                    else:
                        new_condition[cond_key] = item.condition[cond_key]

                item.condition = new_condition

    def apply_language(self, language=Literal["en", "de"]) -> None:
        self._apply_keywords_to_bom(language)  # type: ignore
        self._apply_keywords_to_filters(language)  # type: ignore
        self._applied_keywords = AppliedKeywords(
            **asdict(
                resource._keywords.en if language == "en" else resource._keywords.de
            )
        )
        self._language_applied = True

    def get_info_msg_by_counter(self) -> List[str]:
        """
        Returns the info message by the app usage counter.

        Returns:
            List[str]: A list of all messages that should be shown at the counter value.
        """
        values = []
        for index, value in enumerate(self._infos):
            if value.counter == self._appdata.counter:
                values.append(self._infos[index].msg)
        return values

    def get_user_by_logon(self, logon: str) -> User:
        """
        Returns the user dataclass that matches the logon value.

        Args:
            user (str): The user to fetch from the dataclass list.

        Raises:
            ValueError: Raised when the user doesn't exist.

        Returns:
            User: The user from the dataclass list that matches the provided logon name.
        """
        for index, value in enumerate(self._users):
            if value.logon == logon:
                return self._users[index]
        raise ValueError

    def user_exists(self, logon: str) -> bool:
        """
        Returns wether the user exists in the dataclass list, or not.

        Args:
            logon (str): The logon name to search for.

        Returns:
            bool: The user from the dataclass list that matches the provided logon name.
        """
        for user in self._users:
            if user.logon == logon:
                return True
        return False

    def get_filter_element_by_property_name(self, name: str) -> Optional[FilterElement]:
        """
        Returns the filter dataclass that matches its property name.

        Args:
            name (str): The filter to fetch from the dataclass list by the elements property name.

        Returns:
            User: The filter element from the dataclass list that matches the provided name.
        """
        for index, value in enumerate(self._filters):
            if value.property_name == name:
                return self._filters[index]
        return None


resource = Resources()
