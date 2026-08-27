"""Versioned, non-diagnostic identity rules for longitudinal lab comparison.

This is deliberately *not* a clinical-reference catalogue. Reference ranges and
abnormality decisions remain sourced from the originating laboratory report until
each clinical rule is reviewed and approved.
"""

from dataclasses import dataclass
from typing import Optional


CATALOG_VERSION = "0.1.0"
CATALOG_STATUS = "ENGINEERING_SEED_NOT_CLINICALLY_REVIEWED"


@dataclass(frozen=True)
class TestIdentity:
    canonical_name: str
    canonical_unit: str
    catalog_id: Optional[str]
    matched_by: str


# Entries are limited to stable report-label aliases. They do not contain
# diagnostic assertions, reference ranges, unit conversions, or critical values.
TEST_CATALOG = {
    "hemoglobin": {
        "aliases": {"hemoglobin", "haemoglobin", "hb", "hgb"},
        "units": {"g/dl"},
        "catalog_id": "LOCAL:HEMOGLOBIN",
    },
    "hematocrit": {
        "aliases": {"hematocrit", "haematocrit", "hct", "pcv"},
        "units": {"%", "percent"},
        "catalog_id": "LOCAL:HEMATOCRIT",
    },
    "white blood cell count": {
        "aliases": {"wbc", "white blood cell", "white blood cell count", "leukocyte count"},
        "units": {"cells/ul", "cells/µl", "/ul", "/µl"},
        "catalog_id": "LOCAL:WBC",
    },
    "platelet count": {
        "aliases": {"platelet", "platelets", "platelet count"},
        "units": {"cells/ul", "cells/µl", "/ul", "/µl"},
        "catalog_id": "LOCAL:PLATELETS",
    },
    "thyroid stimulating hormone": {
        "aliases": {"tsh", "thyroid stimulating hormone"},
        "units": {"miu/l", "uiu/ml", "mu/l"},
        "catalog_id": "LOCAL:TSH",
    },
}


def normalize_label(value: object) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def normalize_unit(value: object) -> str:
    return normalize_label(value).replace("μ", "µ").rstrip(".")


def resolve_test_identity(test_name: object, unit: object) -> Optional[TestIdentity]:
    """Resolve a catalog identity only when name and unit are explicitly supported."""
    label = normalize_label(test_name)
    normalized_unit = normalize_unit(unit)
    if not label or not normalized_unit:
        return None

    for canonical_name, entry in TEST_CATALOG.items():
        if label in entry["aliases"] and normalized_unit in entry["units"]:
            return TestIdentity(
                canonical_name=canonical_name,
                canonical_unit=normalized_unit,
                catalog_id=entry["catalog_id"],
                matched_by="catalog_alias_and_unit",
            )
    return None
