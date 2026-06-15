from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from skill_time_series_analysis import (
    TimeSeriesInterpretation,
    TimeSeriesReport,
    analyze_price_series,
    generate_time_series_report,
    interpret_time_series_analysis,
)

REMOVED_TREND_METRIC = "trend" + "_score"


def _trend_price(n: int = 220) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    trend = np.linspace(100.0, 160.0, n)
    cycle = np.sin(np.linspace(0, 12, n)) * 1.5
    return pd.Series(trend + cycle, index=index, name="close")


def _mean_reverting_price(n: int = 220) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    values = 100.0 + np.sin(np.linspace(0, 24, n)) * 2.5
    return pd.Series(values, index=index, name="close")


def test_interpret_time_series_analysis_explains_trend_properties_in_chinese() -> None:
    analysis = analyze_price_series(_trend_price(), windows=[60, 120, 180], lags=[1, 5, 20])

    interpretation = interpret_time_series_analysis(analysis)

    assert isinstance(interpretation, TimeSeriesInterpretation)
    combined = interpretation.to_markdown()
    assert "趋势性" in combined
    assert "非平稳" in combined or "趋势" in combined
    assert "投研方向" in combined
    assert "适合进一步研究" in combined


def test_interpret_time_series_analysis_handles_weak_or_mean_reverting_series() -> None:
    analysis = analyze_price_series(
        _mean_reverting_price(),
        windows=[60, 120, 180],
        lags=[1, 5, 20],
    )

    interpretation = interpret_time_series_analysis(analysis)
    combined = interpretation.to_markdown()

    assert "均值回复" in combined or "谨慎" in combined
    assert "投研方向" in combined


def test_generate_time_series_report_writes_markdown_and_plots(tmp_path: Path) -> None:
    report = generate_time_series_report(
        _trend_price(),
        series_name="demo_series",
        title="Demo Series 自动时序检测报告",
        windows=[60, 120, 180],
        lags=[1, 5, 20],
        output_dir=tmp_path,
    )

    assert isinstance(report, TimeSeriesReport)
    assert report.markdown_path == tmp_path / "demo_series_time_series_report.md"
    assert report.markdown_path.exists()
    assert (tmp_path / "distribution_kde_dist.png").exists()
    assert (tmp_path / "distribution_qq_plot.png").exists()
    assert report.plot_paths["kde"].endswith("distribution_kde_dist.png")
    assert report.plot_paths["qq"].endswith("distribution_qq_plot.png")

    markdown = report.to_markdown()
    expected_sections = [
        "## 一句话结论",
        "## 时间序列性质",
        "### 平稳性分析",
        "### 记忆性分析",
        "### 趋势性分析",
        "### 分布形态分析",
        "## 量化投研建议",
        "### 策略方向",
        "### 因子方向",
        "## 检测证据",
        "### Stationarity / Hurst / ADF / KPSS",
        "### KDE / QQ",
        "## 图表",
        "## 注意事项",
    ]
    for section in expected_sections:
        assert section in markdown
    assert markdown.index("## 一句话结论") < markdown.index("## 检测证据")
    assert REMOVED_TREND_METRIC not in markdown
    assert "投研方向" in markdown
    assert "适合进一步研究" in markdown
    assert "买入" not in markdown
    assert "卖出" not in markdown
    assert "交易信号" not in markdown
