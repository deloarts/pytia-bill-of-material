"""
    Helper functions for messages.
"""

from const import STYLES
from pytia.log import log
from resources import resource
from ttkbootstrap import Menu
from ttkbootstrap import Style


def set_appearance_menu(appearance_menu: Menu) -> None:
    """Binds all callbacks to the appearance menubar."""
    for index, _ in enumerate(STYLES):
        appearance_menu.entryconfig(index, command=lambda x=index: change_theme(x))


def change_theme(index: int) -> None:
    """Changes the apps theme.

    Args:
        index (int): The index of the theme from the STYLES list.
    """
    theme_name = STYLES[index]
    Style(theme=theme_name)
    resource.appdata.theme = theme_name
    log.info(f"Changed theme to {theme_name} ({index}).")
