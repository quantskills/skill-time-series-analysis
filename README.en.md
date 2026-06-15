# skill-time-series-analysis

[简体中文](README.md) | English

Hybrid runnable QuantSkills skill for time-series diagnostics. It provides a
conclusion-first agent workflow plus a Python package for price-series
distribution checks, Hurst/ADF/KPSS stationarity analysis, Engle-Granger
cointegration, mean-reversion half-life, and generic time-series factor examples.

## Quick Start

```bash
uv run python -m pytest tests/ -q
uv run ruff check .
```

```python
from skill_time_series_analysis import analyze_price_series

result = analyze_price_series(price, windows=[40, 80], lags=[1, 2, 5])
print(result.to_markdown())
```

## Public API Pyramid

Use top-level APIs first:

- `analyze_price_series`
- `analyze_spread`
- `analyze_pair_cointegration`
- `build_time_series_factor_frame`

Use diagnostics APIs when composing custom workflows:

- `distribution_diagnostics`
- `stationarity_diagnostics`
- `mean_reversion_diagnostics`
- `cointegration_diagnostics`

Low-level helpers remain available for advanced use:

- `kde_analysis`, `qq_analysis`, `ts_groupby_period`
- `TimeSeriesAnalyzer`, `analysis_results_to_df`
- `half_life_of_mean_reversion`, `engle_granger_cointegration`
- `ts_momentum`, `ts_volatility`, `ts_trend_slope`, `ts_mean_reversion_zscore`

## Boundary

This skill does not include strategy generation, ML, triple-barrier labels,
backtesting, PandaData access, or market data. Outputs are research diagnostics,
not investment advice or trading signals.
