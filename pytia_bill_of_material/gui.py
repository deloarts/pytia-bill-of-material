"""
    The GUI for the application.
"""

import tkinter as tk


class GUI(tk.Tk):
    """The user interface of the app."""

    def __init__(self) -> None:
        tk.Tk.__init__(self)

    def run(self) -> None:
        """Run the app."""
        self.after(100, self.run_controller)
        self.mainloop()

    def run_controller(self) -> None:
        """Runs all controllers. Initializes all lazy loaders."""
