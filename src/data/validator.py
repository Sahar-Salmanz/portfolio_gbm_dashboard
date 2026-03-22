from utils.config import MAX_ASSETS, MIN_ASSETS


def validate_portfolio(entries: list[dict]) -> tuple[bool, str]:
    """
    Validates a list of portfolio entries.
    Check:
        - the number of assets
        - duplicates in assets
        - shares quantity

    :param entries: a list of dictionary entries, each with keys "ticker" (str) and "shares" (int)
    :return: True with empty str if all checks pass, Otherwise False with an error message
    """

    if len(entries) < MIN_ASSETS:
        return False, f"Add at least {MIN_ASSETS} asset."
    
    if len(entries) > MAX_ASSETS:
        return False, f"Maximum {MAX_ASSETS} assets are allowed."
    
    tickers = [e["ticker"] for e in entries] # get the value for tickers in the portfolio

    # Check duplicates
    seen_asset = set()
    for t in tickers:
        if t in seen_asset:
            return False, f"Duplicate ticker detected: {t}. Remove it to update shares."
        
        seen_asset.add(t)

    # Check share quantity
    for e in entries:
        #if not isinstance(e["shares"], (int, float)) or e["shares"] <= 0:
        #    return False, f"Shares for {e["ticker"]} must be a positive number."
        validate_shares(e["shares"])
        
    return True, ""


def validate_shares(shares: int | float) -> tuple[bool, str]:
    if not isinstance(shares, (int, float)):
        return False, f"Shares must be a number."
    
    if shares <= 0:
        return False, f"Shares must be greater than 0."
    
    if shares > 1_000_000:
        return False, "Shares value cannot be greater than 1,000,000."
    
    return True, "" #TODO: check this later