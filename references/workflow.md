# Workflow

1. Clean the input series: numeric, sorted, no missing values in the diagnostic window.
2. Pick the highest-level API:
   - one price series: `analyze_price_series`
   - spread or residual: `analyze_spread`
   - two related series: `analyze_pair_cointegration`
   - feature matrix: `build_time_series_factor_frame`
3. Write the conclusion from `summary`.
4. Add evidence from distribution, stationarity, half-life, or cointegration tables.
5. Add caveats for short samples, conflicting tests, non-positive prices, or unstable residuals.
