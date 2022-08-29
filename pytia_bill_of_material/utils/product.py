"""
    Utility functions associated to the CATIA product.
"""

from pathlib import Path

from const import TEMP_EXPORT
from models.paths import Paths
from pytia.framework.product_structure_interfaces.product import Product
from pytia.log import log
from pytia.utilities.bill_of_material import (
    export_bom,
    set_current_format,
    set_secondary_format,
)
from pytia.wrapper.documents.product_documents import PyProductDocument
from resources import resource

from utils.files import file_utility


def retrieve_paths(product: PyProductDocument) -> Paths:
    """
    Retrieves the paths of all items of the given CATIA product as Paths model. The content of the
    returned Paths object looks like this: 
        `{ 'Part1': 'C:\\Users\\..\\Part1.CATPart', 'Part2': 'C:\\Users\\..\\Part2.CATPart' }`

    Args:
        product (PyProductDocument): The pytia document wrapper object from which to retrieve \
            the paths.

    Returns:
        Paths: The Paths model, that contains a dict of all partnumbers as keys and paths of that \
            partnumbers as values.
    """
    log.info(f"Reading all paths of {product.product.part_number!r}.")
    paths = Paths()
    paths.items[product.product.part_number] = Path(product.product.full_name)

    def iterate_tree(parent_product: Product) -> None:
        for i in range(1, parent_product.products.count + 1):
            current_product = parent_product.products.item(i)
            current_partnumber = Product(current_product.com_object).part_number
            current_path = Path(Product(current_product.com_object).full_name)
            paths.items[current_partnumber] = current_path
            iterate_tree(current_product)

    iterate_tree(product.product)
    return paths


def set_catia_bom_format() -> None:
    """
    Sets the BOM format to the format specified in the `bom.json` (`header_items`) config file.
    """
    header_items = tuple(item for item in resource.bom.header_items)
    set_current_format(header_items)
    set_secondary_format(header_items)


def export_bill_of_material(product: PyProductDocument) -> Path:
    """
    Exports the bill of material from the given pytia product document wrapper as excel (xls) file.
    Call `set_catia_bom_format` before calling this function.
    The excel file will be exported to the users temp folder.

    Args:
        product (PyProductDocument): The pytia product document wrapper object of the CATIA \
            product from which to export the bill of material.

    Returns:
        Path: The path to the exported excel file.
    """
    path = Path(
        export_bom(
            product=product.product,
            filename=file_utility.get_random_filename(filetype="xls"),
            folder=TEMP_EXPORT,
        )
    )
    return path
