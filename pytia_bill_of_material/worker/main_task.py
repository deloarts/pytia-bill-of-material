"""
    Submodule for the main task: Exporting data.
    
    TODO: Split up the main task. This class and its functions have too many responsibilities.

    TODO: Create a class for handling the main tasks' files (temp excel files, png files, etc.).

    TODO: Proper documentation.
"""

from pathlib import Path
from tkinter import Tk
from tkinter import messagebox as tkmsg
from typing import Callable

from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import Status
from helper.lazy_loaders import LazyDocumentHelper
from models.bom import BOM
from models.paths import Paths
from pytia.utilities.docket import DocketConfig
from resources import resource
from utils.files import file_utility
from utils.system import explorer

from .catia_export import CatiaExportTask
from .export_items import ExportItemsTask
from .make_report import MakeReportTask
from .prepare import PrepareTask
from .process_bom import ProcessBomTask
from .save_bom import SaveBomTask


class MainTask:
    def __init__(
        self,
        main_ui: Tk,
        layout: Layout,
        ui_setter: UISetter,
        doc_helper: LazyDocumentHelper,
        variables: Variables,
    ):
        self.main_ui = main_ui
        self.layout = layout
        self.ui_setter = ui_setter
        self.doc_helper = doc_helper
        self.variables = variables

        self._abort = False
        self._project = variables.project.get()
        self._status = Status.SKIPPED
        self._xlsx: Path
        self._paths: Paths
        self._docket_config: DocketConfig
        self._bom: BOM

        self.variables.progress.set(0)
        self.layout.progress_bar.grid()

    def run(self) -> None:
        self._run_task(self._prepare)
        self._run_task(self._catia_export)
        self._run_task(self._process_bom)
        self._run_task(self._create_report)
        self.variables.progress.set(100)

        if self._status == Status.OK:
            self._save_bom()
            self._export_items()
            self._move_files()

            if file_utility.all_moved:
                if tkmsg.askyesno(
                    title=resource.settings.title,
                    message=(
                        "Successfully exported the bill of material.\n\n"
                        "Do you want to open the export folder?"
                    ),
                ):
                    explorer(Path(self.variables.bom_export_path.get()))
            else:
                tkmsg.showwarning(
                    title=resource.settings.title,
                    message=(
                        "Finished the export, but not all files have been moved to their target "
                        "folder.\n\nMaybe you have skipped some files?"
                    ),
                )

        elif self._status == Status.FAILED:
            self.variables.show_report.set(
                tkmsg.askyesno(
                    title=resource.settings.title,
                    message=(
                        "There are errors in the bill of material.\n\n"
                        "Do you want to open the report?"
                    ),
                    icon="warning",
                )
            )

        self.layout.progress_bar.grid_remove()
        self.ui_setter.normal()

    def _run_task(self, task: Callable) -> None:
        if not self._abort:
            task()
            self.variables.progress.set(self.variables.progress.get() + int(100 / 4))
            self.main_ui.update_idletasks()

    def _prepare(self) -> None:
        task = PrepareTask(doc_helper=self.doc_helper)
        task.run()

        self._paths = task.paths
        self._docket_config = task.docket_config

    def _catia_export(self) -> None:
        task = CatiaExportTask(doc_helper=self.doc_helper)
        task.run()

        self._xlsx = task.xlsx

    def _process_bom(self) -> None:
        task = ProcessBomTask(
            xlsx=self._xlsx, project_number=self._project, paths=self._paths
        )
        task.run()

        self._bom = task.bom

    def _create_report(self) -> None:
        task = MakeReportTask(bom=self._bom)
        task.run()

        self._status = task.status
        self.variables.report = task.report

    def _save_bom(self) -> None:
        task = SaveBomTask(
            bom=self._bom, path=Path(self.variables.bom_export_path.get())
        )
        task.run()

    def _export_items(self) -> None:
        task = ExportItemsTask(
            root=self.main_ui,
            progress_callback=self.variables.progress,
            bom=self._bom,
            export_docket=self.variables.export_docket.get(),
            export_stp=self.variables.export_stp.get(),
            export_stl=self.variables.export_stl.get(),
            docket_path=Path(self.variables.docket_export_path.get()),
            stp_path=Path(self.variables.stp_export_path.get()),
            stl_path=Path(self.variables.stl_export_path.get()),
            docket_config=self._docket_config,
        )
        task.run()

    def _move_files(self) -> None:
        progress_increment = 100 / len(file_utility.move_items)
        self.variables.progress.set(0)

        for item in file_utility.move_items:
            file_utility.move_item(item)
            self.variables.progress.set(
                self.variables.progress.get() + progress_increment
            )
            self.main_ui.update_idletasks()

        file_utility.delete_all()
