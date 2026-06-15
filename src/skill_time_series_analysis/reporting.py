"""Human-readable time-series diagnostic reports."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from skill_time_series_analysis.analysis import analyze_price_series
from skill_time_series_analysis.types import (
    TimeSeriesAnalysis,
    TimeSeriesInterpretation,
    TimeSeriesReport,
    _frame_markdown,
)


def _latest_stationarity(analysis: TimeSeriesAnalysis) -> dict[str, Any]:
    if analysis.stationarity.empty:
        return {}
    return analysis.stationarity.iloc[-1].to_dict()


def _as_float(value: Any, default: float = np.nan) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_finite(value: float) -> bool:
    return bool(np.isfinite(value))


def _safe_file_stem(series_name: str) -> str:
    stem = re.sub(r"[^0-9A-Za-z_.-]+", "_", series_name.strip())
    return stem.strip("._-") or "series"


def _relative_link(path: str | Path, base_dir: Path | None) -> str:
    target = Path(path)
    if base_dir is None:
        return str(target)
    try:
        return str(target.relative_to(base_dir))
    except ValueError:
        return str(target)


def _strategy_directions(
    *,
    hurst: float,
    trend_type: str,
    adf_stationary: bool,
    kpss_stationary: bool,
    tail_feature: str,
) -> list[str]:
    directions: list[str] = []
    is_trending = "strong trend" in trend_type or (
        _is_finite(hurst) and hurst > 0.55 and not kpss_stationary
    )
    if is_trending:
        directions.append("适合进一步研究趋势跟随、时间序列动量、突破确认和趋势状态识别等投研方向。")
    elif _is_finite(hurst) and hurst < 0.5 and adf_stationary:
        directions.append("适合进一步研究均值回复、区间震荡、z-score 反转和偏离修复等投研方向。")
    else:
        directions.append("适合进一步研究多状态过滤、趋势与反转切换、低置信度环境下的仓位控制等投研方向。")

    if adf_stationary and kpss_stationary:
        directions.append("平稳性证据较强时，可优先研究价差、残差、标准化偏离、均值回复和周期性结构。")
    if tail_feature == "fat_tail":
        directions.append("收益分布存在厚尾特征时，可补充波动率目标、尾部风险过滤和极端行情压力测试。")
    return directions


def _factor_directions(
    *,
    hurst: float,
    trend_type: str,
    skew_feature: str,
    tail_feature: str,
) -> list[str]:
    directions: list[str] = []
    if "strong trend" in trend_type or (_is_finite(hurst) and hurst > 0.55):
        directions.append("趋势类因子：滚动收益、均线斜率、价格通道位置、趋势强度和突破持续性。")
    elif _is_finite(hurst) and hurst < 0.5:
        directions.append("均值回复类因子：滚动 z-score、布林带偏离、短期反转和残差回归速度。")
    else:
        directions.append("状态识别类因子：Hurst 状态、波动分位、ADF/KPSS 组合标签和 regime filter。")

    if tail_feature == "fat_tail":
        directions.append("风险类因子：尾部波动、QQ 偏离、极端收益频率和下行波动。")
    if skew_feature != "symmetric":
        directions.append("分布类因子：收益偏度、偏度变化和非对称风险暴露。")
    return directions


def _caveats(
    *,
    n_obs: int,
    adf_stationary: bool,
    kpss_stationary: bool,
    tail_feature: str,
) -> list[str]:
    caveats = ["这些检测结果用于确定投研方向，不能直接作为下单依据。"]
    if n_obs < 120:
        caveats.append("样本长度偏短，Hurst、ADF、KPSS 和分布估计可能不稳定。")
    if adf_stationary != kpss_stationary:
        caveats.append("ADF 与 KPSS 结论存在差异，应结合更长窗口、不同频率或业务背景复核。")
    if tail_feature == "fat_tail":
        caveats.append("厚尾分布意味着极端波动更常见，后续研究需要单独评估尾部风险。")
    return caveats


def interpret_time_series_analysis(
    analysis: TimeSeriesAnalysis,
    *,
    language: str = "zh",
) -> TimeSeriesInterpretation:
    """Translate numeric diagnostics into human-readable research interpretation."""

    if language != "zh":
        raise ValueError("only language='zh' is supported in this version")

    latest = _latest_stationarity(analysis)
    n_obs = int(analysis.summary.get("n_obs", 0))
    hurst = _as_float(latest.get("hurst"))
    adf_pvalue = _as_float(latest.get("adf_pvalue"))
    kpss_pvalue = _as_float(latest.get("kpss_pvalue"))
    trend_type = str(latest.get("trend_type", analysis.summary.get("trend_type", "unknown")))
    tail_feature = str(analysis.summary.get("primary_tail_feature", "unknown"))
    skew_feature = str(analysis.summary.get("primary_skew_feature", "unknown"))
    max_qq_deviation = _as_float(analysis.distribution.summary.get("max_qq_deviation"))

    adf_stationary = _is_finite(adf_pvalue) and adf_pvalue < 0.05
    kpss_stationary = _is_finite(kpss_pvalue) and kpss_pvalue > 0.05

    if adf_stationary and kpss_stationary:
        stationarity_text = (
            f"ADF p-value={adf_pvalue:.4f} 且 KPSS p-value={kpss_pvalue:.4f}，"
            "两类检验共同支持序列在当前窗口内更接近平稳过程。"
        )
    elif not adf_stationary and not kpss_stationary:
        stationarity_text = (
            f"ADF p-value={adf_pvalue:.4f} 未拒绝单位根，KPSS p-value={kpss_pvalue:.4f} "
            "拒绝平稳假设，整体更像趋势非平稳序列。"
        )
    else:
        stationarity_text = (
            f"ADF p-value={adf_pvalue:.4f}，KPSS p-value={kpss_pvalue:.4f}，"
            "两类检验给出的平稳性证据不完全一致，需要结合窗口和频率复核。"
        )

    if _is_finite(hurst) and hurst > 0.55:
        memory_text = f"Hurst={hurst:.4f}，显示较强的持续性和记忆性，价格变化更容易沿原方向延续。"
    elif _is_finite(hurst) and hurst < 0.45:
        memory_text = f"Hurst={hurst:.4f}，显示反持续性，序列更接近均值回复或震荡修复。"
    elif _is_finite(hurst):
        memory_text = f"Hurst={hurst:.4f}，接近随机游走区间，单独依赖记忆性证据需要谨慎。"
    else:
        memory_text = "Hurst 未能稳定估计，当前样本不适合单独用记忆性判断投研方向。"

    if "strong trend" in trend_type:
        trend_text = (
            f"最新窗口被分类为 `{trend_type}`，这是由 Hurst={hurst:.4f}、"
            f"ADF p-value={adf_pvalue:.4f} 和 KPSS p-value={kpss_pvalue:.4f} "
            "共同判断出的趋势性证据，适合先从趋势状态切入。"
        )
    elif "conflicting" in trend_type:
        trend_text = (
            f"最新窗口被分类为 `{trend_type}`，Hurst/ADF/KPSS 给出的趋势性证据不一致，"
            "需要加入状态过滤条件。"
        )
    elif "mean-reverting" in trend_type:
        trend_text = (
            f"最新窗口被分类为 `{trend_type}`，趋势延续证据较弱，更适合关注反转和偏离修复。"
        )
    else:
        trend_text = (
            f"最新窗口被分类为 `{trend_type}`，趋势性不够明确，应谨慎使用单一趋势假设。"
        )

    distribution_text = (
        f"KDE/QQ 显示主要尾部特征为 `{tail_feature}`，偏度特征为 `{skew_feature}`"
        f"，最大 QQ 偏离约为 {max_qq_deviation:.4f}。"
        "这说明分布形态会影响止损、仓位和风险预算设计。"
    )

    if "strong trend" in trend_type:
        one_sentence = "该序列呈现较明显的趋势性和非平稳特征，优先作为趋势类投研方向的候选对象。"
    elif _is_finite(hurst) and hurst < 0.5 and adf_stationary:
        one_sentence = "该序列更接近均值回复或震荡结构，优先作为反转和偏离修复类投研方向的候选对象。"
    else:
        one_sentence = "该序列的检测信号并不单一，适合先做状态识别和风险过滤，再决定具体投研方向。"

    properties = {
        "平稳性分析": stationarity_text,
        "记忆性分析": memory_text,
        "趋势性分析": trend_text,
        "分布形态分析": distribution_text,
    }
    strategy_directions = _strategy_directions(
        hurst=hurst,
        trend_type=trend_type,
        adf_stationary=adf_stationary,
        kpss_stationary=kpss_stationary,
        tail_feature=tail_feature,
    )
    factor_directions = _factor_directions(
        hurst=hurst,
        trend_type=trend_type,
        skew_feature=skew_feature,
        tail_feature=tail_feature,
    )
    caveats = _caveats(
        n_obs=n_obs,
        adf_stationary=adf_stationary,
        kpss_stationary=kpss_stationary,
        tail_feature=tail_feature,
    )
    return TimeSeriesInterpretation(
        summary={
            "one_sentence": one_sentence,
            "n_obs": n_obs,
            "trend_type": trend_type,
        },
        properties=properties,
        strategy_directions=strategy_directions,
        factor_directions=factor_directions,
        caveats=caveats,
    )


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- 无。"


def _build_report_markdown(
    *,
    title: str,
    analysis: TimeSeriesAnalysis,
    interpretation: TimeSeriesInterpretation,
    plot_paths: dict[str, str],
    markdown_dir: Path | None,
) -> str:
    chart_lines: list[str]
    if plot_paths:
        chart_lines = []
        if "kde" in plot_paths:
            chart_lines.extend(["### KDE", "", f"![KDE]({_relative_link(plot_paths['kde'], markdown_dir)})", ""])
        if "qq" in plot_paths:
            chart_lines.extend(["### QQ", "", f"![QQ]({_relative_link(plot_paths['qq'], markdown_dir)})", ""])
    else:
        chart_lines = ["未生成图表。", ""]

    return (
        f"# {title}\n\n"
        "## 一句话结论\n\n"
        f"{interpretation.summary.get('one_sentence', '')}\n\n"
        "## 时间序列性质\n\n"
        "### 平稳性分析\n\n"
        f"{interpretation.properties['平稳性分析']}\n\n"
        "### 记忆性分析\n\n"
        f"{interpretation.properties['记忆性分析']}\n\n"
        "### 趋势性分析\n\n"
        f"{interpretation.properties['趋势性分析']}\n\n"
        "### 分布形态分析\n\n"
        f"{interpretation.properties['分布形态分析']}\n\n"
        "## 量化投研建议\n\n"
        "### 策略方向\n\n"
        f"{_bullets(interpretation.strategy_directions)}\n\n"
        "### 因子方向\n\n"
        f"{_bullets(interpretation.factor_directions)}\n\n"
        "## 检测证据\n\n"
        "### Stationarity / Hurst / ADF / KPSS\n\n"
        f"{_frame_markdown(analysis.stationarity, include_index=False)}\n\n"
        "### KDE / QQ\n\n"
        "#### KDE Diagnostics\n\n"
        f"{_frame_markdown(analysis.distribution.kde)}\n\n"
        "#### QQ Diagnostics\n\n"
        f"{_frame_markdown(analysis.distribution.qq)}\n\n"
        "## 图表\n\n"
        f"{chr(10).join(chart_lines)}\n"
        "## 注意事项\n\n"
        f"{_bullets(interpretation.caveats)}\n"
    )


def generate_time_series_report(
    price: pd.Series,
    *,
    series_name: str = "series",
    title: str | None = None,
    windows: list[int] | None = None,
    lags: list[int] | None = None,
    output_dir: str | Path | None = None,
    include_plots: bool = True,
    language: str = "zh",
) -> TimeSeriesReport:
    """Run diagnostics, interpret results, and optionally write a Markdown report."""

    output_path = Path(output_dir) if output_dir is not None else None
    if output_path is not None:
        output_path.mkdir(parents=True, exist_ok=True)

    analysis = analyze_price_series(
        price,
        windows=windows,
        lags=lags,
        plot=False,
        output_dir=output_path if include_plots else None,
    )
    interpretation = interpret_time_series_analysis(analysis, language=language)
    report_title = title or f"{series_name} 自动时序检测报告"
    plot_paths = dict(analysis.distribution.plot_paths if include_plots else {})
    markdown_path = None
    if output_path is not None:
        markdown_path = output_path / f"{_safe_file_stem(series_name)}_time_series_report.md"
    markdown = _build_report_markdown(
        title=report_title,
        analysis=analysis,
        interpretation=interpretation,
        plot_paths=plot_paths,
        markdown_dir=output_path,
    )
    if markdown_path is not None:
        markdown_path.write_text(markdown, encoding="utf-8")
    return TimeSeriesReport(
        analysis=analysis,
        interpretation=interpretation,
        markdown=markdown,
        markdown_path=markdown_path,
        plot_paths=plot_paths,
    )


__all__ = [
    "generate_time_series_report",
    "interpret_time_series_analysis",
]
