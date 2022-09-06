"""
    Generates a report from the BOM object.
"""

import re

from const import Status
from models.bom import BOM
from models.report import Report, ReportItem
from pytia.log import log
from resources import resource
from protocols.task_protocol import TaskProtocol


class MakeReportTask(TaskProtocol):
    __slots__ = ("_bom", "_report", "_status")

    def __init__(self, bom: BOM) -> None:
        self._bom = bom

    @property
    def report(self) -> Report:
        return self._report

    @property
    def status(self) -> Status:
        return self._status

    def run(self) -> None:
        log.info("Creating report.")

        self._report = self._generate_report(bom=self._bom)
        self._status = self._report.status

    @staticmethod
    def _generate_report(bom: BOM) -> Report:
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
                log.info(f"  {assembly_item.partnumber}:")
                report_item = ReportItem(
                    partnumber=assembly_item.partnumber,
                    path=assembly_item.path,
                    parent_path=assembly.path,
                )

                for filter_item in resource.filters:
                    if filter_item.property_name in assembly_item.properties:
                        conditions_satisfied = []

                        if isinstance((cond_item := filter_item.condition), bool):
                            conditions_satisfied.append(cond_item)

                        elif isinstance(cond_item, dict):
                            for cond_key in cond_item:
                                if not cond_key in assembly_item.properties:
                                    raise KeyError(
                                        f"Condition key {cond_key!r} is not available in the BOM properties."
                                    )

                                if (
                                    assembly_item.properties[cond_key]
                                    == cond_item[cond_key]
                                ):
                                    conditions_satisfied.append(True)
                                else:
                                    conditions_satisfied.append(False)

                        else:
                            raise TypeError(
                                f"Type of conditions ({type(cond_item)}) not valid, "
                                "must be 'bool' or 'dict'."
                            )

                        if all(conditions_satisfied):
                            if assembly_item.properties[
                                filter_item.property_name
                            ] is not None and re.match(
                                filter_item.criteria,
                                str(
                                    assembly_item.properties[filter_item.property_name]
                                ),
                            ):
                                report_item.details[
                                    filter_item.property_name
                                ] = Status.OK
                                log.info(f"    - {filter_item.property_name}: OK.")
                            else:
                                report_item.details[
                                    filter_item.property_name
                                ] = Status.FAILED
                                report_item.status = Status.FAILED
                                report.status = Status.FAILED
                                log.info(f"    - {filter_item.property_name}: FAILED.")
                        else:
                            report_item.details[
                                filter_item.property_name
                            ] = Status.SKIPPED
                            log.info(f"    - {filter_item.property_name}: SKIPPED.")

                    else:
                        raise ValueError(
                            f"Item {filter_item.property_name!r} not in BOM."
                        )

                report.items.append(report_item)
        return report
