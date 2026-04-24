/*
 * Pricing d'options américaines par arbre binomial (Cox-Ross-Rubinstein)
 * ======================================================================
 *
 * Compile : g++ -std=c++17 -O2 -o american_option american_option.cpp -lm
 * Run     : ./american_option
 *
 * L'idée : on découpe le temps en N petits pas.
 * A chaque pas, le prix peut monter (x u) ou descendre (x d).
 * On part de la fin (le payoff) et on remonte vers aujourd'hui.
 * A chaque noeud, on compare "exercer" vs "attendre".
 */

#include <iostream>
#include <cmath>
#include <vector>
#include <algorithm>  // pour max()
#include <iomanip>
#include <string>

using namespace std;


double prix_americain(double S, double K, double T, double r, double sigma,
                      int N, string option_type)
{
    // --- Étape 1 : paramètres de l'arbre ---
    
    double dt = T / N;
    double u = exp(sigma * sqrt(dt));    // facteur de hausse
    double d = 1.0 / u;                  // facteur de baisse
    double p = (exp(r * dt) - d) / (u - d);  // proba risque-neutre
    double discount = exp(-r * dt);      // actualisation par pas
    
    // --- Étape 2 : payoff à maturité ---
    
    vector<double> valeurs(N + 1);
    
    for (int i = 0; i <= N; i++)
    {
        // i = nombre de baisses
        double prix_spot = S * pow(u, N - i) * pow(d, i);
        
        if (option_type == "call")
            valeurs[i] = max(prix_spot - K, 0.0);
        else
            valeurs[i] = max(K - prix_spot, 0.0);
    }
    
    // --- Étape 3 : remonter l'arbre ---
    
    for (int step = N - 1; step >= 0; step--)
    {
        for (int i = 0; i <= step; i++)
        {
            // Prix du sous-jacent à ce noeud
            double prix_spot = S * pow(u, step - i) * pow(d, i);
            
            // Valeur si on attend
            double valeur_attente = discount * (p * valeurs[i] + (1.0 - p) * valeurs[i + 1]);
            
            // Valeur si on exerce maintenant
            double valeur_exercice;
            if (option_type == "call")
                valeur_exercice = max(prix_spot - K, 0.0);
            else
                valeur_exercice = max(K - prix_spot, 0.0);
            
            // Le max des deux : la clé de l'américain
            valeurs[i] = max(valeur_attente, valeur_exercice);
        }
    }
    
    return valeurs[0];
}


double prix_europeen(double S, double K, double T, double r, double sigma,
                     int N, string option_type)
{
    // Même chose mais SANS le max avec l'exercice
    
    double dt = T / N;
    double u = exp(sigma * sqrt(dt));
    double d = 1.0 / u;
    double p = (exp(r * dt) - d) / (u - d);
    double discount = exp(-r * dt);
    
    vector<double> valeurs(N + 1);
    
    for (int i = 0; i <= N; i++)
    {
        double prix_spot = S * pow(u, N - i) * pow(d, i);
        
        if (option_type == "call")
            valeurs[i] = max(prix_spot - K, 0.0);
        else
            valeurs[i] = max(K - prix_spot, 0.0);
    }
    
    for (int step = N - 1; step >= 0; step--)
    {
        for (int i = 0; i <= step; i++)
        {
            valeurs[i] = discount * (p * valeurs[i] + (1.0 - p) * valeurs[i + 1]);
            // pas de max ici : on ne peut pas exercer avant T
        }
    }
    
    return valeurs[0];
}


int main()
{
    // Paramètres
    double S     = 100.0;
    double K     = 100.0;
    double T     = 1.0;
    double r     = 0.05;
    double sigma = 0.2;
    int N        = 500;
    
    cout << string(60, '=') << endl;
    cout << "  PRICING D'OPTIONS AMERICAINES (Arbre binomial CRR)" << endl;
    cout << string(60, '=') << endl;
    cout << "  S = " << S << "  |  K = " << K << "  |  T = " << T << endl;
    cout << "  r = " << r << "  |  sigma = " << sigma << "  |  N = " << N << " pas" << endl;
    cout << string(60, '-') << endl;
    
    // --- Call ---
    double call_amer = prix_americain(S, K, T, r, sigma, N, "call");
    double call_euro = prix_europeen(S, K, T, r, sigma, N, "call");
    
    cout << fixed << setprecision(4);
    cout << "\n  CALL :" << endl;
    cout << "    Prix americain  = " << call_amer << endl;
    cout << "    Prix europeen   = " << call_euro << endl;
    cout << "    Difference      = " << setprecision(6) << (call_amer - call_euro) << endl;
    cout << "    --> Les deux sont egaux ! (comme on l'a prouve)" << endl;
    
    // --- Put ---
    double put_amer = prix_americain(S, K, T, r, sigma, N, "put");
    double put_euro = prix_europeen(S, K, T, r, sigma, N, "put");
    
    cout << setprecision(4);
    cout << "\n  PUT :" << endl;
    cout << "    Prix americain  = " << put_amer << endl;
    cout << "    Prix europeen   = " << put_euro << endl;
    cout << "    Difference      = " << (put_amer - put_euro) << endl;
    cout << "    Prime exercice  = " << setprecision(2)
         << (put_amer - put_euro) / put_euro * 100 << "%" << endl;
    cout << "    --> L'americain vaut plus (prime d'exercice anticipe)" << endl;
    
    // --- Convergence ---
    cout << setprecision(4);
    cout << "\n  CONVERGENCE (put americain) :" << endl;
    cout << "  " << setw(6) << "N" << "  |  " << setw(10) << "Prix" << endl;
    cout << "  " << string(22, '-') << endl;
    
    int valeurs_N[] = {10, 50, 100, 200, 500, 1000};
    for (int n : valeurs_N)
    {
        double prix = prix_americain(S, K, T, r, sigma, n, "put");
        cout << "  " << setw(6) << n << "  |  " << setw(10) << prix << endl;
    }
    
    cout << string(60, '=') << endl;
    
    return 0;
}
