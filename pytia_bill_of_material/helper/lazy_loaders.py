"""
    Lazy loader for the UI.
"""

import functools
import os
import time
from pathlib import Path
from typing import List
from typing import Optional

from pytia.exceptions import PytiaDifferentDocumentError
from pytia.exceptions import PytiaDocumentNotSavedError
from pytia.log import log
from resources import resource
from utils.language import get_ui_language


class LazyDocumentHelper:
    """
    Helper class for late imports of any kind of methods related to handle document operations.

    Important: This class loads the current document only once (on instantiation). If the
    document changes all operations will be made on the original document.

    Use the ensure_doc_not_changed method if you're not sure if the part hasn't changed.
    """

    def __init__(self) -> None:
        # Import the PyProductDocument after the GUI exception handler is initialized.
        # Otherwise the CATIA-not-running-exception will not be caught.
        # Also: The UI will load a little bit faster.

        start_time = time.perf_counter()
        # pylint: disable=C0415
        from pytia.framework import framework
        from pytia.wrapper.documents.product_documents import PyProductDocument

        # pylint: enable=C0415

        self.framework = framework
        self.document = PyProductDocument(strict_naming=False)
        self.document.current()
        self.document.product.part_number = self.document.document.name.split(".CATProduct")[0]
        self.name = self.document.document.name
        resource.apply_language(get_ui_language(self.document))  # type: ignore

        if not resource.settings.restrictions.allow_unsaved and not os.path.isabs(self.document.document.full_name):
            raise PytiaDocumentNotSavedError(
                "It is not allowed to export the bill of material of an unsaved document. "
                "Please save the document first."
            )

        end_time = time.perf_counter()
        log.debug(f"Loaded document in {(end_time-start_time):.4f}s")

    @property
    def path(self) -> Path:
        """Returns the documents absolute path with filename and file extension."""
        return Path(self.document.document.full_name)

    @property
    def partnumber(self) -> str:
        """Returns the part number of the document."""
        return self.document.product.part_number

    @property
    def definition(self) -> str:
        """Returns the definition of the document."""
        return self.document.product.definition

    @definition.setter
    def definition(self, value: str) -> None:
        """Sets the definition value of the document."""
        self.document.product.definition = value

    @property
    def revision(self) -> str:
        """Returns the revision of the document."""
        return self.document.product.revision

    @revision.setter
    def revision(self, value: str) -> None:
        """Sets the revision value of the document."""
        self.document.product.revision = value

    @property
    def nomenclature(self) -> str:
        """Returns the nomenclature of the document"""
        return self.document.product.nomenclature

    @nomenclature.setter
    def nomenclature(self, value: str) -> None:
        """Sets the nomenclature value of the document."""
        self.document.product.nomenclature = value

    @property
    def source(self) -> int:
        """Returns the source of the document."""
        return self.document.product.source

    @source.setter
    def source(self, value: int) -> None:
        """Sets the source value of the document."""
        self.document.product.source = value

    @property
    def description(self) -> str:
        """Returns the description of the document"""
        return self.document.product.description_reference

    @description.setter
    def description(self, value: str) -> None:
        """Returns the description value of the document."""
        self.document.product.description_reference = value

    def _lock_catia(self, value: bool) -> None:
        """
        Sets the lock-state of catia.

        Args:
            value (bool): True: Locks the catia UI, False: Releases the lock.
        """
        log.debug(f"Setting catia lock to {value!r}")
        self.framework.catia.refresh_display = not value
        self.framework.catia.interactive = not value
        self.framework.catia.display_file_alerts = value
        self.framework.catia.undo_redo_lock = value
        if value:
            self.framework.catia.disable_new_undo_redo_transaction()
        else:
            self.framework.catia.enable_new_undo_redo_transaction()

    def _doc_changed(self) -> bool:
        """Returns True if the current part document has changed, False if not."""
        part_document = self.document
        part_document.current()
        log.warning(f"The document has changed: {part_document.document.name} -> {self.name}")
        return part_document.document.name != self.name

    @staticmethod
    def _ensure_doc_not_changed(func):
        """
        Ensures that the document hasn't changed.
        Raises the PytiaDifferentDocumentError if the document has changed.
        """

        # pylint: disable=W0212
        # pylint: disable=R1710
        @functools.wraps(func)
        def _ensure_part_not_changed_wrapper(self, *args, **kwargs):
            if self._doc_changed():
                document = self.document
                document.current()
                raise PytiaDifferentDocumentError(
                    f"The name of the current document has changed:\n"
                    f" - Original was {self.name}\n"
                    f" - Current is {document.document.name}"
                )
            return func(self, *args, **kwargs)

        return _ensure_part_not_changed_wrapper
        # pylint: enable=W0212
        # pylint: enable=R1710

    def get_property(self, name: str) -> Optional[str]:
        """
        Retrieves a properties value from the documents properties.

        Args:
            name (str): The name of the property to retrieve the value from.

        Returns:
            Optional[str]: The value of the property as string. Returns None, if the property \
                doesn't exists.
        """
        if self.document.properties.exists(name):
            param = str(self.document.properties.get_by_name(name).value)
            log.info(f"Retrieved property {name} ({param}) from part.")
            return param
        log.info(f"Couldn't retrieve property {name} from part: Doesn't exists.")
        return None

    def get_all_open_documents(self) -> List[str]:
        """Returns a list of all open documents (document.name)"""
        open_documents: List[str] = []
        for i in range(1, self.framework.catia.documents.count + 1):
            open_documents.append(self.framework.catia.documents.item(i).name)
        return open_documents

    def close_all_documents(self) -> None:
        for doc in self.get_all_open_documents():
            try:
                self.framework.catia.documents.item(doc).close()
                log.info(f"Closed document {doc!r}.")
            except Exception:
                log.warning(f"Failed closing document {doc!r}: Maybe it has been already closed.")
