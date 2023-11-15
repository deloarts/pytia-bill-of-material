"""
    Export Task: Exports the bill of material from catia and converts the xls file
    to a xlsx file.
"""

import os
from pathlib import Path

from const import EXCEL_EXE
from helper.lazy_loaders import LazyDocumentHelper
from protocols.task_protocol import TaskProtocol
from pytia.exceptions import PytiaConvertError
from pytia.log import log
from pytia.utilities.bill_of_material import export_bom
from pytia_ui_tools.utils.files import file_utility
from utils.excel import get_excel
from utils.system import application_is_running


class CatiaExportTask(TaskProtocol):
    """
    Exports the BOM data from CATIA. This is done via a xls file, which is the converted to
    a xlsx file.

    This class holds those files as properties.

    All exported data will be deleted at application exit.

    Args:
        TaskProtocol (_type_): The task runner protocol.

    Raises:
        FileNotFoundError: Raised when CATIA failed to export the xls file.
        PytiaConvertError: Raised when the xls file cannot be converted to a xlsx file.
    """

    __slots__ = ("_doc_helper", "_xls", "_xlsx", "_bom")

    def __init__(
        self,
        doc_helper: LazyDocumentHelper,
        export_root_path: Path,
        external_xls_path: Path | None,
    ) -> None:
        """
        Inits the class.

        Args:
            doc_helper (LazyDocumentHelper): The document helper object.
        """
        self.doc_helper = doc_helper
        self.export_root_path = export_root_path
        self.external_xls_path = external_xls_path

    @property
    def xls(self) -> Path:
        return self._xls

    @property
    def xlsx(self) -> Path:
        return self._xlsx

    def run(self) -> None:
        """Runs the export."""
        log.info("Exporting bill of material from catia.")

        # The external_xls_path should be validated from the input,
        # so we don't do it here again. Maybe change that?
        if self.external_xls_path:
            self._xls = self.external_xls_path
        else:
            self._xls = Path(
                export_bom(
                    product=self.doc_helper.document.product,
                    filename=file_utility.get_random_filename(filetype="xls"),
                    folder=self.export_root_path,
                )
            )
            file_utility.add_delete(path=self._xls, ask_retry=True)

        self._xlsx = self._convert_xls_to_xlsx(xls_path=self._xls)
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
