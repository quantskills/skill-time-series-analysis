# Workflow

1. Clean the input series: numeric, sorted, no missing values in the diagnostic window.
2. Pick the highest-level API:
   - user-facing price report: `generate_time_series_report`
   - one price series diagnostics: `analyze_price_series`
   - spread or residual: `analyze_spread`
   - two related series: `analyze_pair_cointegration`
   - feature matrix: `build_time_series_factor_frame`
3. For user-facing output, write `report.to_markdown()` or return the saved Markdown file.
4. Explain stationarity, memory, trend, and distribution shape in plain language.
5. Phrase strategy and factor output as research directions.
6. Add caveats for short samples, conflicting tests, non-positive prices, or unstable residuals.
