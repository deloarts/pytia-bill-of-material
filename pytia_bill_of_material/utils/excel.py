"""
    Excel utility: Functions for handling Excel files.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List

from const import EXCEL_EXE, KEEP, X000D
from exceptions import PytiaConvertError, PytiaDispatchError, PytiaNotInstalledError
from models.bom import BOM, BOMAssembly, BOMAssemblyItem
from models.paths import Paths
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.workbook import Workbook
from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet
from pytia.log import log
from resources import resource
from win32com.client import CDispatch, Dispatch
from win32com.client.gencache import EnsureDispatch
from win32com.server.exception import COMException

from utils.system import application_is_running


def get_excel() -> CDispatch:
    """
    Returns the EXCEL com object.

    Raises:
        PytiaNotInstalledError: Raised when MS Excel is not installed.
        PytiaDispatchError: Raises when the connection to the Excel com host fails.

    Returns:
        CDispatch: The Excel com object.
    """
    try:
        # app = EnsureDispatch("EXCEL.Application")
        app = Dispatch("EXCEL.Application")
        return app  # type: ignore
    except COMException as e:
        raise PytiaNotInstalledError(
            f"Excel is not installed on this system: {e}"
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise PytiaDispatchError(f"Failed connecting to Excel: {e}") from e


def convert_xls_to_xlsx(xls_path: Path) -> Path:
    """
    Converts the xls file format to the xlsx format. This is done by using the installed Excel
    application.

    Args:
        xls_path (Path): The path to the file to convert.

    Raises:
        FileNotFoundError: Raised when the input path does not exist.
        PytiaConvertError: Raised when the file cannot be converted (EXCEL save method fails).

    Returns:
        Path: The path to the converted xlsx file.
    """
    log.info("Converting bill of material format from 'xls' to 'xlsx'.")
    xlsx_path = Path(str(xls_path) + "x")

    if not os.path.isfile(xls_path):
        raise FileNotFoundError(f"Cannot open xls file at {xls_path}: Not found.")

    if os.path.exists(xlsx_path):
        os.remove(xlsx_path)

    keep_running = application_is_running(EXCEL_EXE)

    excel_dispatch = get_excel()
    workbook = excel_dispatch.Workbooks.Open(str(xls_path))
    try:
        workbook.SaveAs(str(xlsx_path), FileFormat=51)  # 51: Format of xlsx extension
        log.info(f"Converted bill of material to {str(xlsx_path)!r}.")
        return xlsx_path
    except Exception as e:
        raise PytiaConvertError(f"Failed to convert xls to xlsx: {e}") from e
    finally:
        workbook.Close() if keep_running else excel_dispatch.Application.Quit()
        # Delete the object, otherwise the excel process remains in the task manager.
        del excel_dispatch


def get_workbook_from_xlsx(xlsx_path: Path) -> Workbook:
    """
    Returns a Workbook object from the xlsx file. Closes the file afterwards. Only reads the data.

    Args:
        xlsx_path (Path): The path to the xlsx file.

    Returns:
        Workbook: The workbook.
    """
    workbook = load_workbook(filename=str(xlsx_path), data_only=True)
    workbook.close()
    return workbook


def get_header_positions(
    worksheet: Worksheet | ReadOnlyWorksheet, row: int, header_items: tuple
) -> Dict[str, int]:
    """
    Returns a dictionary of the header positions from the from CATIA exported raw bill of material.
    Maps the header positions from the bill of material to the header names.

    Example:
    The header of the raw export looks like this: `Project | Part Number | Revision`
    Then the returned dictionary looks like this: `{"Project": 1, "Part Number": 2, "Revision": 3}`

    The index starts with `1`, so the dictionary is usable on excel columns.

    This method is purely for verifying the raw CATIA export. If everything is correct, then
    CATIA will export all later required header items on the correct position, given in the
    bom.json config file.

    Args:
        worksheet (Worksheet | ReadOnlyWorksheet): The worksheet to get the header positions from.
        row (int): The row in which to look for the header positions.
        header_items (tuple): The header names to match.

    Raises:
        KeyError: Raised if the header names do not exist in the worksheet.

    Returns:
        Dict[str, int]: The dictionary of header positions.
    """
    header: dict = {}

    for i in range(1, worksheet.max_column + 1):
        header[worksheet.cell(row, i).value] = i

    # Check if CATIA exported all headers from the provided header items dict from the bom.json
    for item in header_items:
        if item not in header.keys():
            raise KeyError(
                f"Header item {item!r} not found in exported bill of material."
            )

    # Check if all required header items from the bom.json are in the exported headers
    # TODO: Put this into another function, this function has too many responsibilities.
    for required_header in resource.bom.required_header_items.values:
        if required_header not in header.keys():
            raise KeyError(
                f"The required header item {required_header!r} is not present in the exported "
                "bill of material. Please add this header to the bom.json."
            )

    log.info("Retrieved header items from excel worksheet.")
    return header


def create_header(worksheet: Worksheet, items: tuple) -> None:
    """
    Creates a header row in the given worksheet.

    Args:
        worksheet (Worksheet): The worksheet into which to create the header row.
        items (tuple): The header items to create.
    """
    if isinstance(resource.bom.header_row, int):
        for index, item in enumerate(items):
            worksheet.cell(resource.bom.header_row + 1, index + 1).value = item
        log.info(f"Created header for worksheet {worksheet.title!r}")
    else:
        log.info(f"Skipped creating header for worksheet {worksheet.title!r}.")


def write_data(
    worksheet: Worksheet, header_items: tuple, data: List[BOMAssemblyItem]
) -> None:
    """
    Writes the properties from the given data object to the given worksheet.
    Takes care that each datum will be written to the corresponding header.

    Args:
        worksheet (Worksheet): The worksheet to add the data to.
        header_items (tuple): The header items.
        data (List[BOMAssemblyItem]): The actual data.
    """
    for ri, rv in enumerate(data):
        for ci, cv in enumerate(header_items):
            worksheet.cell(
                row=ri + resource.bom.data_row + 1, column=ci + 1
            ).value = rv.properties[cv]
    log.info(f"Wrote all data to worksheet {worksheet.title!r}.")


def row_is_empty(worksheet: Worksheet | ReadOnlyWorksheet, row: int) -> bool:
    """Returns wether the given row is empty or not."""
    return all(
        [
            worksheet.cell(row, i).value is None
            for i in range(1, worksheet.max_column + 1)
        ]
    )


def style_worksheet(worksheet: Worksheet) -> None:
    """Styles the worksheet as stated in the bom.json config file."""
    for column_cells in worksheet.columns:
        # Set format, font and size
        for index, cell in enumerate(column_cells):
            if index > resource.bom.data_row - 1:
                color = (
                    resource.bom.data_color_1
                    if index % 2 == 0
                    else resource.bom.data_color_2
                )
                bg_color = (
                    resource.bom.data_bg_color_1
                    if index % 2 == 0
                    else resource.bom.data_bg_color_2
                )
                cell.fill = PatternFill(
                    start_color=bg_color, end_color=bg_color, fill_type="solid"
                )
            else:
                color = None
            cell.number_format = "@"
            cell.font = Font(
                name=resource.bom.font, size=resource.bom.size, color=color
            )
            cell.alignment = Alignment(horizontal="left", vertical="center")

        # Set font and height for the header row
        if isinstance(resource.bom.header_row, int):
            worksheet.row_dimensions[resource.bom.header_row + 1].height = 20
            column_cells[resource.bom.header_row].font = Font(
                name=resource.bom.font,
                size=resource.bom.size,
                bold=True,
                color=resource.bom.header_color,
            )
            column_cells[resource.bom.header_row].fill = PatternFill(
                start_color=resource.bom.header_bg_color,
                end_color=resource.bom.header_bg_color,
                fill_type="solid",
            )
            column_cells[resource.bom.header_row].alignment = Alignment(
                horizontal="center", vertical="center"
            )

        # Set cell width
        length = max(len(str(cell.value)) * 1.1 for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = (
            length if length > 2 else 2
        )

    log.info(f"Styled worksheet {worksheet.title!r}.")


def retrieve_bom_from_catia_export(
    worksheet: Worksheet | ReadOnlyWorksheet,
    paths: Paths,
    overwrite_project: str = KEEP,
) -> BOM:
    """
    Extracts all bill of materials and the summary from the CATIA export EXCEL file.
    Some keyword names depend on the language of the CATIA UI. It is therefor necessary to
    check the language first, the the keywords can be matched.

    Args:
        worksheet (Worksheet | ReadOnlyWorksheet): The worksheet from which to extract the data.
        paths (Paths): The paths from all CATIA partnumbers in the BOM.
        overwrite_project (str): The project number that will be written into the BOM object. \
            If set to `KEEP` all existing project number will be left, otherwise the provided 
            string will be written into the BOM object.

    Raises:
        KeyError: Raised when the exported EXCEL file has no partnumber column.
        KeyError: Raised when there is a partnumber in the BOM that is not in the paths list.

    Returns:
        BOM: The bill of material object.
    """
    bom = BOM()
    assembly: BOMAssembly | None = None
    header_positions: dict = {}
    data_row = 0
    is_summary = False

    log.info("Retrieving bill of material from exported Excel file.")
    header_items = tuple(item for item in resource.bom.header_items)

    for ri in range(1, worksheet.max_row + 1):
        _bom_or_summary = str(worksheet.cell(ri, 1).value).split(": ")[0]
        _name = str(worksheet.cell(ri, 1).value).split(": ")[-1]

        if row_is_empty(worksheet, ri) and assembly is not None and not is_summary:
            bom.assemblies.append(assembly)
            assembly = None

        elif resource.applied_keywords.bom in _bom_or_summary:
            assembly = BOMAssembly(partnumber=_name, path=paths.items[_name])
            header_positions = get_header_positions(
                worksheet=worksheet, row=ri + 1, header_items=header_items
            )
            data_row = ri + 2
            log.info(f"Processing BOM of element {_name!r}.")

        elif resource.applied_keywords.summary in _bom_or_summary:
            is_summary = True
            assembly = BOMAssembly(partnumber=_name, path=paths.items[_name])
            header_positions = get_header_positions(
                worksheet=worksheet, row=ri + 4, header_items=header_items
            )
            data_row = ri + 5
            log.info(f"Processing BOM summary.")

        if assembly is not None and ri >= data_row:
            row_data: dict = {}
            for position in header_positions:
                cell_value = worksheet.cell(ri, header_positions[position]).value

                if isinstance(cell_value, str) and X000D in cell_value:
                    # This is a result of legacy CATIA macros. This isn't needed if all
                    # parts and products are setup with the pytia-property-manager.
                    cell_value = cell_value.replace("_x000D_\n", "\n")

                if isinstance(cell_value, str) and re.match(r"^\s+$", cell_value):
                    # CATIA exports empty cells as chr(13). This results in a space
                    # string " " instead of a truly empty cell. This is fixed by checking
                    # for only-whitespace characters and replacing them with None.
                    cell_value = None

                cell_value = overwrite_project_number(
                    header_position=position,
                    cell_value=cell_value,
                    overwrite_number=overwrite_project,
                )

                cell_value = translate_username(
                    header_position=position, cell_value=cell_value
                )

                print(type(cell_value))

                row_data[position] = cell_value

            if is_summary:
                bom.summary = assembly

            if not resource.applied_keywords.partnumber in row_data:
                raise KeyError(
                    f"Cannot find keyword {resource.applied_keywords.partnumber!r} in exported Excel file. "
                    "Are your language settings correct? Or is the $partnumber keyword not set "
                    "in the bom.json's header_items?"
                )

            if row_data[resource.applied_keywords.partnumber] is None:
                raise ValueError("The value for the partnumber is empty.")

            if row_data[resource.applied_keywords.partnumber] not in paths.items:
                raise KeyError(f"Cannot find path for BOM item {_name!r}.")

            assembly_item = BOMAssemblyItem(
                partnumber=row_data[resource.applied_keywords.partnumber],
                properties=row_data,
                path=paths.items[row_data[resource.applied_keywords.partnumber]],
            )
            assembly.items.append(assembly_item)
    return bom


def overwrite_project_number(
    header_position: str, cell_value: str | Any | None, overwrite_number: str
) -> str | Any | None:
    """
    Returns the overwritten project number if the header position is the project and if the user
    selected the project number to be overwritten.
    Otherwise returns the given cell_value without changes.

    Args:
        header_position (str): The header position (the name of the header).
        cell_value (str | Any | None): The cell value to be overwritten.
        overwrite_number (str): The project number that will be written.

    Returns:
        str | Any | None: The cell value or the overwritten project number.
    """
    if (
        header_position == resource.bom.required_header_items.project
        and overwrite_number != KEEP
    ):
        return overwrite_number
    return cell_value


def translate_username(
    header_position: str, cell_value: str | Any | None
) -> str | Any | None:
    """
    Returns the translated username if the header position is creator or modifier.
    Otherwise returns the given cell_value without changes.

    Args:
        header_position (str): The header position (the name of the header).
        cell_value (str | Any | None): The cell value to be translated.

    Returns:
        str | Any | None: The translated username or the cell value.
    """
    if (
        resource.settings.export.apply_username_in_bom
        and (
            header_position == resource.props.creator
            or header_position == resource.props.modifier
        )
        and resource.user_exists(str(cell_value))
    ):
        return resource.get_user_by_logon(str(cell_value)).name
    return cell_value
