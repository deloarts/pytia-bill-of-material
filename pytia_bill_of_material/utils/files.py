"""
    File utility submodule.
"""

import atexit
import os
import shutil
from pathlib import Path
from tkinter import messagebox as tkmsg
from typing import List, Optional

from models.files import FileUtilityDeleteModel, FileUtilityMoveModel
from pytia.log import log
from resources import resource


class FileUtility:
    """
    The FileUtility class. Provides methods for deleting and moving files and some other
    useful file related functions.
    """

    def __init__(self) -> None:
        """Inits the FileUtility class."""
        self._delete_list: List[FileUtilityDeleteModel] = []
        self._move_list: List[FileUtilityMoveModel] = []

        atexit.register(self.delete_all_exit)

    @property
    def delete_items(self) -> List[FileUtilityDeleteModel]:
        """Returns a list of all files that should be deleted as FileUtilityDeleteModel."""
        return self._delete_list

    @property
    def move_items(self) -> List[FileUtilityMoveModel]:
        """Returns a list of all files that should be moved as FileUtilityMoveModel."""
        return self._move_list

    @property
    def all_moved(self) -> bool:
        """Returns True if all files have been moved."""
        for item in self._move_list:
            if not item.moved:
                return False
        return True

    @property
    def all_deleted(self) -> bool:
        """Returns True if all files have been deleted."""
        for item in self._delete_list:
            if not item.deleted:
                return False
        return True

    def delete_item(self, item: FileUtilityDeleteModel) -> None:
        """
        Deletes the given item from the list of delete-items.

        Args:
            item (FileUtilityDeleteModel): The file to delete.
        """
        while os.path.exists(item.path) and not item.deleted and not item.skipped:
            try:
                os.remove(item.path)
                item.deleted = True
                log.info(f"Deleted file at {str(item.path)!r}")
            except PermissionError:
                if item.ask_retry and not item.skip_silent:
                    if tkmsg.askretrycancel(
                        title=resource.settings.title,
                        message=(
                            f"The file with the name {item.path.name!r} at the location "
                            f"{str(item.path)!r} cannot be deleted, because it is opened "
                            "by another user or process.\n\n"
                            f"Do you want to retry deleting this file?\n\n"
                            f"If you click 'Retry' you have to make sure that the existing file "
                            "is not blocked by another user or process anymore."
                        ),
                    ):
                        continue

                elif not item.skip_silent:
                    tkmsg.showwarning(
                        title=resource.settings.title,
                        message=(
                            f"The file with the name {item.path.name!r} at the location "
                            f"{str(item.path)!r} cannot be deleted, because it is opened "
                            "by another user or process.\n\n"
                            "Deleting this file will be skipped."
                        ),
                    )

                item.skipped = True
                log.warning(
                    f"Skipped deleting file at {str(item.path)!r}: Not enough permission."
                )
                return

    def move_item(self, item: FileUtilityMoveModel) -> None:
        """
        Moves the given item from the list of move-items.

        Args:
            item (FileUtilityDeleteModel): The file to move.
        """
        # TODO: Add option to move as 'file (new)' if cannot be moved due to permission error.
        if not item.moved and not item.skipped:
            while os.path.exists(item.target):
                if item.delete_existing:
                    try:
                        os.remove(item.target)
                        log.info(f"Deleted existing file at {str(item.target)!r}")
                        break
                    except PermissionError:
                        if item.ask_retry:
                            if tkmsg.askretrycancel(
                                title=resource.settings.title,
                                message=(
                                    f"Cannot move file, because a file with the name "
                                    f"{item.target.name!r} already exists at {str(item.target.parent)!r}, "
                                    "but cannot be overwritten, because it is opened by another "
                                    "user or process.\n\n"
                                    "Do you want to retry moving file?\n\n"
                                    "If you click 'Retry' you have to make sure that the "
                                    "existing file is not blocked by another user or "
                                    "process anymore."
                                ),
                            ):
                                continue
                item.skipped = True
                log.warning(
                    f"Skipped moving file from {str(item.source)!r} to {str(item.target)!r}."
                    "\n\nThe target file already exists and cannot be deleted, because it is "
                    "blocked by another user or process."
                )
                if item.delete_skipped:
                    os.remove(item.source)
                    log.info(f"Deleted skipped file {str(item.source)!r}.")
                return

            shutil.move(item.source, item.target)
            item.moved = True
            log.info(f"Moved file from {str(item.source)!r} to {str(item.target)!r}.")

    def add_delete(
        self,
        path: Path,
        ask_retry: bool = True,
        skip_silent: bool = False,
        at_exit: bool = False,
    ) -> None:
        """
        Adds a file to delete later.

        Args:
            path (Path): The path of the file to delete.
            ask_retry (bool, optional): The user will be asked for retrying if the file cannot be \
                deleted due to a permission error. Defaults to True.
            skip_silent (bool, optional): Skips without a user prompt if the file cannot be \
                deleted. Defaults to False.
            at_exit (bool, optional): Deletes the file only at application exit. Defaults to False.
        """
        if not path.is_file():
            log.error(f"Cannot delete file at {str(path)!r}: Not a file.")
            return

        item = FileUtilityDeleteModel(
            path=path, ask_retry=ask_retry, skip_silent=skip_silent, at_exit=at_exit
        )
        self._delete_list.append(item)

    def add_move(
        self,
        source: Path,
        target: Path,
        delete_existing: bool = True,
        ask_retry: bool = True,
        delete_skipped: bool = True,
    ) -> None:
        """
        Adds a file to move later.

        Args:
            source (Path): The path of the file to move.
            target (Path): The path where the file should be moved.
            delete_existing (bool, optional): An existing file at the target location will be \
                deleted before moving. Defaults to True.
            ask_retry (bool, optional): The user will be asked for retrying if the file at the \
                target location cannot be deleted due to a permission error. Defaults to True.
            delete_skipped (bool, optional): Deletes all skipped files at the source location. \
                Defaults to True.
        """
        if not source.is_file():
            log.error(f"Cannot move file at {str(source)!r}: Not a file.")
            return

        item = FileUtilityMoveModel(
            source=source,
            target=target,
            delete_existing=delete_existing,
            ask_retry=ask_retry,
            delete_skipped=delete_skipped,
        )
        self._move_list.append(item)

    def delete_all_exit(self) -> None:
        """Deletes all file, including those marked as 'delete at exit'."""
        for item in self._delete_list:
            self.delete_item(item)

    def delete_all(self) -> None:
        """Deletes all files, except those marked as 'delete at exit'."""
        for item in self._delete_list:
            if not item.at_exit:
                self.delete_item(item)

    def move_all(self) -> None:
        """Moves all files."""
        for item in self._move_list:
            self.move_item(item)

    @staticmethod
    def get_random_filename(
        prefix: Optional[str] = None, filetype: Optional[str] = None
    ) -> str:
        """
        Returns a random filename.

        Args:
            prefix (Optional[str], optional): A prefix for the filename. Defaults to None.
            filetype (Optional[str], optional): The filetype. Defaults to None. Can be something \
                like `.xls` or `xls`. If set to `None` only a random name will be returned.

        Returns:
            str: A random filename as string.
        """
        if filetype and not filetype.startswith("."):
            filetype = "." + filetype
        if prefix is None:
            prefix = ""
        if filetype is None:
            filetype = ""

        return f"{prefix}{os.urandom(24).hex()}{filetype}"


file_utility = FileUtility()
