"""
    Export submodule. Holds utility functions for handling data exports.
"""
from pathlib import Path
from typing import Literal

from const import LOGON, PROP_DRAWING_PATH, TEMP_EXPORT
from pytia.exceptions import PytiaFileOperationError
from pytia.log import log
from pytia.utilities.docket import (
    DocketConfig,
    create_docket_from_template,
    export_docket_as_pdf,
)
from pytia.wrapper.documents.drawing_documents import PyDrawingDocument
from pytia.wrapper.documents.part_documents import PyPartDocument
from pytia.wrapper.documents.product_documents import PyProductDocument
from resources import resource
from templates import templates

from utils.files import file_utility


def export_docket(
    filename: str,
    folder: Path,
    document: PyProductDocument | PyPartDocument,
    config: DocketConfig,
    **kwargs,
) -> None:
    """
    Exports the docket into a PDF file. The docket will be exported into the temp folder and moved
    after the main task has finished.

    Args:
        filename (str): The filename of the docket pdf.
        folder (Path): The folder into which the pdf will be exported.
        document (PyPartDocument | PyProductDocument): The part or product document from which \
            to create the docket
        config (DocketConfig): The docket configuration object.

        kwargs: Keyword arguments will be added to the docket for text elements which names are \
            prefixed with `arg.`. Example: To add the quantity to the docket text \
            element with the name 'arg.quantity' you have to supply the argument `quantity=1`.

    Raises:
        PytiaFileOperationError: Raised if the given folder isn't valid.
    """
    if ".pdf" not in filename:
        filename += ".pdf"

    if templates.docket_path is None:
        raise PytiaFileOperationError("Cannot export docket, given folder is None.")

    # Translate creator username
    if document.properties.exists(resource.props.creator):
        if (
            resource.user_exists(
                creator_logon := document.properties.get_by_name(
                    resource.props.creator
                ).value
            )
            and resource.settings.export.apply_username_in_docket
        ):
            creator = resource.get_user_by_logon(creator_logon).name
        else:
            creator = creator_logon
    else:
        creator = "Unknown"

    # Translate modifier username
    if document.properties.exists(resource.props.modifier):
        if (
            resource.user_exists(
                modifier_logon := document.properties.get_by_name(
                    resource.props.modifier
                ).value
            )
            and resource.settings.export.apply_username_in_docket
        ):
            modifier = resource.get_user_by_logon(modifier_logon).name
        else:
            modifier = modifier_logon
    else:
        modifier = "Unknown"

    # Translate publisher username
    if (
        resource.user_exists(LOGON)
        and resource.settings.export.apply_username_in_docket
    ):
        publisher = resource.get_user_by_logon(LOGON).name
    else:
        publisher = LOGON

    docket = create_docket_from_template(
        template=templates.docket_path,
        document=document,
        config=config,
        hide_unknown_properties=True,
        creator=creator,
        modifier=modifier,
        publisher=publisher,
        **kwargs,
    )
    export_path = export_docket_as_pdf(
        docket=docket,
        name=file_utility.get_random_filename(filetype="pdf"),
        folder=TEMP_EXPORT,
    )
    target_path = Path(folder, filename)
    file_utility.add_move(
        source=Path(export_path),
        target=target_path,
        delete_existing=True,
        ask_retry=True,
    )


def export_drawing(
    filename: str,
    folder: Path,
    document: PyProductDocument | PyPartDocument,
) -> None:
    """
    Exports the drawing into a pdf and dxf file. The files will be exported into the temp folder
    and moved after the main task has finished.

    This export only works if the 'pytia.drawing_path' property is set and valid. This property
    is created when using the https://github.com/deloarts/pytia-title-block app.

    Args:
        filename (str): The filename of the pdf and dxf files.
        folder (Path): The folder into which the data will be exported.
        document (PyProductDocument | PyPartDocument): The document from which to export the data.
    """
    if document.properties.exists(PROP_DRAWING_PATH):
        drawing_path = Path(document.properties.get_by_name(PROP_DRAWING_PATH).value)
        if drawing_path.exists():
            pdf_export_path = Path(
                TEMP_EXPORT, file_utility.get_random_filename(filetype="pdf")
            )
            pdf_target_path = Path(folder, filename + ".pdf")
            dxf_export_path = Path(
                TEMP_EXPORT, file_utility.get_random_filename(filetype="dxf")
            )
            dxf_target_path = Path(folder, filename + ".dxf")

            with PyDrawingDocument() as drawing_document:
                drawing_document.open(drawing_path)
                drawing_document.drawing_document.export_data(
                    pdf_export_path, "pdf", overwrite=True
                )
                drawing_document.drawing_document.export_data(
                    dxf_export_path, "dxf", overwrite=True
                )

            file_utility.add_move(
                source=pdf_export_path,
                target=pdf_target_path,
                delete_existing=True,
                ask_retry=True,
            )
            file_utility.add_move(
                source=dxf_export_path,
                target=dxf_target_path,
                delete_existing=True,
                ask_retry=True,
            )
        else:
            log.error(
                f"Skipped drawing export of {document.document.name!r}: Path not valid."
            )
    else:
        log.info(f"Skipped drawing export of {document.document.name!r}: Path not set.")


def _export_stp_stl(
    filetype: Literal["stp", "stl"],
    filename: str,
    folder: Path,
    document: PyProductDocument | PyPartDocument,
) -> None:
    """
    Exports the data into a file. The file will be exported into the temp folder and moved
    after the main task has finished.

    Args:
        filetype (str): The type of the file to be exported (stp or stl).
        filename (str): The filename of the file.
        folder (Path): The folder into which the data will be exported.
        document (PyProductDocument | PyPartDocument): The document from which to export the data.
    """
    if filetype not in filename:
        filename += f".{filetype}"

    export_path = Path(TEMP_EXPORT, file_utility.get_random_filename(filetype=filetype))
    target_path = Path(folder, filename)

    document.document.export_data(
        file_name=export_path, file_type=filetype, overwrite=True
    )
    file_utility.add_move(
        source=export_path,
        target=target_path,
        delete_existing=True,
        ask_retry=True,
    )


def export_stp(
    filename: str,
    folder: Path,
    document: PyProductDocument | PyPartDocument,
) -> None:
    """
    Exports the data into a stp file. The file will be exported into the temp folder and moved
    after the main task has finished.

    Args:
        filename (str): The filename of the stp file.
        folder (Path): The folder into which the data will be exported.
        document (PyProductDocument | PyPartDocument): The document from which to export the stp.
    """
    _export_stp_stl(filetype="stp", filename=filename, folder=folder, document=document)


def export_stl(
    filename: str,
    folder: Path,
    document: PyPartDocument,
) -> None:
    """
    Exports the data into a stl file. The file will be exported into the temp folder and moved
    after the main task has finished.

    Args:
        filename (str): The filename of the stl file.
        folder (Path): The folder into which the data will be exported.
        document (PyProductDocument | PyPartDocument): The document from which to export the stl.
    """
    _export_stp_stl(filetype="stl", filename=filename, folder=folder, document=document)
