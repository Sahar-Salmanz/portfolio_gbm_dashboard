#  Assets
ASSET_OPTIONS: dict[str, str] = {
    # US Large Cap
    "AAPL  – Apple":              "AAPL",
    "MSFT  – Microsoft":          "MSFT",
    "GOOGL – Alphabet":           "GOOGL",
    "AMZN  – Amazon":             "AMZN",
    "NVDA  – NVIDIA":             "NVDA",
    "META  – Meta Platforms":     "META",
    "TSLA  – Tesla":              "TSLA",
    "BRK-B – Berkshire Hathaway": "BRK-B",
    "JPM   – JPMorgan Chase":     "JPM",
    "JNJ   – Johnson & Johnson":  "JNJ",
    "V     – Visa":               "V",
    "UNH   – UnitedHealth":       "UNH",
    "XOM   – ExxonMobil":         "XOM",
    "PG    – Procter & Gamble":   "PG",
    "HD    – Home Depot":         "HD",
    "MA    – Mastercard":         "MA",
    "AVGO  – Broadcom":           "AVGO",
    "MRK   – Merck":              "MRK",
    "LLY   – Eli Lilly":          "LLY",
    "CVX   – Chevron":            "CVX",
    # ETFs
    "SPY   – S&P 500 ETF":        "SPY",
    "QQQ   – Nasdaq-100 ETF":     "QQQ",
    "IWM   – Russell 2000 ETF":   "IWM",
    "GLD   – Gold ETF":           "GLD",
    "TLT   – 20yr Treasury ETF":  "TLT",
    "VNQ   – Real Estate ETF":    "VNQ",
    "ARKK  – ARK Innovation ETF": "ARKK",
}

#  Portfolio constraints
MAX_ASSETS: int = 10
MIN_ASSETS: int = 1
 
#  Monte Carlo defaults
HORIZON_OPTIONS: dict[str, int] = {
    "1 month (21 days)":   21,
    "3 months (63 days)":  63,
    "6 months (126 days)": 126,
    "1 year (252 days)":   252,
    "2 years (504 days)":  504,
    "5 years (1260 days)": 1260,
}
 
SIMULATION_OPTIONS: list[int] = [500, 1_000, 2_000, 5_000]
DEFAULT_SIMULATIONS: int       = 1_000
DEFAULT_HORIZON_KEY: str       = "1 year (252 days)"
DEFAULT_HIST_YEARS: int        = 3
 
RISK_FREE_RATE: float = 0.03   # annual, used for Sharpe ratio
TRADING_DAYS:   int   = 252
 
#  Multi-horizon quick comparison rows
MULTI_HORIZON_ROWS: list[tuple[str, int]] = [
    ("1 month",  21),
    ("3 months", 63),
    ("6 months", 126),
    ("1 year",   252),
    ("2 years",  504),
]
MULTI_HORIZON_SIMS: int = 500   # lighter run for the comparison table

#  Colour palette
PALETTE: dict[str, str] = {
    "dark":   "#111827",
    "mid":    "#6b7280",
    "light":  "#e5e7eb",
    "accent": "#2563eb",
    "green":  "#16a34a",
    "red":    "#dc2626",
    "amber":  "#d97706",
    "purple": "#7c3aed",
    "teal":   "#0891b2",
    "pink":   "#db2777",
}
 
# Categorical colours for stacked area / per-asset traces
ASSET_COLORS: list[str] = [
    "#2563eb", "#16a34a", "#d97706",
    "#7c3aed", "#dc2626", "#0891b2",
    "#db2777", "#92400e", "#065f46", "#1e3a5f",
]
 
#  Plotly base layout
PLOT_LAYOUT: dict = dict(
    font_family="sans-serif",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=50, r=30, t=40, b=50),
    xaxis=dict(showgrid=False, linecolor="#e5e7eb", linewidth=1),
    yaxis=dict(gridcolor="#f3f4f6", linecolor="#e5e7eb"),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, font_size=12),
)