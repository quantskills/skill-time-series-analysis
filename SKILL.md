---
name: time-series-analysis
description: Use when an agent needs conclusion-first diagnostics for financial time series, including price-series distribution checks, Hurst/ADF/KPSS stationarity, spread half-life, Engle-Granger cointegration, KDE or QQ evidence, and generic time-series factor examples.
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
model, factor, or strategy workflow. Start from the highest-level API and only
drop to low-level helpers when composing custom analysis.

## Core Workflow

1. Use `analyze_price_series`, `analyze_spread`, or `analyze_pair_cointegration`.
2. Read the returned `summary` first and write the conclusion before evidence.
3. Use `to_markdown()` for a compact report with Summary before Evidence.
4. Open references only when you need deeper API details or interpretation rules.

## API Pyramid

| Layer | Use first | Purpose |
|---|---|---|
| Main API | `analyze_price_series`, `analyze_spread`, `analyze_pair_cointegration`, `build_time_series_factor_frame` | Agent-facing conclusions |
| Diagnostics | `distribution_diagnostics`, `stationarity_diagnostics`, `mean_reversion_diagnostics`, `cointegration_diagnostics` | Composable workflows |
| Helpers | `kde_analysis`, `qq_analysis`, `TimeSeriesAnalyzer`, factor helpers | Advanced or custom analysis |

## Output Contract

Always produce:

- a short conclusion from `result.summary`
- key evidence tables or charts
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
