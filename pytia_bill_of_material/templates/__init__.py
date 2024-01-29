"""
    Templates submodule for the app.
    Provides template files from the templates-folder.
"""

import importlib.resources
import os
import zipfile
from pathlib import Path
from typing import List
from typing import Optional

from const import PYTIA_BILL_OF_MATERIAL
from const import TEMP
from const import TEMP_TEMPLATES
from const import TEMPLATE_DOCKET
from const import TEMPLATE_DOCUMENTATION
from pytia_ui_tools.utils.files import file_utility
from resources import resource


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

        temp_docket_path = Path(TEMP_TEMPLATES, TEMPLATE_DOCKET)
        temp_docu_path = Path(TEMP_TEMPLATES, TEMPLATE_DOCUMENTATION)

        if not resource.settings.debug:
            self._make_tempfolder(existing_templates=[temp_docket_path, temp_docu_path])
            self._extract(filename=TEMPLATE_DOCKET, temp_path=temp_docket_path)
            self._extract(filename=TEMPLATE_DOCUMENTATION, temp_path=temp_docu_path)

        self._docket_path = self._get_path(
            filename=TEMPLATE_DOCKET, temp_path=temp_docket_path
        )
        self._docu_path = self._get_path(
            filename=TEMPLATE_DOCUMENTATION, temp_path=temp_docu_path
        )

    def _make_tempfolder(self, existing_templates: List[Path]) -> None:
        """Creates the temp-folder for the templates. Deletes existing templates."""
        for temp_template in existing_templates:
            if os.path.exists(temp_template):
                os.remove(temp_template)
        os.makedirs(self.tempfolder, exist_ok=True)

    def _extract(self, filename: str, temp_path: Path) -> None:
        """Extracts the templates from the zipped app."""
        try:
            with zipfile.ZipFile(
                Path(resource.settings.paths.release, resource.settings.files.app), "r"
            ) as zfile:
                zfile.extract(member=f"templates/{filename}", path=self.tempfolder)
            file_utility.add_delete(path=temp_path, skip_silent=True, at_exit=True)
        except:
            pass

    def _get_path(self, filename: str, temp_path: Path) -> Path | None:
        """Returns the path to the CATDrawing template. Depends on the apps mode."""
        if resource.settings.debug:
            if importlib.resources.is_resource("templates", filename):
                with importlib.resources.path("templates", filename) as p:
                    return p
            else:
                return None
        else:
            return temp_path if os.path.exists(temp_path) else None

    @property
    def docket_path(self) -> Optional[Path]:
        """The path to the docket template file."""
        return self._docket_path

    @property
    def documentation_path(self) -> Optional[Path]:
        """The path to the documentation template file."""
        return self._docu_path


templates = Templates()
