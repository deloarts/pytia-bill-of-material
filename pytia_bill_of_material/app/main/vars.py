"""
    The variables submodule for the app.
"""
from dataclasses import dataclass
from tkinter import BooleanVar, DoubleVar, StringVar, Tk

from models.bom import BOM
from models.report import Report


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
    docket_export_path: StringVar
    drawing_export_path: StringVar
    stp_export_path: StringVar
    stl_export_path: StringVar
    jpg_export_path: StringVar

    # Export variables
    export_docket: BooleanVar
    export_drawing: BooleanVar
    export_stp: BooleanVar
    export_stl: BooleanVar
    export_jpg: BooleanVar

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
        self.drawing_export_path = StringVar(master=root, name="drawing_export_path")
        self.docket_export_path = StringVar(master=root, name="docket_export_path")
        self.stp_export_path = StringVar(master=root, name="stp_export_path")
        self.stl_export_path = StringVar(master=root, name="stl_export_path")
        self.jpg_export_path = StringVar(master=root, name="jpg_export_path")

        self.export_docket = BooleanVar(master=root, name="export_docket")
        self.export_drawing = BooleanVar(master=root, name="export_drawing")
        self.export_stp = BooleanVar(master=root, name="export_stp")
        self.export_stl = BooleanVar(master=root, name="export_stl")
        self.export_jpg = BooleanVar(master=root, name="export_jpg")

        self.progress = DoubleVar(master=root, name="progress", value=0)

        self.show_report = BooleanVar(master=root, name="show_report", value=False)
