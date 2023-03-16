"""
    Submodule for the main task: Exporting data.
"""

from datetime import datetime
from pathlib import Path
from tkinter import Tk
from tkinter import messagebox as tkmsg

from app.main.frames import Frames
from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import TEMP_EXPORT, Status
from helper.lazy_loaders import LazyDocumentHelper
from models.bom import BOM
from models.paths import Paths
from pytia.log import log
from pytia.utilities.docket import DocketConfig
from pytia_ui_tools.utils.files import file_utility
from resources import resource
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

        self.export_folder = Path(
            TEMP_EXPORT, datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        )
        self.project = variables.project.get()
        self.status = Status.SKIPPED
        self.xlsx_path: Path
        self.doc_paths: Paths
        self.docket_cfg: DocketConfig
        self.bom: BOM

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

        if self.status == Status.OK:
            self._save_bom()
            self._export_items()
            self._move_files()

            if self.doc_helper.name not in self.doc_helper.get_all_open_documents():
                log.info("Re-opening main document...")
                self.doc_helper.framework.catia.documents.open(
                    str(self.doc_helper.path)
                )

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

        elif self.status == Status.FAILED:
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

        # FIXME: There's a bug in the lazy loader: Du to the performance optimization (closing the
        # main product while exporting) the document of the lazy loader isn't available anymore.
        # So, if the user wants to run the export again, the process will fail.
        # Maybe-solution: Re-instance the lazy loader?
        self.ui_setter.normal()

    def _prepare(self, *_) -> None:
        task = PrepareTask(
            doc_helper=self.doc_helper, export_root_path=self.export_folder
        )
        task.run()

        self.doc_paths = task.paths
        self.docket_cfg = task.docket_config

    def _catia_export(self, *_) -> None:
        task = CatiaExportTask(
            doc_helper=self.doc_helper, export_root_path=self.export_folder
        )
        task.run()

        self.xlsx_path = task.xlsx

    def _process_bom(self, *_) -> None:
        task = ProcessBomTask(
            xlsx=self.xlsx_path, project_number=self.project, paths=self.doc_paths
        )
        task.run()

        self.bom = task.bom

    def _create_report(self, *_) -> None:
        task = MakeReportTask(bom=self.bom)
        task.run()

        self.status = task.status
        self.variables.report = task.report

    def _save_bom(self, *_) -> None:
        task = SaveBomTask(
            bom=self.bom,
            export_root_path=self.export_folder,
            filename=Path(self.variables.bom_export_path.get()).name,
        )
        task.run()

    def _export_items(self, *_) -> None:
        task = ExportItemsTask(
            lazy_loader=self.doc_helper,
            runner=self.runner_item_export,
            bom=self.bom,
            export_docket=self.variables.export_docket.get(),
            export_drawing=self.variables.export_drawing.get(),
            export_stp=self.variables.export_stp.get(),
            export_stl=self.variables.export_stl.get(),
            export_root_path=self.export_folder,
            docket_config=self.docket_cfg,
        )
        task.run()

    def _move_files(self, *_) -> None:
        task = MoveFilesTask(
            runner=self.runner_move_files,
            export_root_path=self.export_folder,
            bom_export_path=Path(self.variables.bom_export_path.get()),
            drawing_export_path=Path(self.variables.drawing_export_path.get()),
            docket_export_path=Path(self.variables.docket_export_path.get()),
            stp_export_path=Path(self.variables.stp_export_path.get()),
            stl_export_path=Path(self.variables.stl_export_path.get()),
        )
        task.run()
