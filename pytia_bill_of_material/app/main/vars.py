"""
    The variables submodule for the app.
"""

from dataclasses import dataclass
from tkinter import BooleanVar
from tkinter import DoubleVar
from tkinter import StringVar
from tkinter import Tk

from models.report import Report
from resources import resource


@dataclass(slots=True, kw_only=True)
class Variables:
    """Dataclass for the main windows variables."""

    # Process variables
    report: Report

    # Infrastructure variables
    project: StringVar
    machine: StringVar

    # Path variables
    bom_export_path: StringVar
    documentation_export_path: StringVar
    docket_export_path: StringVar
    drawing_export_path: StringVar
    stp_export_path: StringVar
    stl_export_path: StringVar
    jpg_export_path: StringVar
    bundle_export_path: StringVar

    external_bom_path: StringVar

    # Export variables
    bundle: BooleanVar
    zip_bundle: BooleanVar
    bundle_by_prop: BooleanVar
    bundle_by_prop_txt: StringVar

    export_docket: BooleanVar
    export_documentation: BooleanVar
    export_drawing: BooleanVar
    export_stp: BooleanVar
    export_stl: BooleanVar
    export_jpg: BooleanVar

    ignore_prefix_txt: StringVar
    ignore_prefix: BooleanVar
    ignore_source_unknown: BooleanVar

    # Progress variables
    progress: DoubleVar

    # Trigger variables
    show_report: BooleanVar

    def __init__(self, root: Tk) -> None:
        """
        Inits the variables.

        Args:
            root (Tk): The main window.
        """

        self.project = StringVar(master=root, name="project")
        self.machine = StringVar(master=root, name="machine")

        self.bom_export_path = StringVar(master=root, name="bom_export_path")
        self.documentation_export_path = StringVar(
            master=root, name="documentation_export_path"
        )
        self.docket_export_path = StringVar(master=root, name="docket_export_path")
        self.drawing_export_path = StringVar(master=root, name="drawing_export_path")
        self.stp_export_path = StringVar(master=root, name="stp_export_path")
        self.stl_export_path = StringVar(master=root, name="stl_export_path")
        self.jpg_export_path = StringVar(master=root, name="jpg_export_path")
        self.bundle_export_path = StringVar(master=root, name="bundle_export_path")

        self.external_bom_path = StringVar(
            master=root, name="external_bom_path", value=""
        )

        self.bundle = BooleanVar(master=root, name="bundle", value=False)
        self.zip_bundle = BooleanVar(
            master=root, name="zip_bundle", value=resource.appdata.zip_bundle
        )
        self.bundle_by_prop = BooleanVar(
            master=root, name="bundle_by_prop", value=resource.appdata.bundle_by_prop
        )
        self.bundle_by_prop_txt = StringVar(
            master=root,
            name="bundle_by_prop_txt",
            value=resource.settings.export.bundle_by_prop,
        )

        self.export_documentation = BooleanVar(master=root, name="export_documentation")
        self.export_docket = BooleanVar(master=root, name="export_docket")
        self.export_drawing = BooleanVar(master=root, name="export_drawing")
        self.export_stp = BooleanVar(master=root, name="export_stp")
        self.export_stl = BooleanVar(master=root, name="export_stl")
        self.export_jpg = BooleanVar(master=root, name="export_jpg")

        self.ignore_prefix_txt = StringVar(master=root, name="ignore_prefix_txt")
        self.ignore_prefix = BooleanVar(master=root, name="ignore_prefix")
        self.ignore_source_unknown = BooleanVar(
            master=root, name="ignore_source_unknown"
        )

        self.progress = DoubleVar(master=root, name="progress", value=0)

        self.show_report = BooleanVar(master=root, name="show_report", value=False)
