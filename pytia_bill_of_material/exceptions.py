"""
    Submodule for exceptions.
"""

from pytia.exceptions import PytiaBaseError


class PytiaLanguageNotSupportedError(PytiaBaseError):
    """Exception when the UI language is not supported."""


class PytiaDispatchError(PytiaBaseError):
    """Exception when the dispatch failed."""


class PytiaNotInstalledError(PytiaBaseError):
    """Exception for not installed dependencies or software."""


class PytiaAbortedByUserError(PytiaBaseError):
    """Exception for user abortions."""


class PytiaConvertError(PytiaBaseError):
    """Exception when converting fails."""
