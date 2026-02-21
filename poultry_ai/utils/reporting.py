"""Reporting and analytics helpers using matplotlib."""

from __future__ import annotations

from typing import Dict, List

import matplotlib.pyplot as plt


def generate_trend_charts(records: List[Dict], output_dir: str = "reports") -> Dict[str, str]:
    """Generate mortality/feed trends and disease history charts."""
    import os

    os.makedirs(output_dir, exist_ok=True)
    dates = [r["date"] for r in records]
    mortality = [r["mortality"] for r in records]
    feed = [r["feed_used"] for r in records]

    mortality_path = os.path.join(output_dir, "mortality_trend.png")
    feed_path = os.path.join(output_dir, "feed_trend.png")
    disease_path = os.path.join(output_dir, "disease_history.png")

    plt.figure(figsize=(8, 4))
    plt.plot(dates, mortality, marker="o")
    plt.title("Mortality Trend")
    plt.xlabel("Date")
    plt.ylabel("Mortality")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(mortality_path)
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.plot(dates, feed, marker="o", color="green")
    plt.title("Feed Usage Trend")
    plt.xlabel("Date")
    plt.ylabel("Feed Used (kg)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(feed_path)
    plt.close()

    disease_counts: Dict[str, int] = {}
    for record in records:
        disease = record["disease_detected"]
        disease_counts[disease] = disease_counts.get(disease, 0) + 1

    plt.figure(figsize=(8, 4))
    plt.bar(disease_counts.keys(), disease_counts.values(), color="orange")
    plt.title("Disease History")
    plt.xlabel("Disease")
    plt.ylabel("Occurrences")
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.savefig(disease_path)
    plt.close()

    return {
        "mortality_trend": mortality_path,
        "feed_trend": feed_path,
        "disease_history": disease_path,
    }
