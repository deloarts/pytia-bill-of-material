"""
    Saves the finished bill of material file.
"""

from pathlib import Path

from const import BOM as BOM_FOLDER
from models.bom import BOM
from openpyxl.workbook import Workbook
from protocols.task_protocol import TaskProtocol
from pytia.log import log
from resources import resource
from utils.excel import create_header, style_worksheet, write_data


class SaveBomTask(TaskProtocol):
    """
    This class is used to format and save the finished bill of material file.

    Args:
        TaskProtocol (_type_): The task protocol.
    """

    __slots__ = ("_bom", "_path")

    def __init__(self, bom: BOM, export_root_path: Path, filename: str) -> None:
        self.bom = bom
        self.export_root_path = export_root_path
        self.filename = filename

    def run(self) -> None:
        """Runs the task."""
        log.info("Saving finished bill of material.")
        self._save_bom(
            bom=self.bom,
            folder=Path(self.export_root_path, BOM_FOLDER),
            filename=self.filename,
        )

    @staticmethod
    def _save_bom(bom: BOM, folder: Path, filename: str) -> Path:
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
