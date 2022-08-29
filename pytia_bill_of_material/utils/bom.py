"""
    Bill of Material utility. Functions for the BOM model.
"""

import re
from pathlib import Path
from typing import Literal

from const import Status
from models.bom import BOM, BOMAssemblyItem
from models.report import Report, ReportItem
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pytia.log import log
from resources import resource

from utils.excel import create_header, style_worksheet, write_data


def sort_bom(bom: BOM, language: Literal["en", "de"]) -> None:
    """
    Sorts the BOM model according to the `sort` item in the bom.json.
    Note: This depends on the language of the CATIA UI. Make sure that you have
    executed the `resources.apply_keywords_to_export()` method before calling this function.

    Args:
        bom (BOM): The BOM object to be sorted.
        language (Literal[&quot;en&quot;, &quot;de&quot;]): The language of the CATIA UI.
    """
    keywords = resource.keywords.en if language == "en" else resource.keywords.de

    def _partnumber(assembly_item: BOMAssemblyItem):
        return assembly_item.partnumber

    def _made(assembly_item: BOMAssemblyItem):
        props = assembly_item.properties
        log.info(f"Sorting 'made' items by {resource.bom.sort.made!r}")
        return (
            props[resource.bom.sort.made]
            if props[keywords.source] == keywords.made
            else None
        )

    def _bought(assembly_item: BOMAssemblyItem):
        props = assembly_item.properties
        log.info(f"Sorting 'bought' items by {resource.bom.sort.bought!r}")
        return (
            props[resource.bom.sort.bought]
            if props[keywords.source] == keywords.bought
            else None
        )

    bom.summary.items.sort(key=lambda x: (_bought(x) is None, _bought(x)))
    bom.summary.items.sort(key=lambda x: (_made(x) is None, _made(x)))
    log.info("Sorted BOM items of 'Summary'.")

    for assembly in bom.assemblies:
        # assembly.items.sort(key=_source, reverse=True)
        assembly.items.sort(key=lambda x: (_bought(x) is None, _bought(x)))
        assembly.items.sort(key=lambda x: (_made(x) is None, _made(x)))
        log.info(f"Sorted BOM items of {assembly.partnumber}.")


def generate_report(bom: BOM) -> Report:
    """
    Verifies the BOM model against the criteria of the filters.json.
    The verification is only performed if the conditions of the filters.json are met.
    The report will be created for the `assemblies` items of the given BOM object, because the
    `summary` item doesn't contain all items of the total assembly (Non-empty Product won't show 
    up in the summary).

    Args:
        bom (BOM): The BOM object to verify.

    Raises:
        KeyError: Raised when a condition key is not in the BOM header items.
        TypeError: Raised when a condition value of the filters.json is neither `dict` nor `bool`.
        ValueError: Raised when the property_name value of the filters.json is not in the BOM \
            header items.

    Returns:
        Report: The report object.
    """
    log.info("Verifying bill of material.")

    report = Report()

    for assembly in bom.assemblies:
        log.info(f"Verifying element {assembly.partnumber!r}:")

        for assembly_item in assembly.items:
            log.info(f"  {assembly_item.partnumber}:")
            report_item = ReportItem(
                partnumber=assembly_item.partnumber,
                path=assembly_item.path,
                parent_path=assembly.path,
            )

            for filter_item in resource.filters:
                if filter_item.property_name in assembly_item.properties:
                    conditions_satisfied = []

                    if isinstance((cond_item := filter_item.condition), bool):
                        conditions_satisfied.append(cond_item)

                    elif isinstance(cond_item, dict):
                        for cond_key in cond_item:
                            if not cond_key in assembly_item.properties:
                                raise KeyError(
                                    f"Condition key {cond_key!r} is not available in the BOM properties."
                                )

                            if (
                                assembly_item.properties[cond_key]
                                == cond_item[cond_key]
                            ):
                                conditions_satisfied.append(True)
                            else:
                                conditions_satisfied.append(False)

                    else:
                        raise TypeError(
                            f"Type of conditions ({type(cond_item)}) not valid, "
                            "must be 'bool' or 'dict'."
                        )

                    if all(conditions_satisfied):
                        if assembly_item.properties[
                            filter_item.property_name
                        ] is not None and re.match(
                            filter_item.criteria,
                            str(assembly_item.properties[filter_item.property_name]),
                        ):
                            report_item.details[filter_item.property_name] = Status.OK
                            log.info(f"    - {filter_item.property_name}: OK.")
                        else:
                            report_item.details[
                                filter_item.property_name
                            ] = Status.FAILED
                            report_item.status = Status.FAILED
                            report.status = Status.FAILED
                            log.info(f"    - {filter_item.property_name}: FAILED.")
                    else:
                        report_item.details[filter_item.property_name] = Status.SKIPPED
                        log.info(f"    - {filter_item.property_name}: SKIPPED.")

                else:
                    raise ValueError(f"Item {filter_item.property_name!r} not in BOM.")

            report.items.append(report_item)
    return report


def save_bom(bom: BOM, folder: Path, filename: str) -> Path:
    """
    Saves the bill of material from the BOM object as xlsx file. This saves only the content
    of the BOM object, regardless of wether the Report is OK or FAILED.

    Args:
        bom (BOM): The BOM object to save.
        folder (Path): The path into which to save the bill of material.
        filename (str): The name of the file to save. '.xlsx' will be added if not in name.

    Returns:
        Path: The path to the newly created xlsx file.
    """

    if ".xlsx" not in filename:
        filename += ".xlsx"

    path = Path(folder, filename)
    header_items = tuple(item for item in resource.bom.header_items)

    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.sheet_properties.tabColor = "ff0000"
    create_header(worksheet=ws, items=header_items)
    write_data(worksheet=ws, header_items=header_items, data=bom.summary.items)
    style_worksheet(worksheet=ws)

    for assembly in bom.assemblies:
        ws: Worksheet = wb.create_sheet(title=assembly.partnumber)  # type: ignore
        create_header(worksheet=ws, items=header_items)
        write_data(worksheet=ws, header_items=header_items, data=assembly.items)
        style_worksheet(worksheet=ws)

    wb.active = wb["Summary"]  # type: ignore

    wb.save(str(path))
    log.info(f"Saved processed BOM to {str(path)!r}.")

    return path
