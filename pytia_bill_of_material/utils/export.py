"""
    Export submodule. Holds utility functions for handling data exports.
"""
from pathlib import Path
from typing import List
from typing import Literal
from typing import Tuple

from const import LOGON
from const import PROP_DRAWING_PATH
from pycatia import catia
from pycatia.enumeration.enumeration_types import cat_capture_format
from pycatia.enumeration.enumeration_types import cat_specs_and_geom_window_layout
from pycatia.in_interfaces.specs_and_geom_window import SpecsAndGeomWindow
from pytia.exceptions import PytiaFileOperationError
from pytia.log import log
from pytia.utilities.docket import DocketConfig
from pytia.utilities.docket import create_docket_from_template
from pytia.utilities.docket import export_docket_as_pdf
from pytia.wrapper.documents.drawing_documents import PyDrawingDocument
from pytia.wrapper.documents.part_documents import PyPartDocument
from pytia.wrapper.documents.product_documents import PyProductDocument
from resources import resource
from resources.utils import expand_env_vars


def export_docket(
    docket_template: Path | None,
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
        docket_template (Path): The path to the template CATDrawing file.
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

    if docket_template is None:
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
        template=docket_template,
        document=document,
        config=config,
        hide_unknown_properties=True,
        creator=creator,
        modifier=modifier,
        publisher=publisher,
        **kwargs,
    )
    export_docket_as_pdf(
        docket=docket,
        name=filename,
        folder=folder,
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
        drawing_path = Path(
            expand_env_vars(document.properties.get_by_name(PROP_DRAWING_PATH).value)
        )
        if drawing_path.exists():
            pdf_target_path = Path(folder, filename + ".pdf")
            dxf_target_path = Path(folder, filename + ".dxf")

            with PyDrawingDocument() as drawing_document:
                drawing_document.open(drawing_path)
                drawing_document.drawing_document.export_data(
                    pdf_target_path, "pdf", overwrite=True
                )
                drawing_document.drawing_document.export_data(
                    dxf_target_path, "dxf", overwrite=True
                )
                if resource.settings.export.lock_drawing_views:
                    sheets = drawing_document.drawing_document.sheets
                    for i_sheet in range(1, sheets.count + 1):
                        sheet = sheets.item(i_sheet)
                        for i_view in range(3, sheet.views.count + 1):
                            view = sheet.views.item(i_view)
                            view.lock_status = True
                            log.info(
                                f"Locked view {view.name!r} of sheet {sheet.name!r}."
                            )
                    drawing_document.save()
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

    document.document.export_data(
        file_name=Path(folder, filename), file_type=filetype, overwrite=True
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


def export_jpg(
    filename: str,
    folder: Path,
    views: List[Tuple[float, float, float]],
    bg: Tuple[float, float, float] | None = None,
) -> None:
    """
    Exports the open document as JPG.

    Args:
        filename (str): The filename of the jpg file.
        folder (Path): The folder into which the data will be exported.
        views (tuple): The views from which to export the jpg. Value range is from 0-1.
        bg (tuple): Changes the background to the given RGB-color. \
            Value range is from 0-1, Resets the background after export. \
            Doesn't change the background if value is None. Defaults to None.
    """
    active_window = catia().active_window
    active_viewer = active_window.active_viewer

    # Save the current screen state
    current_fs = active_viewer.full_screen
    active_viewer.full_screen = True

    # Save current background color
    current_bg_color = active_viewer.get_background_color()
    if bg is not None:
        active_viewer.put_background_color(bg)

    # Hide the tree
    specs_and_geom = SpecsAndGeomWindow(active_window.com_object)
    specs_and_geom.layout = cat_specs_and_geom_window_layout.index("catWindowGeomOnly")

    view_point_3D = active_viewer.create_viewer_3d().viewpoint_3d
    for index, view in enumerate(views):
        export_path = Path(
            folder,
            filename
            + f"{' (View ' + str(index+1) + ')' if len(views) > 1 else ''}.jpg",
        )
        log.debug(f"Exporting view {index} of {filename} to {export_path}...")

        view_point_3D.put_sight_direction(view)  # type: ignore
        active_viewer.update()
        active_viewer.reframe()  # Equivalent to "fit all in"
        # active_viewer.zoom_in()
        active_viewer.capture_to_file(
            cat_capture_format.index("catCaptureFormatJPEG"), str(export_path)
        )

    # Reset background and show tree
    active_viewer.full_screen = current_fs
    active_viewer.put_background_color(current_bg_color)  # type: ignore
    specs_and_geom.layout = cat_specs_and_geom_window_layout.index(
        "catWindowSpecsAndGeom"
    )
