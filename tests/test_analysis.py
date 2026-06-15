from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from skill_time_series_analysis import (
    CointegrationAnalysis,
    DistributionDiagnostics,
    MeanReversionAnalysis,
    TimeSeriesAnalysis,
    TimeSeriesAnalyzer,
    analysis_results_to_df,
    analyze_pair_cointegration,
    analyze_price_series,
    analyze_spread,
    engle_granger_cointegration,
    half_life_of_mean_reversion,
    kde_analysis,
    qq_analysis,
    stationarity_diagnostics,
    ts_groupby_period,
)

ROOT = Path(__file__).resolve().parents[1]
REMOVED_TREND_METRIC = "trend" + "_score"


def _price_series(n: int = 180) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=n, freq="D", name="date")
    trend = np.linspace(100.0, 130.0, n)
    cycle = np.sin(np.linspace(0, 8, n)) * 2.0
    return pd.Series(trend + cycle, index=index, name="close")


def test_analyze_price_series_returns_pyramid_result() -> None:
    result = analyze_price_series(_price_series(), windows=[40, 80], lags=[1, 2, 5], plot=False)

    assert isinstance(result, TimeSeriesAnalysis)
    assert isinstance(result.distribution, DistributionDiagnostics)
    assert result.summary["n_obs"] == 180
    assert "trend_type" in result.summary
    assert REMOVED_TREND_METRIC not in result.summary
    assert REMOVED_TREND_METRIC not in result.stationarity.columns
    assert {"window_size", "hurst", "trend_type"}.issubset(result.stationarity.columns)

    markdown = result.to_markdown()
    assert markdown.index("## Summary") < markdown.index("## Evidence")
    assert "Distribution" in markdown
    assert "Stationarity" in markdown


def test_analyze_spread_reports_half_life_and_markdown() -> None:
    spread = pd.Series([(-0.8) ** i for i in range(80)], index=pd.date_range("2024-01-01", periods=80))

    result = analyze_spread(spread, windows=[30, 60], plot=False)

    assert isinstance(result, MeanReversionAnalysis)
    assert result.summary["is_mean_reverting"] is True
    assert result.summary["half_life_bars"] > 0
    assert result.half_life["lambda"] < 0
    assert result.to_markdown().index("## Summary") < result.to_markdown().index("## Evidence")


def test_analyze_pair_cointegration_returns_regression_evidence() -> None:
    x = _price_series(120)
    y = 1.5 * x + 2.0

    result = analyze_pair_cointegration(y, x, significance=0.1)

    assert isinstance(result, CointegrationAnalysis)
    assert result.summary["n_obs"] == 120
    assert result.summary["beta"] == pytest.approx(1.5, rel=1e-6)
    assert "adf_pvalue" in result.summary
    assert len(result.residuals) == 120
    assert result.to_markdown().index("## Summary") < result.to_markdown().index("## Evidence")


def test_distribution_helpers_return_kde_and_qq_fields() -> None:
    price = _price_series(140)

    kde, _ = kde_analysis(price, show=False, lags=[1, 5])
    qq, _ = qq_analysis(price, show=False, lags=[1, 5])

    assert set(kde) == {1, 5}
    assert {"peak_height", "tail_feature", "skew_feature"}.issubset(kde[1])
    assert set(qq) == {1, 5}
    assert {"kurtosis", "skewness", "qq_deviation"}.issubset(qq[1])


def test_stationarity_helpers_cover_hurst_adf_and_kpss() -> None:
    price = _price_series(220)
    analyzer = TimeSeriesAnalyzer(price)

    hurst = analyzer.calculate_hurst(min_lag=10, max_lag=30)
    adf = analyzer.run_adf_test()
    kpss = analyzer.run_kpss_test()
    stationarity = stationarity_diagnostics(price, windows=[60, 120])

    assert np.isfinite(hurst)
    assert {"statistic", "pvalue", "lags", "critical_values"}.issubset(adf)
    assert {"statistic", "pvalue", "critical_values", "warning"}.issubset(kpss)
    assert REMOVED_TREND_METRIC not in stationarity.columns
    assert {"hurst", "adf_pvalue", "kpss_pvalue", "trend_type"}.issubset(
        stationarity.columns
    )


def test_engle_granger_cointegration_helper_returns_residual_adf() -> None:
    x = _price_series(100)
    y = 2.0 * x + 3.0

    result = engle_granger_cointegration(y, x)

    assert result["alpha"] == pytest.approx(3.0, rel=1e-6)
    assert result["beta"] == pytest.approx(2.0, rel=1e-6)
    assert result["adf_pvalue"] <= 0.05
    assert len(result["residuals"]) == 100


def test_ts_groupby_period_writes_png_and_csv(tmp_path: Path) -> None:
    price = _price_series(120)

    _, plot_path, csv_path = ts_groupby_period(
        price,
        periods=["1min", "7D"],
        save_path=tmp_path / "period.png",
        show=False,
    )

    assert plot_path is not None
    assert csv_path is not None
    assert Path(plot_path).exists()
    assert Path(csv_path).exists()


def test_markdown_tables_escape_multiline_values() -> None:
    distribution = DistributionDiagnostics(
        summary={"n_obs": 2},
        kde=pd.DataFrame({"tail_feature": ["line one\nline two"]}),
        qq=pd.DataFrame(),
        plot_paths={},
    )
    result = TimeSeriesAnalysis(
        summary={"trend_type": "line one\nline two"},
        distribution=distribution,
        stationarity=pd.DataFrame({"kpss_warning": ["line one\nline two"]}),
    )

    markdown = result.to_markdown()

    assert "line one<br>line two" in markdown
    assert "line one\nline two" not in markdown


def test_low_level_helpers_keep_existing_behavior() -> None:
    frame = analysis_results_to_df(
        {
            "price_length": 100,
            "kde": {
                1: {"peak_height": 0.4, "skew_feature": "symmetric"},
                2: {"peak_height": 0.5, "skew_feature": "right_skew"},
            },
        }
    )
    assert list(frame.index) == [1, 2]
    assert frame.loc[2, "kde_skew_feature"] == "right_skew"

    analyzer = TimeSeriesAnalyzer(pd.Series(np.linspace(100.0, 120.0, 80)))
    analyzer.results[40] = {
        "hurst": 0.62,
        "adf": {"pvalue": 0.2},
        "kpss": {"pvalue": 0.01, "warning": None},
        "min_lag": 5,
        "window_max_lag": 12,
    }
    assert "strong trend" in analyzer.get_results_dataframe().loc[0, "trend_type"]

    with pytest.raises(ValueError, match="at least 10"):
        half_life_of_mean_reversion(pd.Series([1.0, 0.5, 0.25]))


def test_agent_metadata_references_exist() -> None:
    data = yaml.safe_load((ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    for ref in data["references"]:
        assert (ROOT / ref).exists(), ref
