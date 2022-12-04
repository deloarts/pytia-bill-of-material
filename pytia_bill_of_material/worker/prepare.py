"""
    Preparation Task: Prepares the document for the export.
"""

import os
from pathlib import Path

from const import BOM, DOCKETS, DRAWINGS, STLS, STPS
from helper.lazy_loaders import LazyDocumentHelper
from models.paths import Paths
from protocols.task_protocol import TaskProtocol
from pycatia.in_interfaces.document import Document
from pycatia.product_structure_interfaces.product import Product
from pytia.exceptions import PytiaDifferentDocumentError
from pytia.framework import framework
from pytia.log import log
from pytia.utilities.bill_of_material import set_current_format, set_secondary_format
from pytia.utilities.docket import DocketConfig
from pytia.wrapper.documents.product_documents import PyProductDocument
from resources import resource


class PrepareTask(TaskProtocol):
    """
    This class is responsible for preparing the document for the export.
    It sets up the catia bom format and retrieves all paths from all documents.

    Args:
        TaskProtocol (_type_): The protocol for the task runner.

    Raises:
        PytiaDifferentDocumentError: Raised when the initial document has changed.
    """

    __slots__ = ("_doc_helper", "_paths", "_docket_config")

    def __init__(self, doc_helper: LazyDocumentHelper, export_root_path: Path) -> None:
        self.doc_helper = doc_helper
        self.export_root_path = export_root_path

        document = Document(framework.catia.active_document.com_object)
        if document.full_name != str(self.doc_helper.path):
            raise PytiaDifferentDocumentError(
                "The document has changed. Please open the original document and try again."
            )

    @property
    def paths(self) -> Paths:
        return self._paths

    @property
    def docket_config(self) -> DocketConfig:
        return self._docket_config

    def run(self) -> None:
        """Runs the task."""
        log.info("Preparing to export bill of material.")

        os.makedirs(Path(self.export_root_path, BOM))
        os.makedirs(Path(self.export_root_path, DOCKETS))
        os.makedirs(Path(self.export_root_path, DRAWINGS))
        os.makedirs(Path(self.export_root_path, STLS))
        os.makedirs(Path(self.export_root_path, STPS))

        self._set_catia_bom_format()
        self._paths: Paths = self._retrieve_paths(self.doc_helper.document)
        self._docket_config = DocketConfig.from_dict(resource.docket)

    @staticmethod
    def _set_catia_bom_format() -> None:
        """
        Sets the BOM format to the format specified in the `bom.json` (`header_items`) config file.
        """
        header_items = tuple(item for item in resource.bom.header_items)
        set_current_format(header_items)
        set_secondary_format(header_items)

    @staticmethod
    def _retrieve_paths(product: PyProductDocument) -> Paths:
        """
        Retrieves the paths of all items of the given CATIA product as Paths model. The content of \
            the returned Paths object looks like this: 
            `{ 'Part1': 'C:\\Users\\..\\Part1.CATPart', 'Part2': 'C:\\Users\\..\\Part2.CATPart' }`

        Args:
            product (PyProductDocument): The pytia document wrapper object from which to retrieve \
                the paths.

        Returns:
            Paths: The Paths model, that contains a dict of all partnumbers as keys and paths of \
                that partnumbers as values.
        """
        log.info(f"Reading all paths of {product.product.part_number!r}.")
        paths = Paths()
        paths.items[product.product.part_number] = Path(product.product.full_name)

        def iterate_tree(parent_product: Product) -> None:
            for i in range(1, parent_product.products.count + 1):
                current_product = parent_product.products.item(i)
                try:
                    # If there are items in the tree that aren't parts or products the
                    # iteration will fail, because the reference product cannot be fetched.
                    # Maybe this should be done in a better way, without a try-except clause.
                    current_partnumber = Product(current_product.com_object).part_number
                    current_path = Path(Product(current_product.com_object).full_name)
                    paths.items[current_partnumber] = current_path
                    log.info(
                        f"Indexed item {current_product.name!r} to {str(current_path)!r}."
                    )
                    iterate_tree(current_product)
                except Exception as e:
                    log.warning(
                        f"Skipped adding item {current_product.name!r} to paths: {e}"
                    )

        iterate_tree(product.product)
        return paths
