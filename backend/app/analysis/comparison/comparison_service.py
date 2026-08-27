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
    ) -> Dict[str, Any]:
        current_labs = current_parsed_json.get("lab_results") or current_parsed_json.get("lab_facts") or []
        comparisons = []

        for current_lab in current_labs:
            comparison = self._compare_lab(current_lab, previous_reports, current_report_date)
            if comparison:
                comparisons.append(comparison)

        return {
            "catalog_version": CATALOG_VERSION,
            "catalog_status": CATALOG_STATUS,
            "history_available": bool(previous_reports),
            "previous_report_count": len(previous_reports),
            "comparisons": comparisons,
        }

    def _compare_lab(
        self,
        current_lab: Dict[str, Any],
        previous_reports: List[Dict[str, Any]],
        current_report_date: Optional[str],
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
                    history.append({"date": report_date, "value": value, "status": status})

        history.sort(key=lambda item: item["date"])
        previous = history[-1] if history else None
        previous_value = previous["value"] if previous else None
        previous_status = previous["status"] if previous else None
        direction = detect_trend(previous_value, current_value)
        finding_status = self._finding_status(previous_status, current_status, previous_value, current_value)

        return {
            "test_name": current_lab.get("test_name"),
            "unit": current_lab.get("unit"),
            "canonical_test_name": current_identity.canonical_name if current_identity else None,
            "catalog_id": current_identity.catalog_id if current_identity else None,
            "comparison_method": current_identity.matched_by if current_identity else "exact_normalized_label_and_unit",
            "history": history + [{"date": current_report_date or "current", "value": current_value, "status": current_status, "is_current": True}],
            "previous_value": previous_value,
            "current_value": current_value,
            "previous_status": previous_status,
            "current_status": current_status,
            "trend": direction,
            "finding_status": finding_status,
        }

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
            return "RESOLVED"
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
    def _report_date(report: Dict[str, Any]) -> str:
        metadata = (report.get("parsed_json") or {}).get("patient_metadata") or {}
        return str(metadata.get("report_date") or report.get("created_at") or "")
