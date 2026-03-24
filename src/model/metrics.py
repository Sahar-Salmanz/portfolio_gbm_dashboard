from dataclasses import dataclass
 
import numpy as np
import pandas as pd
 
from utils.config import MULTI_HORIZON_ROWS, MULTI_HORIZON_SIMS, RISK_FREE_RATE, TRADING_DAYS
from model.gbm import SimulationResult, gbm_simulation
 
 
@dataclass
class HistoricalMetrics:
    """Risk/return summary computed from historical price data."""
    ann_return:  float   # annualised log-return
    ann_vol:     float   # annualised volatility
    sharpe:      float   # Sharpe ratio (risk-free = RISK_FREE_RATE)
    max_drawdown: float  # maximum drawdown (fraction, ≤ 0)
    total_return: float  # cumulative return over the full period (fraction)
 
 
def compute_historical_metrics(
    prices: pd.DataFrame,
    shares: dict[str, int | float],
    tickers: list[str],
) -> HistoricalMetrics:
    """
    Compute historical portfolio-level risk/return metrics.
 
    Parameters
    ----------
    prices  : pd.DataFrame  — cleaned closing prices
    shares  : dict          — {ticker: n_shares}
    tickers : list[str]     — ordered list of tickers to include
    """
    px        = prices[tickers].dropna()
    share_arr = np.array([shares[t] for t in tickers])
 
    port_val  = (px * share_arr).sum(axis=1)
    log_rets  = np.log(port_val / port_val.shift(1)).dropna()
 
    ann_return   = float(log_rets.mean() * TRADING_DAYS)
    ann_vol      = float(log_rets.std()  * np.sqrt(TRADING_DAYS))
    sharpe       = (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else 0.0
 
    roll_max     = port_val.cummax()
    drawdown     = (port_val - roll_max) / roll_max
    max_drawdown = float(drawdown.min())
 
    total_return = float((port_val.iloc[-1] / port_val.iloc[0]) - 1)
 
    return HistoricalMetrics(
        ann_return   = ann_return,
        ann_vol      = ann_vol,
        sharpe       = sharpe,
        max_drawdown = max_drawdown,
        total_return = total_return,
    )
 
 
def compute_multi_horizon_summary(
    prices: pd.DataFrame,
    shares: dict[str, int | float],
    max_horizon_days: int,
) -> pd.DataFrame:
    """
    Run lightweight simulations across multiple horizons and return a summary table.
 
    Only horizons ≤ max_horizon_days * 2 and ≤ 504 days are included so the table
    stays relevant to the user's selected horizon.
 
    Returns
    -------
    pd.DataFrame with columns: Horizon, P5, P50 (median), P95, Prob. of loss, 95% VaR
    """
    rows: list[dict] = []
 
    for label, horizon_days in MULTI_HORIZON_ROWS:
        if horizon_days > max_horizon_days * 2 or horizon_days > 504:
            continue
 
        result: SimulationResult = gbm_simulation(
            prices       = prices,
            shares       = shares,
            horizon_days = horizon_days,
            n_sims       = MULTI_HORIZON_SIMS,
        )
 
        rows.append({
            "Horizon":       label,
            "P5":            f"${result.p5:,.0f}",
            "P50 (median)":  f"${result.p50:,.0f}",
            "P95":           f"${result.p95:,.0f}",
            "Prob. of loss": f"{result.prob_loss * 100:.1f}%",
            "95% VaR":       f"${result.var_95:,.0f}",
        })
 
    return pd.DataFrame(rows)
 
 
def build_decision_table(result: SimulationResult) -> pd.DataFrame:
    """
    Map simulation percentiles to plain-English decision use-cases.
    Returns a DataFrame ready for st.dataframe().
    """
    initial = result.initial_value
    rows = [
        ("P5  — Severe downside", result.p5,  "Stress test / worst-case reserve"),
        ("P25 — Bad scenario",    result.p25, "Conservative planning floor"),
        ("P50 — Expected outcome",result.p50, "Base case for financial planning"),
        ("P75 — Good scenario",   result.p75, "Optimistic planning ceiling"),
        ("P95 — Best case",       result.p95, "Best-case / aspirational target"),
    ]
    return pd.DataFrame([
        {
            "Percentile":  label,
            "Final value": f"${val:,.0f}",
            "Return":      f"{(val / initial - 1) * 100:.1f}%",
            "Decision use": use,
        }
        for label, val, use in rows
    ])