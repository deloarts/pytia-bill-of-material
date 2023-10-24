"""
    Exports all items selected by the user. Dockets, STP, STL, ...
"""

from pathlib import Path

from const import DOCKETS
from const import DRAWINGS
from const import JPGS
from const import LOGON
from const import STLS
from const import STPS
from const import TEMP_EXPORT
from helper.lazy_loaders import LazyDocumentHelper
from helper.names import get_data_export_name
from models.bom import BOM
from models.bom import BOMAssemblyItem
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

    def __init__(
        self,
        lazy_loader: LazyDocumentHelper,
        runner: Runner,
        bom: BOM,
        export_docket: bool,
        export_drawing: bool,
        export_stp: bool,
        export_stl: bool,
        export_jpg: bool,
        export_root_path: Path,
        docket_config: DocketConfig,
    ) -> None:
        """
        Inits the class.

        Args:
            lazy_loader (LazyDocumentHelper): The doc helper instance.
            runner (Runner): The task runner instance.
            bom (BOM): The BOM object.
            export_docket (bool): Wether to export the docket or not.
            export_drawing (bool): Wether to export the drawing or not.
            export_stp (bool): Wether to export the stp or not.
            export_stl (bool): Wether to export the stl or not.
            export_jpg (bool): Wether to export the jpg or not.
            export_root_path (Path): The root folder for all exports.
            docket_config (DocketConfig): The configuration for the docket.
        """
        self.lazy_loader = lazy_loader
        self.runner = runner
        self.bom = bom
        self.export_docket = export_docket
        self.export_drawing = export_drawing
        self.export_stp = export_stp
        self.export_stl = export_stl
        self.export_jpg = export_jpg
        self.export_root_path = export_root_path
        self.docket_config = docket_config

    def run(self) -> None:
        """
        Runs the task.

        Raises:
            Exception: Raised when the keyword for 'source' is not in the BOM.
        """
        log.info("Exporting selected items.")
        if any(
            [
                self.export_docket,
                self.export_stp,
                self.export_stl,
                self.export_drawing,
                self.export_jpg,
            ]
        ):
            self.lazy_loader.close_all_documents()

            for item in self.bom.summary.items:
                if not resource.applied_keywords.source in item.properties:
                    raise Exception(
                        f"Keyword {resource.applied_keywords.source!r} not in bill of material."
                    )
                if (
                    item.properties[resource.applied_keywords.source]
                    == resource.applied_keywords.made
                ):
                    self.runner.add(
                        func=self._export_item,
                        name=f"Export item {item.partnumber!r}",
                        bom_item=item,
                    )

            self.runner.run_tasks()
            log.info("Finished item export.")
        else:
            log.info("Skipping item export: None selected.")

    def _generate_qr(self, bom_item: BOMAssemblyItem) -> Path:
        """
        Generates a qr jpg file and saves it to the temp directory. Returns the path.
        The QR ode contains a serialized json of: project, machine, partnumber and revision.

        Args:
            bom_item (BOMAssemblyItem): An item of the BOM object, from which data to generate the \
                qr code.

        Returns:
            Path: The path to the generated jpg file.
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
                self.export_root_path,
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
                if self.export_docket:
                    export.export_docket(
                        filename=export_filename_with_project,
                        folder=Path(self.export_root_path, DOCKETS),
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

                if self.export_drawing:
                    export.export_drawing(
                        filename=export_filename,
                        folder=Path(self.export_root_path, DRAWINGS),
                        document=part_document,
                    )
                if self.export_stp:
                    export.export_stp(
                        filename=export_filename,
                        folder=Path(self.export_root_path, STPS),
                        document=part_document,
                    )
                if self.export_stl:
                    export.export_stl(
                        filename=export_filename,
                        folder=Path(self.export_root_path, STLS),
                        document=part_document,
                    )
                if self.export_jpg:
                    views = [
                        (view[0], view[1], view[2])
                        for view in resource.settings.export.jpg_views
                    ]
                    export.export_jpg(
                        filename=export_filename,
                        folder=Path(self.export_root_path, JPGS),
                        views=views,
                        bg=(1, 1, 1),
                    )

        elif ".CATProduct" in str(bom_item.path):
            with PyProductDocument() as product_document:
                product_document.open(bom_item.path)
                if self.export_docket:
                    export.export_docket(
                        filename=export_filename_with_project,
                        folder=Path(self.export_root_path, DOCKETS),
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
                if self.export_drawing:
                    export.export_drawing(
                        filename=export_filename,
                        folder=Path(self.export_root_path, DRAWINGS),
                        document=product_document,
                    )
                if self.export_stp:
                    export.export_stp(
                        filename=export_filename,
                        folder=Path(self.export_root_path, STPS),
                        document=product_document,
                    )
                if self.export_jpg:
                    views = [
                        (view[0], view[1], view[2])
                        for view in resource.settings.export.jpg_views
                    ]
                    export.export_jpg(
                        filename=export_filename,
                        folder=Path(self.export_root_path, JPGS),
                        views=views,
                        bg=(1, 1, 1),
                    )

        else:
            raise PytiaWrongDocumentTypeError(
                f"Failed exporting data: Document {str(bom_item.path)!r} is neither a part nor "
                "a product."
            )
