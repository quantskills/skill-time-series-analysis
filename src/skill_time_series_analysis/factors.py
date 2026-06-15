"""Generic single-instrument time-series factor examples."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _require_price(group: pd.DataFrame, price_col: str, func_name: str) -> pd.Series:
    if price_col not in group.columns:
        raise ValueError(f"{func_name} requires '{price_col}' column")
    return group[price_col].astype(float)


def _require_lookback(lookback: int, func_name: str, *, minimum: int = 1) -> None:
    if lookback < minimum:
        raise ValueError(f"{func_name} requires lookback >= {minimum}")


def ts_momentum(
    group: pd.DataFrame,
    *,
    lookback: int = 20,
    price_col: str = "close",
) -> pd.Series:
    """Trailing percentage return over ``lookback`` bars."""

    _require_lookback(lookback, "ts_momentum")
    price = _require_price(group, price_col, "ts_momentum")
    return price.pct_change(lookback).rename(None)


def ts_volatility(
    group: pd.DataFrame,
    *,
    lookback: int = 20,
    price_col: str = "close",
    annualization: int = 252,
) -> pd.Series:
    """Annualized trailing return volatility."""

    _require_lookback(lookback, "ts_volatility")
    if annualization <= 0:
        raise ValueError("ts_volatility requires positive annualization")

    price = _require_price(group, price_col, "ts_volatility")
    returns = price.pct_change()
    volatility = returns.rolling(lookback, min_periods=lookback).std(ddof=0)
    return (volatility * np.sqrt(float(annualization))).rename(None)


def ts_trend_slope(
    group: pd.DataFrame,
    *,
    lookback: int = 20,
    price_col: str = "close",
) -> pd.Series:
    """Rolling OLS slope of log price over ``lookback`` bars."""

    _require_lookback(lookback, "ts_trend_slope", minimum=2)
    price = _require_price(group, price_col, "ts_trend_slope")
    log_price = np.log(price.where(price > 0.0))
    x = np.arange(lookback, dtype=float)
    x_centered = x - x.mean()
    denominator = float(np.sum(x_centered**2))

    def slope(values: np.ndarray) -> float:
        if not np.isfinite(values).all():
            return np.nan
        y_centered = values - values.mean()
        return float(np.sum(y_centered * x_centered) / denominator)

    return log_price.rolling(lookback, min_periods=lookback).apply(slope, raw=True).rename(None)


def ts_mean_reversion_zscore(
    group: pd.DataFrame,
    *,
    lookback: int = 20,
    price_col: str = "close",
) -> pd.Series:
    """Negative rolling price z-score, so lower-than-average prices rank higher."""

    _require_lookback(lookback, "ts_mean_reversion_zscore", minimum=2)
    price = _require_price(group, price_col, "ts_mean_reversion_zscore")
    mean = price.rolling(lookback, min_periods=lookback).mean()
    std = price.rolling(lookback, min_periods=lookback).std(ddof=0).replace(0.0, np.nan)
    return (-(price - mean) / std).rename(None)


def build_time_series_factor_frame(
    bars: pd.DataFrame,
    *,
    lookback: int = 20,
    price_col: str = "close",
) -> pd.DataFrame:
    """Build the four public generic factor columns in pyramid order."""

    return pd.DataFrame(
        {
            "momentum": ts_momentum(bars, lookback=lookback, price_col=price_col),
            "volatility": ts_volatility(bars, lookback=lookback, price_col=price_col),
            "trend_slope": ts_trend_slope(bars, lookback=lookback, price_col=price_col),
            "mean_reversion_zscore": ts_mean_reversion_zscore(
                bars, lookback=lookback, price_col=price_col
            ),
        },
        index=bars.index,
    )


__all__ = [
    "build_time_series_factor_frame",
    "ts_mean_reversion_zscore",
    "ts_momentum",
    "ts_trend_slope",
    "ts_volatility",
]
