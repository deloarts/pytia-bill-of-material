"""
    Generates a report from the BOM object.
"""

import re

from const import Status
from models.bom import BOM
from models.report import Report
from models.report import ReportItem
from protocols.task_protocol import TaskProtocol
from pytia.log import log
from pytia_ui_tools.handlers.workspace_handler import Workspace
from resources import resource


class MakeReportTask(TaskProtocol):
    """
    Generates the report for the exported bill of material.

    Args:
        TaskProtocol (_type_): The task runner protocol.

    Raises:
            KeyError: Raised when a condition key is not in the BOM header items.
            TypeError: Raised when a condition value of the filters.json is neither `dict` nor `bool`.
            ValueError: Raised when the property_name value of the filters.json is not in the BOM \
                header items.
    """

    __slots__ = ("_bom", "_report", "_status")

    def __init__(self, bom: BOM, workspace: Workspace) -> None:
        self._workspace = workspace
        self._bom = bom

    @property
    def report(self) -> Report:
        return self._report

    @property
    def status(self) -> Status:
        return self._status

    def run(self) -> None:
        """Runs the task."""
        log.info("Creating report.")

        self._report = self._generate_report(bom=self._bom, workspace=self._workspace)
        self._status = self._report.status

    @staticmethod
    def _generate_report(bom: BOM, workspace: Workspace) -> Report:
        """
        Verifies the BOM model against the criteria of the filters.json.
        The verification is only performed if the conditions of the filters.json are met.
        The report will be created for the `assemblies` items of the given BOM object, because the
        `summary` item doesn't contain all items of the total assembly (Non-empty Product won't show 
        up in the summary).

        Args:
            bom (BOM): The BOM object to verify.

        Raises:
            KeyError: Raised when a condition key is not in the BOM header items.
            TypeError: Raised when a condition value of the filters.json is neither `dict` nor `bool`.
            ValueError: Raised when the property_name value of the filters.json is not in the BOM \
                header items.

        Returns:
            Report: The report object.
        """
        log.info("Verifying bill of material.")

        report = Report()

        for assembly in bom.assemblies:
            log.info(f"Verifying element {assembly.partnumber!r}:")

            for assembly_item in assembly.items:
                log.info(f"  {assembly_item.partnumber}")
                report_item = ReportItem(
                    partnumber=assembly_item.partnumber,
                    path=assembly_item.path,
                    parent_partnumber=assembly.partnumber,
                    parent_path=assembly.path,
                )

                for filter_element in resource.filters:
                    if not filter_element._enabled:
                        raise ValueError(
                            f"Filter element {filter_element.property_name} is not "
                            "setup correctly: '_enabled' is None."
                        )

                    if filter_element.property_name in assembly_item.properties:
                        conditions_satisfied = []
                        conditions_satisfied.append(filter_element._enabled.get())

                        if isinstance((cond_item := filter_element.condition), bool):
                            conditions_satisfied.append(cond_item)

                        elif isinstance(cond_item, dict):
                            for cond_key in cond_item:
                                if not cond_key in assembly_item.properties:
                                    raise KeyError(
                                        f"Condition key {cond_key!r} is not available in the BOM properties."
                                    )

                                if assembly_item.properties[cond_key] == cond_item[cond_key]:
                                    conditions_satisfied.append(True)
                                else:
                                    conditions_satisfied.append(False)

                        else:
                            raise TypeError(
                                f"Type of conditions ({type(cond_item)}) not valid, must be 'bool' or 'dict'."
                            )

                        if all(conditions_satisfied):
                            if assembly_item.properties[filter_element.property_name] is not None:
                                if filter_element.criteria.startswith("%WS:"):
                                    workspace_element = filter_element.criteria.split("%WS:")[-1]
                                    workspace_dict = workspace.elements.__dict__
                                    if (
                                        workspace.available
                                        and workspace_element in workspace_dict
                                        and assembly_item.properties[filter_element.property_name]
                                        == workspace_dict[workspace_element]
                                    ):
                                        report_item.details[filter_element.name] = Status.OK
                                        log.debug(f"    - {filter_element.name}: OK.")
                                    else:

                                        report_item.details[filter_element.name] = Status.FAILED
                                        report_item.status = Status.FAILED
                                        report.status = Status.FAILED
                                        log.debug(f"    - {filter_element.name}: FAILED.")

                                elif re.match(
                                    filter_element.criteria,
                                    str(assembly_item.properties[filter_element.property_name]),
                                ):
                                    report_item.details[filter_element.name] = Status.OK
                                    log.debug(f"    - {filter_element.name}: OK.")

                                else:
                                    report_item.details[filter_element.name] = Status.FAILED
                                    report_item.status = Status.FAILED
                                    report.status = Status.FAILED
                                    log.debug(f"    - {filter_element.name}: FAILED.")

                            else:
                                report_item.details[filter_element.name] = Status.FAILED
                                report_item.status = Status.FAILED
                                report.status = Status.FAILED
                                log.debug(f"    - {filter_element.name}: FAILED.")
                        else:
                            report_item.details[filter_element.name] = Status.SKIPPED
                            log.debug(f"    - {filter_element.name}: SKIPPED.")

                    else:
                        raise ValueError(f"Item {filter_element.property_name!r} not in BOM.")
                report.items.append(report_item)
        return report
