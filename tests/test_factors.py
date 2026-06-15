from __future__ import annotations

import numpy as np
import pandas as pd

from skill_time_series_analysis import (
    build_time_series_factor_frame,
    ts_mean_reversion_zscore,
    ts_momentum,
    ts_trend_slope,
    ts_volatility,
)


def _bars() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=12, freq="D", name="date")
    close = pd.Series([10.0, 10.5, 11.0, 10.8, 11.3, 11.9, 12.2, 12.6, 12.4, 12.8, 13.1, 13.4], index=index)
    return pd.DataFrame(
        {
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close + 0.2,
            "low": close - 0.2,
            "close": close,
            "volume": np.arange(1_000, 1_012),
        },
        index=index,
    )


def test_generic_factor_functions_return_aligned_series() -> None:
    bars = _bars()

    for func in [ts_momentum, ts_volatility, ts_trend_slope, ts_mean_reversion_zscore]:
        result = func(bars, lookback=3)
        assert isinstance(result, pd.Series)
        assert result.index.equals(bars.index)
        assert result.iloc[:2].isna().all()


def test_build_time_series_factor_frame_uses_pyramid_column_names() -> None:
    bars = _bars()

    factors = build_time_series_factor_frame(bars, lookback=3)

    assert list(factors.columns) == [
        "momentum",
        "volatility",
        "trend_slope",
        "mean_reversion_zscore",
    ]
    assert factors.index.equals(bars.index)
    assert factors.iloc[:2].isna().all().all()
