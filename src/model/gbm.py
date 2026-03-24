from dataclasses import dataclass, field
 
import numpy as np
import pandas as pd
 
from utils.config import RISK_FREE_RATE, TRADING_DAYS


@dataclass
class SimulationResult:
    # Raw paths
    paths: np.ndarray             # shape (n_sims, T+1) — portfolio value
    final_values: np.ndarray      # shape (n_sims,)
 
    # Portfolio baseline
    initial_value: float
    tickers: list[str]
    horizon_days: int
    n_sims: int

    # Percentiles of final portfolio value
    p5:  float
    p25: float
    p50: float
    p75: float
    p95: float
    mean: float
    std:  float
 
    # Risk metrics
    var_95:  float    # 95% Value at Risk  (loss in $)
    cvar_95: float    # 95% Conditional VaR / Expected Shortfall
 
    # Probability metrics
    prob_loss: float  # P(final < initial)
    prob_2x:   float  # P(final >= 2 × initial)
 
    # Return & risk-adjusted metrics
    cagr_p50: float   # CAGR implied by median outcome
    sharpe:   float   # annualised Sharpe (risk-free subtracted)
 
    # Drawdown distribution (sampled subset of sims)
    max_dds: np.ndarray   # shape (min(n_sims, 500),)
 
    # Correlation / return data (for heatmap & diagnostics)
    log_returns: pd.DataFrame
    corr_matrix: pd.DataFrame


def gbm_simulation(prices, shares, horizon_days, n_sims=1000, dt=1/TRADING_DAYS, random_seed=42):
    tickers = list(shares.keys())
    px = prices[tickers].dropna()
    n_assets = len(tickers)
    T = horizon_days

    # Parameter estimation from historical data
    log_returns = np.log(px / px.shift(1)).dropna()
    mu = log_returns.mean().values          # (n_assets,) daily mean log-return
    cov         = log_returns.cov().values           # (n_assets, n_assets) daily cov matrix
    S0          = px.iloc[-1].values                 # (n_assets,) last observed prices

    # Cholesky decomposition for correlated noise
    try:
        L = np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        # Regularise if the matrix is not positive-definite (can happen with short history)
        cov_reg = cov + np.eye(n_assets) * 1e-8
        L = np.linalg.cholesky(cov_reg)
 
    # Simulate price paths
    # paths shape: (n_sims, T+1, n_assets)
    asset_paths = np.zeros((n_sims, T + 1, n_assets))
    asset_paths[:, 0, :] = S0
 
    rng         = np.random.default_rng(random_seed)
    drift       = (mu - 0.5 * np.diag(cov)) * dt    # (n_assets,)
    sqrt_dt     = np.sqrt(dt)
 
    for t in range(1, T + 1):
        Z_iid    = rng.standard_normal((n_sims, n_assets))
        Z_corr   = Z_iid @ L.T                        # correlate via Cholesky
        shock    = drift + Z_corr * sqrt_dt
        asset_paths[:, t, :] = asset_paths[:, t - 1, :] * np.exp(shock)
 
    # Aggregate to portfolio value
    share_arr       = np.array([shares[t] for t in tickers])   # (n_assets,)
    portfolio_paths = (asset_paths * share_arr).sum(axis=2)     # (n_sims, T+1)
    final_values    = portfolio_paths[:, -1]                    # (n_sims,)
 
    # Compute metrics
    initial_value = float((S0 * share_arr).sum())
    p5, p25, p50, p75, p95 = np.percentile(final_values, [5, 25, 50, 75, 95])
 
    losses   = initial_value - final_values
    var_95   = float(np.percentile(losses, 95))
    cvar_95  = float(losses[losses >= var_95].mean())
 
    prob_loss = float((final_values < initial_value).mean())
    prob_2x   = float((final_values >= 2 * initial_value).mean())
 
    years    = T / TRADING_DAYS
    cagr_p50 = float((p50 / initial_value) ** (1 / years) - 1) if years > 0 else 0.0
 
    rf_daily   = RISK_FREE_RATE / TRADING_DAYS
    ret_paths  = np.diff(np.log(portfolio_paths), axis=1)        # (n_sims, T)
    excess     = ret_paths.mean(axis=1) - rf_daily
    sharpe     = float((excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS)) \
                 if excess.std() > 0 else 0.0
 
    # Max drawdown distribution (sampled subset for performance)
    sample_size = min(n_sims, 500)
    sample_idx  = rng.choice(n_sims, size=sample_size, replace=False)
    max_dds     = np.array([_max_drawdown(portfolio_paths[i]) for i in sample_idx])
 
    return SimulationResult(
        paths         = portfolio_paths,
        final_values  = final_values,
        initial_value = initial_value,
        tickers       = tickers,
        horizon_days  = T,
        n_sims        = n_sims,
        p5=float(p5), p25=float(p25), p50=float(p50), p75=float(p75), p95=float(p95),
        mean          = float(final_values.mean()),
        std           = float(final_values.std()),
        var_95        = var_95,
        cvar_95       = cvar_95,
        prob_loss     = prob_loss,
        prob_2x       = prob_2x,
        cagr_p50      = cagr_p50,
        sharpe        = sharpe,
        max_dds       = max_dds,
        log_returns   = log_returns,
        corr_matrix   = log_returns.corr(),
    )
 
 
#  Private helpers
def _max_drawdown(path: np.ndarray) -> float:
    """Return the maximum drawdown (as a fraction, ≤ 0) for a single value path."""
    roll_max = np.maximum.accumulate(path)
    drawdown = (path - roll_max) / roll_max
    return float(drawdown.min())