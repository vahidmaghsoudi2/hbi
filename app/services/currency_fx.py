"""HBI C-01 locked currency helpers.

USD = canonical base currency.
R = fx_rate_usd_to_irr = IRR per 1 USD.
1 Toman = 10 IRR.

  amount_irr = amount_usd * R
  amount_toman = amount_irr / 10
  amount_usd = amount_irr / R
  amount_irr = amount_toman * 10

Rates are never invented; callers must supply R > 0.
"""
from __future__ import annotations


def validate_fx_rate(fx_rate_usd_to_irr: float) -> float:
    if fx_rate_usd_to_irr is None:
        raise ValueError("fx_rate_usd_to_irr is required (never invented)")
    rate = float(fx_rate_usd_to_irr)
    if rate <= 0:
        raise ValueError("fx_rate_usd_to_irr must be > 0")
    return rate


def usd_to_irr(amount_usd: float, fx_rate_usd_to_irr: float) -> float:
    r = validate_fx_rate(fx_rate_usd_to_irr)
    return float(amount_usd) * r


def irr_to_usd(amount_irr: float, fx_rate_usd_to_irr: float) -> float:
    r = validate_fx_rate(fx_rate_usd_to_irr)
    return float(amount_irr) / r


def irr_to_toman(amount_irr: float) -> float:
    return float(amount_irr) / 10.0


def toman_to_irr(amount_toman: float) -> float:
    return float(amount_toman) * 10.0


def usd_to_toman(amount_usd: float, fx_rate_usd_to_irr: float) -> float:
    return irr_to_toman(usd_to_irr(amount_usd, fx_rate_usd_to_irr))


def toman_to_usd(amount_toman: float, fx_rate_usd_to_irr: float) -> float:
    return irr_to_usd(toman_to_irr(amount_toman), fx_rate_usd_to_irr)
