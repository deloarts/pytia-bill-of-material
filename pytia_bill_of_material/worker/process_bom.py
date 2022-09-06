"""
    Processes the xlsx file and generates the BOM object from it.
"""

import re
from pathlib import Path
from typing import Any, Dict

from const import KEEP, X000D
from models.bom import BOM, BOMAssembly, BOMAssemblyItem
from models.paths import Paths
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet
from protocols.task_protocol import TaskProtocol
from pytia.log import log
from resources import resource
from utils.excel import row_is_empty


class ProcessBomTask(TaskProtocol):
    __slots__ = ("_xlsx", "_project", "_paths", "_bom")

    def __init__(self, xlsx: Path, project_number: str, paths: Paths) -> None:
        self._xlsx = xlsx
        self._project = project_number
        self._paths = paths

    @property
    def bom(self) -> BOM:
        return self._bom

    def run(self) -> None:
        log.info("Processing bill of material.")

        wb = self._get_workbook_from_xlsx(xlsx_path=self._xlsx)
        self._bom = self._retrieve_bom_from_catia_export(
            worksheet=wb.worksheets[0],
            paths=self._paths,
            overwrite_project=self._project,
        )
        self._sort_bom(bom=self._bom)

    @staticmethod
    def _get_workbook_from_xlsx(xlsx_path: Path) -> Workbook:
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

    @classmethod
    def _retrieve_bom_from_catia_export(
        cls,
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
                header_positions = cls._get_header_positions(
                    worksheet=worksheet, row=ri + 1, header_items=header_items
                )
                data_row = ri + 2
                log.info(f"Processing BOM of element {_name!r}.")

            elif resource.applied_keywords.summary in _bom_or_summary:
                is_summary = True
                assembly = BOMAssembly(partnumber=_name, path=paths.items[_name])
                header_positions = cls._get_header_positions(
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

                    cell_value = cls._overwrite_project_number(
                        header_position=position,
                        cell_value=cell_value,
                        overwrite_number=overwrite_project,
                    )

                    cell_value = cls._translate_username(
                        header_position=position, cell_value=cell_value
                    )

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
                    item_path = None
                    log.warning(
                        f"No path found for item {row_data[resource.applied_keywords.partnumber]!r}."
                    )
                else:
                    item_path = paths.items[
                        row_data[resource.applied_keywords.partnumber]
                    ]

                assembly_item = BOMAssemblyItem(
                    partnumber=row_data[resource.applied_keywords.partnumber],
                    properties=row_data,
                    path=item_path,
                )
                assembly.items.append(assembly_item)
                log.info(
                    f" - Added item {row_data[resource.applied_keywords.partnumber]!r} to element."
                )
        return bom

    @staticmethod
    def _get_header_positions(
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

        log.debug("Retrieved header items from excel worksheet.")
        return header

    @staticmethod
    def _overwrite_project_number(
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

    @staticmethod
    def _translate_username(
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

    @staticmethod
    def _sort_bom(bom: BOM) -> None:
        """
        Sorts the BOM model according to the `sort` item in the bom.json.
        Note: This depends on the language of the CATIA UI. Make sure that you have
        executed the `resources.apply_keywords_to_export()` method before calling this function.

        Args:
            bom (BOM): The BOM object to be sorted.
        """

        def _partnumber(assembly_item: BOMAssemblyItem):
            return assembly_item.partnumber

        def _made(assembly_item: BOMAssemblyItem):
            props = assembly_item.properties
            log.debug(f"Sorting 'made' items by {resource.bom.sort.made!r}")
            return (
                props[resource.bom.sort.made]
                if props[resource.applied_keywords.source]
                == resource.applied_keywords.made
                else None
            )

        def _bought(assembly_item: BOMAssemblyItem):
            props = assembly_item.properties
            log.debug(f"Sorting 'bought' items by {resource.bom.sort.bought!r}")
            return (
                props[resource.bom.sort.bought]
                if props[resource.applied_keywords.source]
                == resource.applied_keywords.bought
                else None
            )

        bom.summary.items.sort(key=lambda x: (_bought(x) is None, _bought(x)))
        bom.summary.items.sort(key=lambda x: (_made(x) is None, _made(x)))
        log.info("Sorted BOM items of 'Summary'.")

        for assembly in bom.assemblies:
            # assembly.items.sort(key=_source, reverse=True)
            assembly.items.sort(key=lambda x: (_bought(x) is None, _bought(x)))
            assembly.items.sort(key=lambda x: (_made(x) is None, _made(x)))
            log.debug(f"Sorted BOM items of {assembly.partnumber}.")
        log.info("Sorted BOM items of all assemblies.")