"""
    Exports all items selected by the user. Dockets, STP, STL, ...
"""

from pathlib import Path

from const import LOGON, TEMP_EXPORT
from helper.lazy_loaders import LazyDocumentHelper
from helper.names import get_data_export_name
from models.bom import BOM, BOMAssemblyItem
from protocols.task_protocol import TaskProtocol
from pytia.exceptions import PytiaWrongDocumentTypeError
from pytia.log import log
from pytia.utilities.docket import DocketConfig
from pytia.wrapper.documents.part_documents import PyPartDocument
from pytia.wrapper.documents.product_documents import PyProductDocument
from pytia_ui_tools.utils.files import file_utility
from pytia_ui_tools.utils.qr import QR
from resources import resource
from utils import export

from .runner import Runner


class ExportItemsTask(TaskProtocol):
    """
    Exports all items:
    - Dockets
    - Drawings
    - STP
    - STL

    Args:
        TaskProtocol (_type_): The protocol for the task runner.

    Raises:
        Exception: Raised when the keyword for 'source' is not in the BOM.
        PytiaWrongDocumentTypeError: Raised when the document is neither a part nor a product.

    Returns:
        _type_: _description_
    """

    __slots__ = (
        "_lazy_loader",
        "_runner",
        "_bom",
        "_export_docket",
        "_export_stp",
        "_export_stl",
        "_docket_path",
        "_drawing_path",
        "_stp_path",
        "_stl_path",
        "_docket_config",
        "items_to_export",
    )

    def __init__(
        self,
        lazy_loader: LazyDocumentHelper,
        runner: Runner,
        bom: BOM,
        export_docket: bool,
        export_drawing: bool,
        export_stp: bool,
        export_stl: bool,
        docket_path: Path,
        drawing_path: Path,
        stp_path: Path,
        stl_path: Path,
        docket_config: DocketConfig,
    ) -> None:
        """
        Inits the class.

        Note for the export folders: All files will be exported to the user's temp directory.
        After all exports have been finished, all files will be moved to the given export paths.

        Args:
            lazy_loader (LazyDocumentHelper): The doc helper instance.
            runner (Runner): The task runner instance.
            bom (BOM): The BOM object.
            export_docket (bool): Wether to export the docket or not.
            export_drawing (bool): Wether to export the drawing or not.
            export_stp (bool): Wether to export the stp or not.
            export_stl (bool): Wether to export the stl or not.
            docket_path (Path): The destination folder for the docket.
            drawing_path (Path): The destination folder for the drawing.
            stp_path (Path): The destination folder for the stp.
            stl_path (Path): The destination folder for the stl.
            docket_config (DocketConfig): The configuration for the docket.
        """
        self._lazy_loader = lazy_loader
        self._runner = runner
        self._bom = bom
        self._export_docket = export_docket
        self._export_drawing = export_drawing
        self._export_stp = export_stp
        self._export_stl = export_stl
        self._docket_path = docket_path
        self._drawing_path = drawing_path
        self._stp_path = stp_path
        self._stl_path = stl_path
        self._docket_config = docket_config

    def run(self) -> None:
        """
        Runs the task.

        Raises:
            Exception: Raised when the keyword for 'source' is not in the BOM.
        """
        self._lazy_loader.close_all_documents()

        log.info("Exporting selected items.")
        if any(
            [
                self._export_docket,
                self._export_stp,
                self._export_stl,
                self._export_drawing,
            ]
        ):
            for item in self._bom.summary.items:
                if not resource.applied_keywords.source in item.properties:
                    raise Exception(
                        f"Keyword {resource.applied_keywords.source!r} not in bill of material."
                    )
                if (
                    item.properties[resource.applied_keywords.source]
                    == resource.applied_keywords.made
                ):
                    self._runner.add(
                        func=self._export_item,
                        name=f"Export item {item.partnumber!r}",
                        bom_item=item,
                    )

            self._runner.run_tasks()
            log.info("Finished item export.")
        else:
            log.info("Skipping item export: None selected.")

    def _generate_qr(self, bom_item: BOMAssemblyItem) -> Path:
        """
        Generates a qr png file and saves it to the temp directory. Returns the path.
        The QR ode contains a serialized json of: project, machine, partnumber and revision.

        Args:
            bom_item (BOMAssemblyItem): An item of the BOM object, from which data to generate the \
                qr code.

        Returns:
            Path: The path to the generated png file.
        """
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
        file_utility.add_delete(path=qr_path, skip_silent=True)
        return qr_path

    def _export_item(self, bom_item: BOMAssemblyItem) -> None:
        """
        Exports the BOM item.

        TODO: Refactor this into smaller bits.

        Args:
            bom_item (BOMAssemblyItem): An item of the BOM object.

        Raises:
            PytiaWrongDocumentTypeError: Raised when the BOM item is neither a part nor a product.
        """
        if bom_item.path is None:
            log.warning(
                f"Skipped export of item {bom_item.partnumber!r}: Path of item not found."
            )
            return

        log.info(f"Exporting data of item {bom_item.partnumber!r}.")
        export_filename = get_data_export_name(bom_item, with_project=False)
        export_filename_with_project = get_data_export_name(bom_item, with_project=True)
        qr_path = self._generate_qr(bom_item=bom_item)

        if ".CATPart" in str(bom_item.path):
            with PyPartDocument() as part_document:
                part_document.open(bom_item.path)
                if self._export_docket:
                    export.export_docket(
                        filename=export_filename_with_project,
                        folder=self._docket_path,
                        document=part_document,
                        config=self._docket_config,
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

                if self._export_drawing:
                    export.export_drawing(
                        filename=export_filename,
                        folder=self._drawing_path,
                        document=part_document,
                    )
                if self._export_stp:
                    export.export_stp(
                        filename=export_filename,
                        folder=self._stp_path,
                        document=part_document,
                    )
                if self._export_stl:
                    export.export_stl(
                        filename=export_filename,
                        folder=self._stl_path,
                        document=part_document,
                    )

        elif ".CATProduct" in str(bom_item.path):
            with PyProductDocument() as product_document:
                product_document.open(bom_item.path)
                if self._export_docket:
                    export.export_docket(
                        filename=export_filename_with_project,
                        folder=self._docket_path,
                        document=product_document,
                        config=self._docket_config,
                        project=bom_item.properties[
                            resource.bom.required_header_items.project
                        ],
                        quantity=bom_item.properties[
                            resource.bom.required_header_items.quantity
                        ],
                        logon=LOGON,
                        qr_path=qr_path,
                    )
                if self._export_drawing:
                    export.export_drawing(
                        filename=export_filename,
                        folder=self._drawing_path,
                        document=product_document,
                    )
                if self._export_stp:
                    export.export_stp(
                        filename=export_filename,
                        folder=self._stp_path,
                        document=product_document,
                    )

        else:
            raise PytiaWrongDocumentTypeError(
                f"Failed exporting data: Document {str(bom_item.path)!r} is neither a part nor "
                "a product."
            )
