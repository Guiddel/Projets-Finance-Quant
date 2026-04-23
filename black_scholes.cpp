/*
 * Black-Scholes European Call Option Pricer & Greeks
 * ====================================================
 * Implémente la CDF et PDF de la loi normale standard
 * sans dépendance externe (uniquement <cmath>).
 */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef M_SQRT1_2
#define M_SQRT1_2 0.70710678118654752440
#endif

#include <cmath>
#include <iostream>
#include <iomanip>
#include <string>
using namespace std;
// ====================================================================
//  Distribution normale standard
// ====================================================================

/**
 * PDF de la loi normale standard : φ(x) = (1/√2π) e^{-x²/2}
 */
double norm_pdf(double x) {
    return (1.0 / sqrt(2.0 * M_PI)) * exp(-0.5 * x * x);
}

/**
 * CDF de la loi normale standard via l'approximation d'Abramowitz & Stegun.
 * Précision : |erreur| < 7.5 × 10⁻⁸
 *
 * On utilise erfc (complementary error function) de <cmath> :
 *   Φ(x) = 0.5 × erfc(-x / √2)
 */
double norm_cdf(double x) {
    return 0.5 * erfc(-x * M_SQRT1_2);
}

// ====================================================================
//  Classe BlackScholes
// ====================================================================

class BlackScholes {
public:
    double S, K, T, r, sigma;
    double d_plus, d_minus;

    /**
     * Constructeur
     * @param S     Prix du sous-jacent
     * @param K     Prix d'exercice (strike)
     * @param T     Temps à l'échéance (années)
     * @param r     Taux sans risque (annualisé)
     * @param sigma Volatilité (annualisée)
     */
    BlackScholes(double S, double K, double T, double r, double sigma)
        : S(S), K(K), T(T), r(r), sigma(sigma)
    {
        double sqrtT = sqrt(T);
        d_plus  = (log(S / K) + (r + 0.5 * sigma * sigma) * T)
                  / (sigma * sqrtT);
        d_minus = d_plus - sigma * sqrtT;
    }

    // === Prix ===

    /** C = S Φ(d₊) - K e^{-rT} Φ(d₋) */
    double price() const {
        return S * norm_cdf(d_plus)
             - K * exp(-r * T) * norm_cdf(d_minus);
    }

    // === Greeks ===

    /** Δ = Φ(d₊) */
    double delta() const {
        return norm_cdf(d_plus);
    }

    /** Γ = φ(d₊) / [σ S √T] */
    double gamma() const {
        return norm_pdf(d_plus) / (sigma * S * sqrt(T));
    }

    /** V = S √T φ(d₊) */
    double vega() const {
        return S * sqrt(T) * norm_pdf(d_plus);
    }

    /** Θ = -σS φ(d₊) / [2√T] - rK e^{-rT} Φ(d₋)   (par an) */
    double theta() const {
        double term1 = -sigma * S * norm_pdf(d_plus) / (2.0 * std::sqrt(T));
        double term2 = -r * K * exp(-r * T) * norm_cdf(d_minus);
        return term1 + term2;
    }

    /** ρ = K T e^{-rT} Φ(d₋) */
    double rho() const {
        return K * T * exp(-r * T) * norm_cdf(d_minus);
    }

    // === Affichage ===

    void print_summary() const {
        auto row = [](const std::string& label, double value) {
            std::cout << "  " << left << setw(20) << label
                      << "= " << right <<setw(12)
                      << fixed << setprecision(6) << value
                      << endl;
        };

        cout << string(55, '=') <<endl;
        cout << "  BLACK-SCHOLES : European Call Option Pricer (C++)" <<endl;
        cout << string(55, '=') <<endl;
        cout << "  S = " << S << "  |  K = " << K << "  |  T = " << T <<endl;
        cout << "  r = " << r << "  |  sigma = " << sigma <<endl;
        cout << string(55, '-') << endl;
        row("d+", d_plus);
        row("d-", d_minus);
        cout << std::string(55, '-') <<endl;
        row("Prix du Call", price());
        row("Delta", delta());
        row("Gamma", gamma());
        row("Vega", vega());
        row("Theta (par an)", theta());
        row("Theta (par jour)", theta() / 365.0);
        row("Rho", rho());
        cout << string(55, '=') <<endl;
    }
};

// ====================================================================
//  Main : exemple d'utilisation
// ====================================================================

int main() {
    
    // test 
   

    // Paramètres
    double S     = 100.0;   // Spot
    double K     = 100.0;   // Strike
    double T     = 1.0;     // Maturité (1 an)
    double r     = 0.05;    // Taux sans risque (5%)
    double sigma = 0.2;     // Volatilité (20%)

    BlackScholes bs(S, K, T, r, sigma);
    
    bs.print_summary();
    

    return 0;
}
