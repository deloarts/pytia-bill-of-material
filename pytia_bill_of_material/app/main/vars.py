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
    bom: BOM
    report: Report
    initial_filepath: str

    # Infrastructure variables
    project: StringVar
    machine: StringVar

    # Path variables
    bom_export_path: StringVar
    docket_export_path: StringVar
    stp_export_path: StringVar
    stl_export_path: StringVar

    # Export variables
    export_docket: BooleanVar
    export_stp: BooleanVar
    export_stl: BooleanVar

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
        self.docket_export_path = StringVar(master=root, name="docket_export_path")
        self.stp_export_path = StringVar(master=root, name="stp_export_path")
        self.stl_export_path = StringVar(master=root, name="stl_export_path")

        self.export_docket = BooleanVar(master=root, name="export_docket")
        self.export_stp = BooleanVar(master=root, name="export_stp")
        self.export_stl = BooleanVar(master=root, name="export_stl")

        self.progress = DoubleVar(master=root, name="progress", value=0)

        self.show_report = BooleanVar(master=root, name="show_report", value=False)
