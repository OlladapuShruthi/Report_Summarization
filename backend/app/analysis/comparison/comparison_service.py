from typing import Any, Dict, List, Optional

from app.analysis.comparison.medical_catalog import CATALOG_STATUS, CATALOG_VERSION, normalize_label, normalize_unit, resolve_test_identity
from app.analysis.comparison.trend_detector import detect_trend


class ComparisonService:
    """Produces factual, report-to-report comparison data without diagnosis."""

    def build_context(
        self,
        current_parsed_json: Dict[str, Any],
        previous_reports: List[Dict[str, Any]],
        current_report_date: Optional[str] = None,
        current_report_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        current_parsed_json = current_parsed_json or {}
        current_labs = current_parsed_json.get("lab_results") or current_parsed_json.get("lab_facts") or []
        comparisons = []

        for current_lab in current_labs:
            if not isinstance(current_lab, dict):
                continue
            comparison = self._compare_lab(current_lab, previous_reports or [], current_report_date, current_report_id)
            if comparison:
                comparisons.append(comparison)

        current_identities = {
            self._comparison_key(lab)
            for lab in current_labs
            if isinstance(lab, dict) and self._comparison_key(lab)
        }
        comparisons.extend(
            self._missing_historical_findings(
                previous_reports or [],
                current_identities,
            )
        )
        finding_events = self._build_finding_events(comparisons)

        return {
            "catalog_version": CATALOG_VERSION,
            "catalog_status": CATALOG_STATUS,
            "history_available": bool(previous_reports),
            "previous_report_count": len(previous_reports),
            "comparisons": comparisons,
            "finding_events": finding_events,
        }

    @staticmethod
    def _build_finding_events(comparisons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        events = []
        for comparison in comparisons:
            finding_id = "|".join(
                value
                for value in (
                    comparison.get("canonical_test_name") or normalize_label(comparison.get("test_name")),
                    normalize_unit(comparison.get("unit")),
                )
                if value
            )
            for measurement in comparison.get("history") or []:
                events.append(
                    {
                        "finding_id": finding_id,
                        "test_name": comparison.get("test_name"),
                        "canonical_test_name": comparison.get("canonical_test_name"),
                        "unit": comparison.get("unit"),
                        "date": measurement.get("date"),
                        "report_id": measurement.get("report_id"),
                        "value": measurement.get("value"),
                        "status": measurement.get("status"),
                        "lifecycle_state": comparison.get("lifecycle_state", "UNKNOWN"),
                        "evidence_type": measurement.get("evidence_type", "LAB_REPORT"),
                        "is_current": bool(measurement.get("is_current")),
                    }
                )
        return events

    def _missing_historical_findings(
        self,
        previous_reports: List[Dict[str, Any]],
        current_identities: set[tuple[str, str]],
    ) -> List[Dict[str, Any]]:
        latest_by_identity: Dict[tuple[str, str], Dict[str, Any]] = {}
        for report in previous_reports:
            report_date = self._report_date(report)
            report_id = report.get("analysis_id") or report.get("report_id")
            parsed_json = report.get("parsed_json") or {}
            for lab in parsed_json.get("lab_results") or parsed_json.get("lab_facts") or []:
                key = self._comparison_key(lab)
                status = self._status(lab)
                if not key or status != "NORMAL":
                    if key and status:
                        latest_by_identity[key] = {
                            "test_name": lab.get("test_name"),
                            "unit": lab.get("unit"),
                            "value": self._numeric(lab.get("value")),
                            "status": status,
                            "date": report_date,
                            "report_id": report_id,
                            "reference_range": lab.get("reference_range"),
                        }

        missing = []
        for key, previous in latest_by_identity.items():
            if key in current_identities:
                continue
            missing.append(
                {
                    "test_name": previous["test_name"],
                    "unit": previous["unit"],
                    "canonical_test_name": key[0],
                    "catalog_id": None,
                    "comparison_method": "historical_measurement_not_present_current_report",
                    "history": [
                        {
                            "date": previous["date"],
                            "value": previous["value"],
                            "status": previous["status"],
                            "report_id": previous["report_id"],
                            "reference_range": previous["reference_range"],
                            "evidence_type": "LAB_REPORT",
                        }
                    ],
                    "previous_value": previous["value"],
                    "current_value": None,
                    "previous_status": previous["status"],
                    "current_status": "UNKNOWN",
                    "trend": "UNKNOWN",
                    "finding_status": "UNKNOWN",
                    "lifecycle_state": "UNKNOWN",
                    "uncertainty_reason": "measurement_not_present_in_current_report",
                }
            )
        return missing

    def _compare_lab(
        self,
        current_lab: Dict[str, Any],
        previous_reports: List[Dict[str, Any]],
        current_report_date: Optional[str],
        current_report_id: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        current_value = self._numeric(current_lab.get("value"))
        current_status = self._status(current_lab)
        if current_value is None or current_status is None:
            return None

        current_identity = resolve_test_identity(current_lab.get("test_name"), current_lab.get("unit"))

        history = []
        for report in previous_reports:
            parsed_json = report.get("parsed_json") or {}
            report_date = self._report_date(report)
            labs = parsed_json.get("lab_results") or parsed_json.get("lab_facts") or []
            for lab in labs:
                match = self._comparison_match(current_lab, lab, current_identity)
                if not match["comparable"]:
                    continue
                value = self._numeric(lab.get("value"))
                status = self._status(lab)
                if value is not None and status is not None:
                    history.append(
                        {
                            "date": report_date,
                            "value": value,
                            "status": status,
                            "report_id": report.get("analysis_id") or report.get("report_id"),
                            "evidence_type": "LAB_REPORT",
                        }
                    )

        history.sort(key=lambda item: item["date"])
        previous = history[-1] if history else None
        previous_value = previous["value"] if previous else None
        previous_status = previous["status"] if previous else None
        direction = detect_trend(previous_value, current_value)
        finding_status = self._finding_status(previous_status, current_status, previous_value, current_value)
        lifecycle_state = self._lifecycle_state(finding_status)

        return {
            "test_name": current_lab.get("test_name"),
            "unit": current_lab.get("unit"),
            "canonical_test_name": current_identity.canonical_name if current_identity else None,
            "catalog_id": current_identity.catalog_id if current_identity else None,
            "comparison_method": current_identity.matched_by if current_identity else "exact_normalized_label_and_unit",
            "history": history
            + [
                {
                    "date": current_report_date or "current",
                    "value": current_value,
                    "status": current_status,
                    "report_id": current_report_id,
                    "is_current": True,
                    "evidence_type": "LAB_REPORT",
                }
            ],
            "previous_value": previous_value,
            "current_value": current_value,
            "previous_status": previous_status,
            "current_status": current_status,
            "trend": direction,
            "finding_status": finding_status,
            "lifecycle_state": lifecycle_state,
            "evidence_type": "LAB_REPORT",
        }

    @staticmethod
    def _comparison_key(lab: Dict[str, Any]) -> Optional[tuple[str, str]]:
        identity = resolve_test_identity(lab.get("test_name"), lab.get("unit"))
        if identity:
            return identity.canonical_name, identity.canonical_unit
        name = normalize_label(lab.get("test_name"))
        unit = normalize_unit(lab.get("unit"))
        if not name or not unit:
            return None
        return name, unit

    @staticmethod
    def _comparison_match(
        current_lab: Dict[str, Any], historic_lab: Dict[str, Any], current_identity: Optional[Any]
    ) -> Dict[str, Any]:
        historic_identity = resolve_test_identity(historic_lab.get("test_name"), historic_lab.get("unit"))
        if current_identity and historic_identity:
            return {
                "comparable": current_identity.canonical_name == historic_identity.canonical_name
                and current_identity.canonical_unit == historic_identity.canonical_unit,
                "reason": "catalog_identity_match",
            }

        # Unknown tests can only be compared under a conservative exact-normalized
        # name-and-unit match. No implicit unit conversion is ever applied.
        current_name = normalize_label(current_lab.get("test_name"))
        historic_name = normalize_label(historic_lab.get("test_name"))
        current_unit = normalize_unit(current_lab.get("unit"))
        historic_unit = normalize_unit(historic_lab.get("unit"))
        return {
            "comparable": bool(current_name and current_unit and current_name == historic_name and current_unit == historic_unit),
            "reason": "exact_normalized_label_and_unit",
        }

    def _status(self, lab: Dict[str, Any]) -> Optional[str]:
        value = self._numeric(lab.get("value"))
        reference = lab.get("reference_range") or {}
        low = self._numeric(reference.get("low"))
        high = self._numeric(reference.get("high"))
        if value is None or low is None or high is None or low > high:
            return None
        if value < low:
            return "LOW"
        if value > high:
            return "HIGH"
        return "NORMAL"

    @staticmethod
    def _numeric(value: Any) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _finding_status(previous_status: Optional[str], current_status: str, previous_value: Optional[float], current_value: float) -> str:
        if previous_status is None:
            return "NEW_ABNORMAL" if current_status != "NORMAL" else "NO_PRIOR_COMPARISON"
        if previous_status != "NORMAL" and current_status == "NORMAL":
            return "CURRENTLY_NORMAL"
        if previous_status == "NORMAL" and current_status != "NORMAL":
            return "NEW_ABNORMAL"
        if previous_status == "NORMAL" and current_status == "NORMAL":
            return "NORMAL_STABLE"

        # Both results remain outside their report-provided ranges. Moving toward
        # the nearest boundary is factual improvement, not a recovery claim.
        if previous_status == "LOW":
            if previous_value is not None and current_value > previous_value:
                return "PERSISTENT_IMPROVING"
            if previous_value is not None and current_value < previous_value:
                return "PERSISTENT_WORSENING"
        if previous_status == "HIGH":
            if previous_value is not None and current_value < previous_value:
                return "PERSISTENT_IMPROVING"
            if previous_value is not None and current_value > previous_value:
                return "PERSISTENT_WORSENING"
        return "PERSISTENT_STABLE"

    @staticmethod
    def _lifecycle_state(finding_status: str) -> str:
        return {
            "NEW_ABNORMAL": "ACTIVE",
            "PERSISTENT_IMPROVING": "IMPROVING",
            "PERSISTENT_WORSENING": "WORSENED",
            "PERSISTENT_STABLE": "PERSISTENT",
            "CURRENTLY_NORMAL": "CURRENTLY_NORMAL",
            "NORMAL_STABLE": "CURRENTLY_NORMAL",
            "UNKNOWN": "UNKNOWN",
            "NO_PRIOR_COMPARISON": "UNKNOWN",
        }.get(finding_status, "UNKNOWN")

    @staticmethod
    def _report_date(report: Dict[str, Any]) -> str:
        metadata = (report.get("parsed_json") or {}).get("patient_metadata") or {}
        return str(metadata.get("report_date") or report.get("created_at") or "")
