"""Rule-based management decision engine."""

from __future__ import annotations

from typing import List


def evaluate_management_rules(
    mortality_rate: float,
    droppings_status: str,
    feed_used: float,
    flock_size: int,
) -> List[str]:
    alerts: List[str] = []

    if mortality_rate > 5:
        alerts.append("ALERT: Mortality rate is above 5%. Immediate veterinary review recommended.")

    if droppings_status.lower() == "bloody":
        alerts.append("WARNING: Bloody droppings suggest possible Coccidiosis. Isolate affected birds.")

    feed_per_bird = (feed_used / flock_size) if flock_size > 0 else 0
    if droppings_status.lower() == "green" and feed_per_bird < 0.08:
        alerts.append("WARNING: Green droppings with low feed intake may indicate a viral issue.")

    if not alerts:
        alerts.append("No major risk flag detected. Continue regular monitoring and biosecurity.")

    alerts.append("Recommendation: Maintain vaccination, sanitation, and daily flock observation logs.")
    return alerts
