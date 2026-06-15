---
name: time-series-analysis
description: Use when an agent needs conclusion-first diagnostics or Markdown reports for financial time series, including KDE/QQ distribution checks, Hurst/ADF/KPSS stationarity, spread half-life, Engle-Granger cointegration, and generic time-series factor examples.
quantSkills:
  organization: https://github.com/quantskills
  repository: quantskills/skill-time-series-analysis
  repository_url: https://github.com/quantskills/skill-time-series-analysis
  project_type: skill
  collection: quant-research-tools
  license: GPL-3.0
  category: tooling
  tags: [time-series, stationarity, cointegration, mean-reversion, quant-research]
  platforms: [claude-code, codex, openclaw, cursor]
  language: zh-en
  status: draft
  validation_level: runnable
  maintainer_type: community
  requires: []
  summary_zh: 结论先行的时序分析 Skill：分布、平稳性、协整、半衰期和 generic 时序因子。
  summary_en: Conclusion-first time-series diagnostics for distributions, stationarity, cointegration, half-life, and generic factors.
---

# Time Series Analysis

Use this skill to diagnose price series, spreads, or pairs before choosing a
model, factor, or strategy workflow. For user-facing answers, start with the
report API so the agent can return a Chinese, conclusion-first Markdown
diagnostic with evidence and research directions.

## Core Workflow

1. For a single price series, call `generate_time_series_report(...)`.
2. Use `report.to_markdown()` or the written `.md` file as the user-facing answer.
3. For custom workflows, use `analyze_price_series`, `analyze_spread`, or `analyze_pair_cointegration`.
4. Report conclusions before evidence; phrase strategy output as research directions, not orders.

## API Pyramid

| Layer | Use first | Purpose |
|---|---|---|
| Report API | `generate_time_series_report`, `interpret_time_series_analysis` | User-facing Markdown reports |
| Main API | `analyze_price_series`, `analyze_spread`, `analyze_pair_cointegration`, `build_time_series_factor_frame` | Agent-facing conclusions |
| Diagnostics | `distribution_diagnostics`, `stationarity_diagnostics`, `mean_reversion_diagnostics`, `cointegration_diagnostics` | Composable workflows |
| Helpers | `kde_analysis`, `qq_analysis`, `TimeSeriesAnalyzer`, factor helpers | Advanced or custom analysis |

## Output Contract

Always produce:

- a short conclusion from `result.summary`
- key evidence tables or charts
- plain-language stationarity, memory, trend, and distribution interpretation
- quant research directions for strategy and factor exploration
- explicit caveats when sample length is short, tests conflict, or residuals are unstable

## References

- `references/workflow.md` - recommended agent workflow
- `references/api.md` - public API map
- `references/interpretation.md` - Hurst/ADF/KPSS, KDE/QQ, half-life, cointegration interpretation
- `references/report-format.md` - Markdown report template
- `references/anti-patterns.md` - mistakes that make diagnostics misleading

## Boundary

This skill does not fetch data, run backtests, train ML models, or generate
trading signals. It provides research diagnostics only.
