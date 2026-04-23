"""
Black-Scholes European Call Option Pricer & Greeks
====================================================

Formules dérivées dans les notes de cours :

    C   = S Φ(d₊) - K e^{-r(T-t)} Φ(d₋)

    d₊  = [ln(S/K) + (r + σ²/2)(T-t)] / [σ√(T-t)]
    d₋  = d₊ - σ√(T-t)

Greeks :
    Δ (Delta) = Φ(d₊)
    Γ (Gamma) = φ(d₊) / [σ S √(T-t)]
    V (Vega)  = S √(T-t) φ(d₊)
    Θ (Theta) = -σS φ(d₊) / [2√(T-t)] - rK e^{-r(T-t)} Φ(d₋)
    ρ (Rho)   = K(T-t) e^{-r(T-t)} Φ(d₋)

où Φ = CDF normale standard, φ = PDF normale standard.
"""

import math
from scipy.stats import norm


class BlackScholes:
    """Pricer Black-Scholes pour un call européen avec tous les grecs."""

    def __init__(self, S: float, K: float, T: float, r: float, sigma: float):
        """
        Paramètres
        ----------
        S     : Prix du sous-jacent
        K     : Prix d'exercice (strike)
        T     : Temps à l'échéance (en années)
        r     : Taux sans risque (annualisé)
        sigma : Volatilité (annualisée)
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

        # Précalcul de d+ et d-
        self.d_plus = (
            (math.log(S / K) + (r + 0.5 * sigma**2) * T)
            / (sigma * math.sqrt(T))
        )
        self.d_minus = self.d_plus - sigma * math.sqrt(T)

    # === Prix ===
    def price(self) -> float:
        """C = S Φ(d₊) - K e^{-rT} Φ(d₋)"""
        return (
            self.S * norm.cdf(self.d_plus)
            - self.K * math.exp(-self.r * self.T) * norm.cdf(self.d_minus)
        )

    # === Greeks ===
    def delta(self) -> float:
        """Δ = Φ(d₊)"""
        return norm.cdf(self.d_plus)

    def gamma(self) -> float:
        """Γ = φ(d₊) / [σ S √T]"""
        return norm.pdf(self.d_plus) / (self.sigma * self.S * math.sqrt(self.T))

    def vega(self) -> float:
        """V = S √T φ(d₊)   (pour un shift de 1 en σ ; diviser par 100 pour 1%)"""
        return self.S * math.sqrt(self.T) * norm.pdf(self.d_plus)

    def theta(self) -> float:
        """Θ = -σS φ(d₊) / [2√T] - rK e^{-rT} Φ(d₋)   (par an)"""
        term1 = -self.sigma * self.S * norm.pdf(self.d_plus) / (2 * math.sqrt(self.T))
        term2 = -self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(self.d_minus)
        return term1 + term2

    def rho(self) -> float:
        """ρ = K T e^{-rT} Φ(d₋)   (pour un shift de 1 en r ; diviser par 100 pour 1%)"""
        return (
            self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(self.d_minus)
        )

    def summary(self) -> dict:
        """Retourne un dictionnaire avec tous les résultats."""
        return {
            "Prix du Call": self.price(),
            "Delta": self.delta(),
            "Gamma": self.gamma(),
            "Vega": self.vega(),
            "Theta (par an)": self.theta(),
            "Theta (par jour)": self.theta() / 365,
            "Rho": self.rho(),
        }


# ====================================================================
#                        EXEMPLE D'UTILISATION
# ====================================================================
if __name__ == "__main__":
    # Paramètres
    S = 100       # Spot
    K = 100       # Strike
    T = 1         # Maturité (1 an)
    r = 0.05      # Taux sans risque (5%)
    sigma = 0.2   # Volatilité (20%)

    bs = BlackScholes(S, K, T, r, sigma)

    print("=" * 55)
    print("  BLACK-SCHOLES : European Call Option Pricer")
    print("=" * 55)
    print(f"  S = {S}  |  K = {K}  |  T = {T}")
    print(f"  r = {r}  |  σ = {sigma}")
    print("-" * 55)
    print(f"  d₊            = {bs.d_plus:>12.6f}")
    print(f"  d₋            = {bs.d_minus:>12.6f}")
    print("-" * 55)

    results = bs.summary()
    for name, value in results.items():
        print(f"  {name:<18s} = {value:>12.6f}")

    print("=" * 55)
