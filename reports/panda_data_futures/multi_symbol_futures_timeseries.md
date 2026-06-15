# PandaData Futures Time-Series Analysis

- Data source: PandaData `get_market_data`, type=`future`.
- Date range: `20240101` to `20241231`.
- Symbols: `IF_DOMINANT.CFE`, `CU_DOMINANT.SHF`, `I_DOMINANT.DCE`.

## Cross-Symbol Summary

| symbol | n_obs | trend_score | trend_type | tail | skew |
| --- | --- | --- | --- | --- | --- |
| IF_DOMINANT.CFE | 242 | 5 | strong trend, non-stationary (trend strategies) | fat_tail | right_skew |
| CU_DOMINANT.SHF | 242 | 2 | weak trend or counter-trend | fat_tail | symmetric |
| I_DOMINANT.DCE | 242 | 2 | weak trend or counter-trend | fat_tail | right_skew |

## IF_DOMINANT.CFE

## Summary

| Metric | Value |
|---|---:|
| `n_obs` | 242 |
| `start` | 2024-01-02 00:00:00 |
| `end` | 2024-12-31 00:00:00 |
| `trend_score` | 5 |
| `trend_type` | strong trend, non-stationary (trend strategies) |
| `primary_tail_feature` | fat_tail |
| `primary_skew_feature` | right_skew |

## Evidence

### Distribution

| index | peak_height | peak_position | num_peaks | tail_feature | skew_feature | statistical_kurtosis | statistical_skewness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.5808 | -0.1351 | 2 | fat_tail | right_skew | 10.7425 | 0.9351 |
| 5 | 0.5871 | -0.1652 | 2 | fat_tail | right_skew | 17.2617 | 3.2085 |
| 20 | 0.5686 | -0.4955 | 2 | fat_tail | right_skew | 2.3922 | 1.6753 |

### Stationarity

| window_size | hurst | adf_pvalue | kpss_pvalue | trend_score | trend_type | min_lag | effective_max_lag | kpss_warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | 0.7213 | 0.0159 | 0.1000 | 2 | trending but stationary (short-term trend possible) | 10 | 20 | The test statistic is outside of the range of p-values available in the<br>look-up table. The actual p-value is greater than the p-value returned.<br> |
| 120 | 0.7538 | 0.6333 | 0.0331 | 5 | strong trend, non-stationary (trend strategies) | 20 | 40 |  |
| 180 | 0.7248 | 0.5294 | 0.0100 | 5 | strong trend, non-stationary (trend strategies) | 30 | 60 | The test statistic is outside of the range of p-values available in the<br>look-up table. The actual p-value is smaller than the p-value returned.<br> |


### Generated Charts

![KDE](IF_DOMINANT_CFE/distribution_kde_dist.png)

![QQ](IF_DOMINANT_CFE/distribution_qq_plot.png)

## CU_DOMINANT.SHF

## Summary

| Metric | Value |
|---|---:|
| `n_obs` | 242 |
| `start` | 2024-01-02 00:00:00 |
| `end` | 2024-12-31 00:00:00 |
| `trend_score` | 2 |
| `trend_type` | weak trend or counter-trend |
| `primary_tail_feature` | fat_tail |
| `primary_skew_feature` | symmetric |

## Evidence

### Distribution

| index | peak_height | peak_position | num_peaks | tail_feature | skew_feature | statistical_kurtosis | statistical_skewness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.4552 | 0.0551 | 1 | fat_tail | symmetric | 1.7606 | -0.1673 |
| 5 | 0.4325 | -0.1552 | 1 | near_normal | symmetric | 0.5532 | -0.0892 |
| 20 | 0.4467 | -0.0551 | 1 | near_normal | symmetric | -0.0885 | -0.1466 |

### Stationarity

| window_size | hurst | adf_pvalue | kpss_pvalue | trend_score | trend_type | min_lag | effective_max_lag | kpss_warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | 0.7389 | 0.4414 | 0.0499 | 5 | strong trend, non-stationary (trend strategies) | 10 | 20 |  |
| 120 | 0.5923 | 0.1036 | 0.0476 | 4 | strong trend, non-stationary (trend strategies) | 20 | 40 |  |
| 180 | 0.5496 | 0.5097 | 0.0225 | 2 | weak trend or counter-trend | 30 | 60 |  |


### Generated Charts

![KDE](CU_DOMINANT_SHF/distribution_kde_dist.png)

![QQ](CU_DOMINANT_SHF/distribution_qq_plot.png)

## I_DOMINANT.DCE

## Summary

| Metric | Value |
|---|---:|
| `n_obs` | 242 |
| `start` | 2024-01-02 00:00:00 |
| `end` | 2024-12-31 00:00:00 |
| `trend_score` | 2 |
| `trend_type` | weak trend or counter-trend |
| `primary_tail_feature` | fat_tail |
| `primary_skew_feature` | right_skew |

## Evidence

### Distribution

| index | peak_height | peak_position | num_peaks | tail_feature | skew_feature | statistical_kurtosis | statistical_skewness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.3775 | 0.1652 | 1 | fat_tail | right_skew | 1.5161 | 0.4007 |
| 5 | 0.3998 | 0.1552 | 1 | fat_tail | right_skew | 2.2166 | 0.4626 |
| 20 | 0.3617 | 0.0751 | 1 | near_normal | right_skew | -0.3578 | 0.2215 |

### Stationarity

| window_size | hurst | adf_pvalue | kpss_pvalue | trend_score | trend_type | min_lag | effective_max_lag | kpss_warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | 0.8115 | 0.0675 | 0.1000 | 3 | conflicting signals (verify further) | 10 | 20 | The test statistic is outside of the range of p-values available in the<br>look-up table. The actual p-value is greater than the p-value returned.<br> |
| 120 | 0.5465 | 0.1320 | 0.0100 | 2 | weak trend or counter-trend | 20 | 40 | The test statistic is outside of the range of p-values available in the<br>look-up table. The actual p-value is smaller than the p-value returned.<br> |
| 180 | 0.4400 | 0.3603 | 0.0100 | 2 | weak trend or counter-trend | 30 | 60 | The test statistic is outside of the range of p-values available in the<br>look-up table. The actual p-value is smaller than the p-value returned.<br> |


### Generated Charts

![KDE](I_DOMINANT_DCE/distribution_kde_dist.png)

![QQ](I_DOMINANT_DCE/distribution_qq_plot.png)

## Factor Snapshot

Latest factor rows are saved at `multi_symbol_factors_tail.csv`.
