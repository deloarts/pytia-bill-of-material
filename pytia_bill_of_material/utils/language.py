"""
    Submodule for language related functions.
"""

from typing import Literal

from pytia.exceptions import PytiaLanguageError
from pytia.framework import framework
from pytia.framework.in_interfaces.documentation_setting_att import (
    DocumentationSettingAtt,
)
from pytia.framework.product_structure_interfaces.product import Product
from pytia.log import log
from pytia.wrapper.documents.product_documents import PyProductDocument
from resources import resource


def get_ui_language(product: PyProductDocument) -> Literal["en", "de"]:
    """
    Returns the language of the CATIA UI.
    Reads the partnumber parameter from the product document. The name of this parameter
    changes depending on the language of the UI.

    This is not a good solution, but currently the only one that works.

    Raises:
        PytiaLanguageError: Raised when the UI language is not supported.

    Returns:
        Literal["en", "de"]: The language of the CATIA UI.
    """
    parameters = Product(product.product.com_object).parameters
    try:
        parameters.get_item(resource.keywords.en.partnumber)
        log.info("UI language is set to 'English'.")
        return "en"
    except:
        pass

    try:
        parameters.get_item(resource.keywords.de.partnumber)
        log.info("UI language is set to 'German'.")
        return "de"
    except:
        pass

    raise PytiaLanguageError(
        f"The selected language is not supported. "
        "Please select either 'English' or 'German'."
    )


def get_doc_language() -> Literal["en", "de"]:
    """
    Returns the language of the CATIA online documentation.

    Raises:
        PytiaLanguageError: Raised when the UI language is not supported.

    Returns:
        Literal["en", "de"]: The language of the CATIA doc.
    """
    settings_controller = framework.catia.setting_controllers()
    doc_settings_controller = DocumentationSettingAtt(
        settings_controller.item("CATCafDocumentationSettingCtrl").com_object
    )
    code = doc_settings_controller.doc_language

    match code:
        case 0:
            raise PytiaLanguageError(
                "Cannot proceed with language setting 'default'. "
                "Please select either 'English' or 'German'."
            )
        case 602:
            return "de"
        case 714:
            return "en"
        case _:
            raise PytiaLanguageError(
                f"The selected language {code!r} is not supported. "
                "Please select either 'English' or 'German'."
            )
