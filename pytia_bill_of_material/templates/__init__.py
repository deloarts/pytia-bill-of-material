"""
    Templates submodule for the app.
    Provides template files from the templates-folder.
"""

import importlib.resources
import os
import zipfile
from pathlib import Path
from typing import Optional

from const import PYTIA_BILL_OF_MATERIAL, TEMP, TEMP_TEMPLATES, TEMPLATE_DOCKET
from resources import resource
from pytia_ui_tools.utils.files import file_utility


class Templates:
    """
    The Templates class.
    """

    def __init__(self) -> None:
        """
        Inits the class. Extracts the templates files from the zipped app and copies them into
        the temp-folder (TEMP\\pytia_bill_of_material\\templates\\). Deletes templates from the
        temp-folder at application exit.

        Warning: If the app mode is set to DEBUG, all templates will be used from the apps
        templates folder, not from the zipped app.
        """
        self.tempfolder = Path(TEMP, PYTIA_BILL_OF_MATERIAL)
        self.temp_docket_path = Path(TEMP_TEMPLATES, TEMPLATE_DOCKET)

        self._docket_path = None

        if not resource.settings.debug:
            self._make_tempfolder()
            self._extract()

        self._get_docket_path()

    def _make_tempfolder(self) -> None:
        """Creates the temp-folder for the templates. Deletes existing templates."""
        if os.path.exists(self.temp_docket_path):
            os.remove(self.temp_docket_path)
        os.makedirs(self.tempfolder, exist_ok=True)

    def _extract(self) -> None:
        """Extracts the templates from the zipped app."""
        try:
            with zipfile.ZipFile(
                Path(resource.settings.paths.release, resource.settings.files.app), "r"
            ) as zfile:
                zfile.extract(
                    member=f"templates/{TEMPLATE_DOCKET}", path=self.tempfolder
                )
            file_utility.add_delete(
                path=self.temp_docket_path, skip_silent=True, at_exit=True
            )
        except:
            pass

    @property
    def docket_path(self) -> Optional[Path]:
        """The path to the docket template file."""
        return self._docket_path

    def _get_docket_path(self) -> None:
        """Returns the path to the docket template. Depends on the apps mode."""
        if resource.settings.debug:
            if importlib.resources.is_resource("templates", TEMPLATE_DOCKET):
                with importlib.resources.path("templates", TEMPLATE_DOCKET) as p:
                    self._docket_path = p
            else:
                self._docket_path = None

        else:
            self._docket_path = (
                self.temp_docket_path if os.path.exists(self.temp_docket_path) else None
            )


templates = Templates()
