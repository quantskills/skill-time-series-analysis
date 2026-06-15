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

## Real-Data Example Report

The repository keeps one PandaData multi-symbol futures analysis report:

- Report entry: `reports/panda_data_futures/multi_symbol_futures_timeseries.md`
- Generating test: `tests/test_panda_data_futures_report.py`
- Data source: PandaData `get_market_data(type="future")`
- Symbols: `IF_DOMINANT.CFE`, `CU_DOMINANT.SHF`, `I_DOMINANT.DCE`

Regenerate the report with PandaData credentials:

```bash
PANDA_DATA_ENV_FILE=/path/to/.env \
  uv run python -m pytest tests/test_panda_data_futures_report.py -q
```

The `.env` file should define `PANDA_DATA_USERNAME` and `PANDA_DATA_PASSWORD`.
The integration test skips when credentials or the SDK are unavailable; the
runtime Python package itself does not depend on PandaData.

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

The runtime package does not include strategy generation, ML, triple-barrier
labels, backtesting, a PandaData client, or market-data management.
`tests/test_panda_data_futures_report.py` is an optional real-data integration
example that demonstrates the API on external futures bars. Outputs are research
diagnostics, not investment advice or trading signals.
