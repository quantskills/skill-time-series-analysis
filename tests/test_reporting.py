from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from skill_time_series_analysis import (
    AnalysisReport,
    TimeSeriesInterpretation,
    TimeSeriesReport,
    analyze_price_series,
    generate_pair_cointegration_report,
    generate_spread_report,
    generate_time_series_report,
    interpret_time_series_analysis,
)

REMOVED_TREND_METRIC = "trend" + "_score"
ROOT = Path(__file__).resolve().parents[1]


def _trend_price(n: int = 220) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    trend = np.linspace(100.0, 160.0, n)
    cycle = np.sin(np.linspace(0, 12, n)) * 1.5
    return pd.Series(trend + cycle, index=index, name="close")


def _mean_reverting_price(n: int = 220) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    values = 100.0 + np.sin(np.linspace(0, 24, n)) * 2.5
    return pd.Series(values, index=index, name="close")


def _spread_series(n: int = 180) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    rng = np.random.default_rng(42)
    values = []
    current = 0.0
    for _ in range(n):
        current = 0.82 * current + rng.normal(0.0, 0.15)
        values.append(current)
    return pd.Series(values, index=index, name="spread")


def _cointegrated_pair(n: int = 180) -> tuple[pd.Series, pd.Series]:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    x = pd.Series(np.linspace(100.0, 140.0, n) + np.sin(np.linspace(0, 12, n)), index=index, name="x")
    residual = np.random.default_rng(42).normal(0.0, 0.2, n)
    y = pd.Series(1.6 * x + 3.0 + residual, index=index, name="y")
    return y, x


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
        "## Log Diff 分析",
        "Log diff 1",
        "Log diff 5",
        "Log diff 10",
        "### Log Diff KDE / QQ",
        "#### Log Diff KDE Diagnostics",
        "#### Log Diff QQ Diagnostics",
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
    assert "build_time_series_" + "factor_frame" not in markdown
    assert "Factor" + " Snapshot" not in markdown


def test_generate_spread_report_writes_spread_example(tmp_path: Path) -> None:
    report = generate_spread_report(
        _spread_series(),
        series_name="demo_spread",
        title="Demo Spread 价差检测报告",
        windows=[60, 120],
        output_dir=tmp_path,
    )

    assert isinstance(report, AnalysisReport)
    assert report.markdown_path == tmp_path / "demo_spread_spread_report.md"
    assert report.markdown_path.exists()
    markdown = report.to_markdown()
    for phrase in [
        "## 一句话结论",
        "## Spread / 价差检测结果",
        "### 半衰期",
        "### Hurst / ADF / KPSS",
        "均值回复",
        "投研方向",
    ]:
        assert phrase in markdown
    assert "买入" not in markdown
    assert "卖出" not in markdown
    assert "交易信号" not in markdown


def test_generate_pair_cointegration_report_writes_pair_example(tmp_path: Path) -> None:
    y, x = _cointegrated_pair()

    report = generate_pair_cointegration_report(
        y,
        x,
        pair_name="demo_pair",
        title="Demo Pair 协整检测报告",
        output_dir=tmp_path,
    )

    assert isinstance(report, AnalysisReport)
    assert report.markdown_path == tmp_path / "demo_pair_cointegration_report.md"
    assert report.markdown_path.exists()
    markdown = report.to_markdown()
    for phrase in [
        "## 一句话结论",
        "## Pair / 双序列协整检测结果",
        "Engle-Granger",
        "alpha",
        "beta",
        "残差平稳性",
        "投研方向",
    ]:
        assert phrase in markdown
    assert "买入" not in markdown
    assert "卖出" not in markdown
    assert "交易信号" not in markdown


def test_checked_in_spread_and_pair_report_examples_exist() -> None:
    examples = {
        "reports/time_series_examples/demo_spread/demo_spread_spread_report.md": [
            "Spread / 价差检测结果",
            "半衰期",
            "Hurst / ADF / KPSS",
        ],
        "reports/time_series_examples/demo_pair/demo_pair_cointegration_report.md": [
            "Pair / 双序列协整检测结果",
            "Engle-Granger",
            "残差平稳性",
        ],
    }

    for relative_path, phrases in examples.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase in text
