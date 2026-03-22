def fmt_dollars(value: float, decimals: int=0) -> str:
    """
    Format a number as a dollar string.
    """
    fmt = f",.{decimals}f"
    return f"${value: {fmt}}"

def fmt_pct(value: float, decimals: int = 1) -> str:
    """
    Format a fraction (0–1 or actual percentage) as a percentage string.
    Automatically detects whether *value* is already in % form.
    """
    if abs(value) <= 1.5:          # treat as a fraction
        return f"{value * 100:.{decimals}f}%"
    return f"{value:.{decimals}f}%"

def fmt_delta_pct(value: float, initial: float, decimals: int = 1) -> str:
    """
    Return a delta percentage string for st.metric *delta* argument.
    """
    if initial == 0:
        return "N/A"
    delta = (value / initial - 1) * 100
    sign  = "+" if delta >= 0 else ""
    return f"{sign}{delta:.{decimals}f}%"

def risk_badge_html(prob_loss: float) -> str:
    """
    Return an HTML badge string indicating the overall risk level based on
    the probability of portfolio loss.
 
        prob_loss < 30%  → LOW    (green)
        30% ≤ prob < 50% → MEDIUM (amber)
        prob ≥ 50%       → HIGH   (red)
    """
    if prob_loss < 0.30:
        return '<span class="badge-low">LOW</span>'
    elif prob_loss < 0.50:
        return '<span class="badge-medium">MEDIUM</span>'
    else:
        return '<span class="badge-high">HIGH</span>'