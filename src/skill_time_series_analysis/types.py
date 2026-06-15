"""Result dataclasses for time-series diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        if pd.isna(value):
            return "nan"
        return f"{value:.4f}"
    return str(value)


def _summary_markdown(summary: dict[str, Any]) -> str:
    rows = ["| Metric | Value |", "|---|---:|"]
    for key, value in summary.items():
        rows.append(f"| `{key}` | {_format_value(value)} |")
    return "\n".join(rows)


def _frame_markdown(frame: pd.DataFrame, *, include_index: bool = True, rows: int = 10) -> str:
    if frame.empty:
        return "_No rows._"
    view = frame.head(rows).copy()
    columns = list(view.columns)
    if include_index:
        header = ["index", *columns]
        body = [[idx, *[view.loc[idx, col] for col in columns]] for idx in view.index]
    else:
        header = columns
        body = [[row[col] for col in columns] for _, row in view.iterrows()]
    lines = [
        "| " + " | ".join(str(col) for col in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(_format_value(value) for value in row) + " |")
    return "\n".join(lines)


@dataclass
class DistributionDiagnostics:
    """Distribution-level diagnostics for a price series."""

    summary: dict[str, Any]
    kde: pd.DataFrame
    qq: pd.DataFrame
    plot_paths: dict[str, str]

    def to_markdown(self) -> str:
        return (
            "## Summary\n\n"
            f"{_summary_markdown(self.summary)}\n\n"
            "## Evidence\n\n"
            "### KDE Diagnostics\n\n"
            f"{_frame_markdown(self.kde)}\n\n"
            "### QQ Diagnostics\n\n"
            f"{_frame_markdown(self.qq)}\n"
        )


@dataclass
class TimeSeriesAnalysis:
    """Top-level price-series analysis result."""

    summary: dict[str, Any]
    distribution: DistributionDiagnostics
    stationarity: pd.DataFrame

    def to_markdown(self) -> str:
        return (
            "## Summary\n\n"
            f"{_summary_markdown(self.summary)}\n\n"
            "## Evidence\n\n"
            "### Distribution\n\n"
            f"{_frame_markdown(self.distribution.kde)}\n\n"
            "### Stationarity\n\n"
            f"{_frame_markdown(self.stationarity, include_index=False)}\n"
        )


@dataclass
class MeanReversionAnalysis:
    """Spread and mean-reversion diagnostics."""

    summary: dict[str, Any]
    stationarity: pd.DataFrame
    half_life: dict[str, Any]
    distribution: DistributionDiagnostics | None = None

    def to_markdown(self) -> str:
        return (
            "## Summary\n\n"
            f"{_summary_markdown(self.summary)}\n\n"
            "## Evidence\n\n"
            "### Half-Life\n\n"
            f"{_summary_markdown(self.half_life)}\n\n"
            "### Stationarity\n\n"
            f"{_frame_markdown(self.stationarity, include_index=False)}\n"
        )


@dataclass
class CointegrationAnalysis:
    """Engle-Granger pair cointegration diagnostics."""

    summary: dict[str, Any]
    residuals: pd.Series
    evidence: dict[str, Any]

    def to_markdown(self) -> str:
        return (
            "## Summary\n\n"
            f"{_summary_markdown(self.summary)}\n\n"
            "## Evidence\n\n"
            f"{_summary_markdown(self.evidence)}\n"
        )


__all__ = [
    "CointegrationAnalysis",
    "DistributionDiagnostics",
    "MeanReversionAnalysis",
    "TimeSeriesAnalysis",
]
