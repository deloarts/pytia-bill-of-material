"""
    Submodule for the main task: Exporting data.
"""

from pathlib import Path
from tkinter import Tk
from tkinter import messagebox as tkmsg

from app.main.frames import Frames
from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import Status
from helper.lazy_loaders import LazyDocumentHelper
from models.bom import BOM
from models.paths import Paths
from pytia.log import log
from pytia.utilities.docket import DocketConfig
from resources import resource
from utils.files import file_utility
from utils.system import explorer

from .catia_export import CatiaExportTask
from .export_items import ExportItemsTask
from .make_report import MakeReportTask
from .move_files import MoveFilesTask
from .prepare import PrepareTask
from .process_bom import ProcessBomTask
from .runner import Runner
from .save_bom import SaveBomTask


class MainTask:
    """
    This class runs all tasks to export and process the bill of material.
    It uses the task runner to update the UI state.
    """

    def __init__(
        self,
        main_ui: Tk,
        layout: Layout,
        ui_setter: UISetter,
        doc_helper: LazyDocumentHelper,
        variables: Variables,
        frames: Frames,
    ):
        """
        Inits the main task class.

        This class hold 3 runners:
        - Main runner for export handling and processing the bill of material.
        - Export runner for handling all file exports.
        - Move runner for releasing all exported files.

        Args:
            main_ui (Tk): The main window.
            layout (Layout): The layout of the main window.
            ui_setter (UISetter): The ui setter for the main window.
            doc_helper (LazyDocumentHelper): The doc helper object.
            variables (Variables): The main windows variables.
            frames (Frames): The main windows frames.
        """
        self.main_ui = main_ui
        self.layout = layout
        self.ui_setter = ui_setter
        self.doc_helper = doc_helper
        self.variables = variables
        self.frames = frames

        self._abort = False
        self._project = variables.project.get()
        self._status = Status.SKIPPED
        self._xlsx: Path
        self._paths: Paths
        self._docket_config: DocketConfig
        self._bom: BOM

        self.runner_main = Runner(
            root=self.main_ui,
            callback_variable=self.variables.progress,
        )
        self.runner_item_export = Runner(
            root=self.main_ui,
            callback_variable=self.variables.progress,
        )
        self.runner_move_files = Runner(
            root=self.main_ui,
            callback_variable=self.variables.progress,
        )

        self.runner_main.add(func=self._prepare, name="Prepare Export")
        self.runner_main.add(func=self._catia_export, name="Catia Export")
        self.runner_main.add(func=self._process_bom, name="Process Bill of Material")
        self.runner_main.add(func=self._create_report, name="Create Report")

    def run(self) -> None:
        """Runs the task."""
        self.runner_main.run_tasks()

        if self._status == Status.OK:
            self._save_bom()
            self._export_items()
            self._move_files()

            log.info("Re-opening main document...")
            self.doc_helper.framework.catia.documents.open(self.doc_helper.path)

            if file_utility.all_moved:
                log.info("Export completed successfully.")
                if tkmsg.askyesno(
                    title=resource.settings.title,
                    message=(
                        "Successfully exported the bill of material.\n\n"
                        "Do you want to open the export folder?"
                    ),
                ):
                    explorer(Path(self.variables.bom_export_path.get()))
            else:
                log.info("Export completed with skipped files.")
                tkmsg.showwarning(
                    title=resource.settings.title,
                    message=(
                        "Finished the export, but not all files have been moved to their target "
                        "folder.\n\nMaybe you have skipped some files?"
                    ),
                )

        elif self._status == Status.FAILED:
            log.info("Export failed: Some properties don't match the filters.")
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

        self.ui_setter.normal()

    def _prepare(self, *_) -> None:
        task = PrepareTask(doc_helper=self.doc_helper)
        task.run()

        self._paths = task.paths
        self._docket_config = task.docket_config

    def _catia_export(self, *_) -> None:
        task = CatiaExportTask(doc_helper=self.doc_helper)
        task.run()

        self._xlsx = task.xlsx

    def _process_bom(self, *_) -> None:
        task = ProcessBomTask(
            xlsx=self._xlsx, project_number=self._project, paths=self._paths
        )
        task.run()

        self._bom = task.bom

    def _create_report(self, *_) -> None:
        task = MakeReportTask(bom=self._bom)
        task.run()

        self._status = task.status
        self.variables.report = task.report

    def _save_bom(self, *_) -> None:
        task = SaveBomTask(
            bom=self._bom, path=Path(self.variables.bom_export_path.get())
        )
        task.run()

    def _export_items(self, *_) -> None:
        task = ExportItemsTask(
            lazy_loader=self.doc_helper,
            runner=self.runner_item_export,
            bom=self._bom,
            export_docket=self.variables.export_docket.get(),
            export_drawing=self.variables.export_drawing.get(),
            export_stp=self.variables.export_stp.get(),
            export_stl=self.variables.export_stl.get(),
            docket_path=Path(self.variables.docket_export_path.get()),
            drawing_path=Path(self.variables.drawing_export_path.get()),
            stp_path=Path(self.variables.stp_export_path.get()),
            stl_path=Path(self.variables.stl_export_path.get()),
            docket_config=self._docket_config,
        )
        task.run()

    def _move_files(self, *_) -> None:
        task = MoveFilesTask(runner=self.runner_move_files)
        task.run()
