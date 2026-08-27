from typing import Literal, Optional

Trend = Literal["INCREASING", "DECREASING", "STABLE", "INSUFFICIENT_HISTORY"]


def detect_trend(previous_value: Optional[float], current_value: Optional[float]) -> Trend:
    if previous_value is None or current_value is None:
        return "INSUFFICIENT_HISTORY"
    if current_value > previous_value:
        return "INCREASING"
    if current_value < previous_value:
        return "DECREASING"
    return "STABLE"
