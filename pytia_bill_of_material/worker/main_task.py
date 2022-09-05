"""
    Submodule for the main task: Exporting data.
    
    TODO: Split up the main task. This class and its functions have too many responsibilities.

    TODO: Create a class for handling the main tasks' files (temp excel files, png files, etc.).

    TODO: Proper documentation.
"""

from pathlib import Path
from tkinter import Tk
from tkinter import messagebox as tkmsg
from typing import Callable, List

from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import LOGON, TEMP_EXPORT, Status
from helper.lazy_loaders import LazyDocumentHelper
from helper.names import get_data_export_name
from models.bom import BOMAssemblyItem
from models.paths import Paths
from pytia.exceptions import PytiaDifferentDocumentError, PytiaWrongDocumentTypeError
from pytia.framework import framework
from pytia.framework.in_interfaces.document import Document
from pytia.log import log
from pytia.utilities.docket import DocketConfig
from pytia.wrapper.documents.part_documents import PyPartDocument
from pytia.wrapper.documents.product_documents import PyProductDocument
from pytia_ui_tools.utils.qr import QR
from resources import resource
from utils import export
from utils.bom import generate_report, save_bom, sort_bom
from utils.excel import (
    convert_xls_to_xlsx,
    get_workbook_from_xlsx,
    retrieve_bom_from_catia_export,
)
from utils.files import file_utility
from utils.product import export_bill_of_material, retrieve_paths, set_catia_bom_format
from utils.system import explorer


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
        self.paths: Paths
        self.xls_path: Path
        self.xlsx_path: Path
        self.qr_path: Path

        self.docket_config: DocketConfig

        self.items_to_export: List[BOMAssemblyItem] = []

        self.variables.progress.set(0)
        self.layout.progress_bar.grid()

        self._abort = False
        self._status = Status.SKIPPED

    def run(self) -> None:
        self._run_task(self._prepare)
        self._run_task(self._export_bom_from_catia)
        self._run_task(self._process_bom_from_catia_export)
        self._run_task(self._create_report)
        self.variables.progress.set(100)

        if self._status == Status.OK:
            self._save_finished_bom()
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
        log.info("Preparing to export bill of material.")

        document = Document(framework.catia.active_document.com_object)
        if document.full_name != self.doc_helper.path:
            raise PytiaDifferentDocumentError(
                "The document has changed. Please open the original document and try again."
            )

        set_catia_bom_format()
        self.paths: Paths = retrieve_paths(self.doc_helper.document)
        self.docket_config = DocketConfig.from_dict(resource.docket)

    def _export_bom_from_catia(self) -> None:
        log.info("Exporting bill of material from catia.")
        self.xls_path = export_bill_of_material(product=self.doc_helper.document)
        self.xlsx_path = convert_xls_to_xlsx(xls_path=self.xls_path)

    def _process_bom_from_catia_export(self) -> None:
        log.info("Processing bill of material.")
        wb = get_workbook_from_xlsx(xlsx_path=self.xlsx_path)
        self.variables.bom = retrieve_bom_from_catia_export(
            worksheet=wb.worksheets[0],
            paths=self.paths,
            overwrite_project=self.variables.project.get(),
        )
        sort_bom(bom=self.variables.bom)
        file_utility.add_delete(path=self.xls_path, ask_retry=True)
        file_utility.add_delete(path=self.xlsx_path, ask_retry=True)

    def _create_report(self) -> None:
        log.info("Creating report.")
        self.variables.report = generate_report(bom=self.variables.bom)
        self._status = self.variables.report.status

    def _save_finished_bom(self) -> None:
        log.info("Saving finished bill of material.")
        source_path = save_bom(
            bom=self.variables.bom,
            folder=TEMP_EXPORT,
            filename=file_utility.get_random_filename(),
        )
        target_path = Path(self.variables.bom_export_path.get())
        file_utility.add_move(
            source=source_path, target=target_path, delete_existing=True, ask_retry=True
        )

    def _generate_qr(self, bom_item: BOMAssemblyItem) -> Path:
        project = bom_item.properties[resource.bom.required_header_items.project]
        machine = bom_item.properties[resource.bom.required_header_items.machine]
        partnumber = bom_item.properties[resource.bom.required_header_items.partnumber]
        revision = bom_item.properties[resource.bom.required_header_items.revision]

        qr = QR()
        qr_data = {
            "project": project,
            "machine": machine,
            "partnumber": partnumber,
            "revision": revision,
        }
        qr.generate(data=qr_data)
        qr_path = qr.save(
            path=Path(
                TEMP_EXPORT,
                file_utility.get_random_filename(filetype="png"),
            )
        )
        # atexit.register(lambda: delete_file(qr_path, warning=True))
        file_utility.add_delete(path=qr_path, skip_silent=True)
        return qr_path

    def _export_item(self, bom_item: BOMAssemblyItem) -> None:
        log.info(f"Exporting data of item {bom_item.partnumber!r}.")

        export_filename = get_data_export_name(bom_item)
        qr_path = self._generate_qr(bom_item=bom_item)

        if ".CATPart" in str(bom_item.path):
            with PyPartDocument() as part_document:
                part_document.open(bom_item.path)
                if self.variables.export_docket.get():
                    export.export_docket(
                        filename=export_filename,
                        folder=Path(self.variables.docket_export_path.get()),
                        document=part_document,
                        config=self.docket_config,
                        project=bom_item.properties[
                            resource.bom.required_header_items.project
                        ],
                        machine=bom_item.properties[
                            resource.bom.required_header_items.machine
                        ],
                        partnumber=bom_item.properties[
                            resource.bom.required_header_items.partnumber
                        ],
                        revision=bom_item.properties[
                            resource.bom.required_header_items.revision
                        ],
                        quantity=bom_item.properties[
                            resource.bom.required_header_items.quantity
                        ],
                        qr_path=qr_path,
                    )

                if self.variables.export_stp.get():
                    export.export_stp(
                        filename=export_filename,
                        folder=Path(self.variables.stp_export_path.get()),
                        document=part_document,
                    )
                if self.variables.export_stl.get():
                    export.export_stl(
                        filename=export_filename,
                        folder=Path(self.variables.stl_export_path.get()),
                        document=part_document,
                    )

        elif ".CATProduct" in str(bom_item.path):
            with PyProductDocument() as product_document:
                product_document.open(bom_item.path)
                if self.variables.export_docket.get():
                    export.export_docket(
                        filename=export_filename,
                        folder=Path(self.variables.docket_export_path.get()),
                        document=product_document,
                        config=self.docket_config,
                        project=bom_item.properties[
                            resource.bom.required_header_items.project
                        ],
                        quantity=bom_item.properties[
                            resource.bom.required_header_items.quantity
                        ],
                        logon=LOGON,
                        qr_path=qr_path,
                    )
                if self.variables.export_stp.get():
                    export.export_stp(
                        filename=export_filename,
                        folder=Path(self.variables.stp_export_path.get()),
                        document=product_document,
                    )

        else:
            raise PytiaWrongDocumentTypeError(
                f"Failed exporting data: Document {str(bom_item.path)!r} is neither a part nor "
                "a product."
            )

    def _export_items(self) -> None:
        if any(
            [
                self.variables.export_docket.get(),
                self.variables.export_stp.get(),
                self.variables.export_stl.get(),
            ]
        ):
            for item in self.variables.bom.summary.items:
                if not resource.applied_keywords.source in item.properties:
                    raise Exception(
                        f"Keyword {resource.applied_keywords.source!r} not in bill of material."
                    )
                if (
                    item.properties[resource.applied_keywords.source]
                    == resource.applied_keywords.made
                ):
                    self.items_to_export.append(item)

            progress_increment = 100 / len(self.items_to_export)
            self.variables.progress.set(1)
            self.main_ui.update_idletasks()
            for item in self.items_to_export:
                self._export_item(bom_item=item)
                self.variables.progress.set(
                    self.variables.progress.get() + progress_increment
                )
                self.main_ui.update_idletasks()
            log.info("Finished item export.")
        else:
            log.info("Skipping item export: None selected.")

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
