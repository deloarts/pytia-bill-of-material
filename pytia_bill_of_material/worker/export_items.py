"""
    Exports all items selected by the user. Dockets, STP, STL, ...
"""

import os
from pathlib import Path
from shutil import make_archive
from shutil import rmtree
from typing import Annotated
from typing import Dict

from app.main.vars import Variables
from const import BUNDLE
from const import DOCKETS
from const import DOCUMENTATION
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
from pytia_ui_tools.handlers.workspace_handler import Workspace
from pytia_ui_tools.utils.files import file_utility
from pytia_ui_tools.utils.qr import QR
from resources import resource
from templates import templates
from utils import export

from .runner import Runner

PartnumberString = Annotated[str, lambda s: str(s)]


class ExportItemsTask(TaskProtocol):
    """
    Exports all items:
    - Dockets
    - Docu Dockets
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
        variables: Variables,
        bom: BOM,
        export_root_path: Path,
        docket_config: DocketConfig,
        documentation_config: DocketConfig,
        workspace: Workspace,
    ) -> None:
        """
        Inits the class.

        Args:
            lazy_loader (LazyDocumentHelper): The doc helper instance.
            runner (Runner): The task runner instance.
            variables (Variables): The apps variables instance.
            bom (BOM): The BOM object.
            export_root_path (Path): The root folder for all exports.
            docket_config (DocketConfig): The configuration for the docket.
            documentation_config (DocketConfig): The configuration for the docu docket.
        """
        self.lazy_loader = lazy_loader
        self.runner = runner
        self.variables = variables
        self.bom = bom

        self.export_root_path = export_root_path

        self.docket_config = docket_config
        self.documentation_config = documentation_config

        self.workspace = workspace

    def run(self) -> None:
        """
        Runs the task.

        Raises:
            Exception: Raised when the keyword for 'source' is not in the BOM.
        """
        log.info("Exporting selected items.")
        if any(
            [
                self.variables.export_documentation.get(),
                self.variables.export_docket.get(),
                self.variables.export_drawing.get(),
                self.variables.export_stp.get(),
                self.variables.export_stl.get(),
                self.variables.export_jpg.get(),
            ]
        ):
            self.lazy_loader.close_all_documents()
            complete_items: Dict[PartnumberString, BOMAssemblyItem] = {}

            # The following 'solution' is required to export all assemblies,
            # even those that don't show in the summary of the CATIA BOM.
            # It's not possible to only use all items of the bom.assemblies
            # object, because this would result in false quantities.
            # Therefor it's a must to compare those list object with great
            # care.
            for summary_item in self.bom.summary.items:
                complete_items[summary_item.partnumber] = summary_item

                for assembly in self.bom.assemblies:
                    for assembly_item in assembly.items:
                        if not assembly_item.partnumber in complete_items:
                            complete_items[assembly_item.partnumber] = assembly_item

            for partnumber, item in complete_items.items():
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
                        name=f"Export item {partnumber!r}",
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

        bundle = self.variables.bundle.get()

        machine = bom_item.properties[resource.bom.required_header_items.machine]
        partnumber = bom_item.properties[resource.bom.required_header_items.partnumber]
        revision = bom_item.properties[resource.bom.required_header_items.revision]

        export_filename = get_data_export_name(bom_item, with_project=False)
        export_filename_with_project = get_data_export_name(bom_item, with_project=True)
        bundle_name = f"{machine} {partnumber} Rev{revision}"
        bundle_path = Path(self.export_root_path, BUNDLE, bundle_name)
        if bundle:
            os.makedirs(bundle_path, exist_ok=True)

        qr_path = self._generate_qr(bom_item=bom_item)
        docu_path = Path(self.export_root_path, DOCUMENTATION)
        docket_path = bundle_path if bundle else Path(self.export_root_path, DOCKETS)
        drawing_path = bundle_path if bundle else Path(self.export_root_path, DRAWINGS)
        stp_path = bundle_path if bundle else Path(self.export_root_path, STPS)
        stl_path = bundle_path if bundle else Path(self.export_root_path, STLS)
        jpg_path = bundle_path if bundle else Path(self.export_root_path, JPGS)

        if ".CATPart" in str(bom_item.path):
            with PyPartDocument() as part_document:
                part_document.open(bom_item.path)

                if self.variables.export_documentation.get():
                    export.export_docket(
                        docket_template=templates.documentation_path,
                        filename=export_filename,
                        folder=docu_path,
                        document=part_document,
                        config=self.documentation_config,
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
                if self.variables.export_docket.get():
                    export.export_docket(
                        docket_template=templates.docket_path,
                        filename=export_filename_with_project,
                        folder=docket_path,
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
                if self.variables.export_drawing.get():
                    export.export_drawing(
                        filename=export_filename,
                        folder=drawing_path,
                        document=part_document,
                        workspace=self.workspace,
                    )
                if self.variables.export_stp.get():
                    export.export_stp(
                        filename=export_filename,
                        folder=stp_path,
                        document=part_document,
                    )
                if self.variables.export_stl.get():
                    export.export_stl(
                        filename=export_filename,
                        folder=stl_path,
                        document=part_document,
                    )
                if self.variables.export_jpg.get():
                    views = [
                        (view[0], view[1], view[2])
                        for view in resource.settings.export.jpg_views
                    ]
                    export.export_jpg(
                        filename=export_filename,
                        folder=jpg_path,
                        views=views,
                        bg=(1, 1, 1),
                    )

        elif ".CATProduct" in str(bom_item.path):
            with PyProductDocument() as product_document:
                product_document.open(bom_item.path)

                if self.variables.export_documentation.get():
                    export.export_docket(
                        docket_template=templates.documentation_path,
                        filename=export_filename,
                        folder=docu_path,
                        document=product_document,
                        config=self.documentation_config,
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
                if self.variables.export_docket.get():
                    export.export_docket(
                        docket_template=templates.docket_path,
                        filename=export_filename_with_project,
                        folder=docket_path,
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
                if self.variables.export_drawing.get():
                    export.export_drawing(
                        filename=export_filename,
                        folder=drawing_path,
                        document=product_document,
                        workspace=self.workspace,
                    )
                if self.variables.export_stp.get():
                    export.export_stp(
                        filename=export_filename,
                        folder=stp_path,
                        document=product_document,
                    )
                if self.variables.export_jpg.get():
                    views = [
                        (view[0], view[1], view[2])
                        for view in resource.settings.export.jpg_views
                    ]
                    export.export_jpg(
                        filename=export_filename,
                        folder=jpg_path,
                        views=views,
                        bg=(1, 1, 1),
                    )

        else:
            raise PytiaWrongDocumentTypeError(
                f"Failed exporting data: Document {str(bom_item.path)!r} is neither a part nor "
                "a product."
            )

        if bundle and self.variables.zip_bundle.get():
            make_archive(
                base_name=str(bundle_path),
                format="zip",
                root_dir=bundle_path,
            )
            rmtree(bundle_path)
