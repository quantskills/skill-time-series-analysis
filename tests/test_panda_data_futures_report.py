from __future__ import annotations

import os
from pathlib import Path

import matplotlib
import pandas as pd
import pytest

from skill_time_series_analysis import analyze_price_series, build_time_series_factor_frame

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "panda_data_futures"
REPORT_MD = REPORT_DIR / "multi_symbol_futures_timeseries.md"
FACTOR_CSV = REPORT_DIR / "multi_symbol_factors_tail.csv"
SYMBOLS = ["IF_DOMINANT.CFE", "CU_DOMINANT.SHF", "I_DOMINANT.DCE"]
START_DATE = "20240101"
END_DATE = "20241231"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _panda_data_credentials() -> tuple[str, str]:
    env_file = os.environ.get("PANDA_DATA_ENV_FILE")
    if env_file:
        _load_env_file(Path(env_file))
    _load_env_file(ROOT / ".env")

    username = os.environ.get("PANDA_DATA_USERNAME", "")
    password = os.environ.get("PANDA_DATA_PASSWORD", "")
    if not username or not password:
        pytest.skip("PANDA_DATA_USERNAME and PANDA_DATA_PASSWORD are required")
    return username, password


def _fetch_futures_bars() -> pd.DataFrame:
    panda_data = pytest.importorskip("panda_data")
    username, password = _panda_data_credentials()
    panda_data.init_token(username=username, password=password)
    raw = panda_data.get_market_data(
        symbol=SYMBOLS,
        start_date=START_DATE,
        end_date=END_DATE,
        type="future",
        fields=["symbol", "date", "open", "high", "low", "close", "volume"],
    )
    if raw.empty:
        raise AssertionError("PandaData returned no futures bars")

    bars = raw.copy()
    bars.columns = [str(column).lower() for column in bars.columns]
    if "date" not in bars.columns or "symbol" not in bars.columns:
        raise AssertionError(f"missing expected PandaData columns: {bars.columns.tolist()}")
    bars["date"] = pd.to_datetime(bars["date"].astype(str), format="%Y%m%d")
    bars = bars.sort_values(["symbol", "date"]).set_index("date")
    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(bars.columns)
    if missing:
        raise AssertionError(f"missing OHLCV columns: {sorted(missing)}")
    return bars


def _frame_to_markdown(frame: pd.DataFrame) -> str:
    rows = ["| " + " | ".join(frame.columns) + " |", "| " + " | ".join("---" for _ in frame.columns) + " |"]
    for _, row in frame.iterrows():
        rows.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(rows)


@pytest.mark.integration
def test_real_panda_data_multi_symbol_futures_report() -> None:
    bars = _fetch_futures_bars()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    factor_frames = []
    report_sections = [
        "# PandaData Futures Time-Series Analysis",
        "",
        "- Data source: PandaData `get_market_data`, type=`future`.",
        f"- Date range: `{START_DATE}` to `{END_DATE}`.",
        f"- Symbols: {', '.join(f'`{symbol}`' for symbol in SYMBOLS)}.",
        "",
    ]

    for symbol in SYMBOLS:
        symbol_bars = bars[bars["symbol"] == symbol]
        assert len(symbol_bars) >= 180, f"{symbol} needs at least 180 daily bars"

        symbol_report_dir = REPORT_DIR / symbol.replace(".", "_")
        analysis = analyze_price_series(
            symbol_bars["close"],
            windows=[60, 120, 180],
            lags=[1, 5, 20],
            plot=False,
            output_dir=symbol_report_dir,
        )
        factors = build_time_series_factor_frame(symbol_bars, lookback=20).tail(5).copy()
        factors.insert(0, "symbol", symbol)
        factor_frames.append(factors.reset_index())

        summary_rows.append(
            {
                "symbol": symbol,
                "n_obs": analysis.summary["n_obs"],
                "trend_score": analysis.summary["trend_score"],
                "trend_type": analysis.summary["trend_type"],
                "tail": analysis.summary["primary_tail_feature"],
                "skew": analysis.summary["primary_skew_feature"],
            }
        )

        report_sections.extend(
            [
                f"## {symbol}",
                "",
                analysis.to_markdown(),
                "",
                "### Generated Charts",
                "",
                f"![KDE]({symbol.replace('.', '_')}/distribution_kde_dist.png)",
                "",
                f"![QQ]({symbol.replace('.', '_')}/distribution_qq_plot.png)",
                "",
            ]
        )

    summary = pd.DataFrame(summary_rows)
    factors_tail = pd.concat(factor_frames, ignore_index=True)
    factors_tail.to_csv(FACTOR_CSV, index=False)

    report = "\n".join(
        [
            report_sections[0],
            *report_sections[1:6],
            "## Cross-Symbol Summary",
            "",
            _frame_to_markdown(summary),
            "",
            *report_sections[6:],
            "## Factor Snapshot",
            "",
            f"Latest factor rows are saved at `{FACTOR_CSV.relative_to(REPORT_DIR)}`.",
            "",
        ]
    )
    REPORT_MD.write_text(report, encoding="utf-8")

    assert REPORT_MD.exists()
    assert FACTOR_CSV.exists()
    assert set(summary["symbol"]) == set(SYMBOLS)
    assert factors_tail["symbol"].nunique() == len(SYMBOLS)
    for symbol in SYMBOLS:
        symbol_dir = REPORT_DIR / symbol.replace(".", "_")
        assert (symbol_dir / "distribution_kde_dist.png").exists()
        assert (symbol_dir / "distribution_qq_plot.png").exists()
