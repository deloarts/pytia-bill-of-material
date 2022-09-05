"""
    Export Task: Exports the bill of material from catia and converts the xls file
    to a xlsx file.
"""

import os
from pathlib import Path

from const import EXCEL_EXE, TEMP_EXPORT
from exceptions import PytiaConvertError
from helper.lazy_loaders import LazyDocumentHelper
from pytia.log import log
from pytia.utilities.bill_of_material import export_bom
from pytia.wrapper.documents.product_documents import PyProductDocument
from utils.excel import get_excel
from utils.files import file_utility
from utils.system import application_is_running


class CatiaExportTask:
    __slots__ = ("_doc_helper", "_xls", "_xlsx", "_bom")

    def __init__(self, doc_helper: LazyDocumentHelper) -> None:
        self._doc_helper = doc_helper

    @property
    def xls(self) -> Path:
        return self._xls

    @property
    def xlsx(self) -> Path:
        return self._xlsx

    def run(self) -> None:
        log.info("Exporting bill of material from catia.")

        self._xls = Path(
            export_bom(
                product=self._doc_helper.document.product,
                filename=file_utility.get_random_filename(filetype="xls"),
                folder=TEMP_EXPORT,
            )
        )
        self._xlsx = self._convert_xls_to_xlsx(xls_path=self._xls)

        file_utility.add_delete(path=self._xls, ask_retry=True)
        file_utility.add_delete(path=self._xlsx, ask_retry=True)

    @staticmethod
    def _convert_xls_to_xlsx(xls_path: Path) -> Path:
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
            workbook.SaveAs(
                str(xlsx_path), FileFormat=51
            )  # 51: Format of xlsx extension
            log.info(f"Converted bill of material to {str(xlsx_path)!r}.")
            return xlsx_path
        except Exception as e:
            raise PytiaConvertError(f"Failed to convert xls to xlsx: {e}") from e
        finally:
            workbook.Close() if keep_running else excel_dispatch.Application.Quit()
            # Delete the object, otherwise the excel process remains in the task manager.
            del excel_dispatch
