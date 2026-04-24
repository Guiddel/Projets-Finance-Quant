"""
Pricing d'options américaines par arbre binomial (Cox-Ross-Rubinstein)
======================================================================

L'idée : on découpe le temps en N petits pas.
A chaque pas, le prix peut monter (x u) ou descendre (x d).
On part de la fin (le payoff) et on remonte vers aujourd'hui.
A chaque noeud, on vérifie si c'est mieux d'exercer maintenant
ou d'attendre -> c'est ça qui rend l'option "américaine".
"""

import math


def prix_americain(S, K, T, r, sigma, N, option_type="call"):
    """
    Prix d'une option américaine par arbre binomial.
    
    S     = prix actuel du sous-jacent
    K     = strike
    T     = temps jusqu'à maturité (en années)
    r     = taux sans risque
    sigma = volatilité
    N     = nombre de pas dans l'arbre (plus c'est grand, plus c'est précis)
    option_type = "call" ou "put"
    """
    
    # --- Étape 1 : paramètres de l'arbre ---
    
    dt = T / N                          # durée d'un pas
    u = math.exp(sigma * math.sqrt(dt)) # facteur de hausse
    d = 1 / u                           # facteur de baisse (symétrique)
    p = (math.exp(r * dt) - d) / (u - d)  # proba risque-neutre de monter
    discount = math.exp(-r * dt)        # facteur d'actualisation par pas
    
    # --- Étape 2 : prix du sous-jacent à maturité (dernière colonne de l'arbre) ---
    
    # A maturité, après N pas, le prix peut être :
    #   S * u^N  (si ça a monté N fois)
    #   S * u^(N-1) * d  (si ça a monté N-1 fois et baissé 1 fois)
    #   ...
    #   S * d^N  (si ça a baissé N fois)
    
    prix_final = []
    for i in range(N + 1):
        # i = nombre de baisses
        prix_spot = S * (u ** (N - i)) * (d ** i)
        prix_final.append(prix_spot)
    
    # --- Étape 3 : payoff à maturité ---
    
    valeurs = []
    for i in range(N + 1):
        if option_type == "call":
            payoff = max(prix_final[i] - K, 0)
        else:  # put
            payoff = max(K - prix_final[i], 0)
        valeurs.append(payoff)
    
    # --- Étape 4 : remonter l'arbre (backward induction) ---
    
    # On part de la fin et on remonte pas par pas
    for step in range(N - 1, -1, -1):  # de N-1 jusqu'à 0
        
        nouvelles_valeurs = []
        
        for i in range(step + 1):
            # Prix du sous-jacent à ce noeud
            prix_spot = S * (u ** (step - i)) * (d ** i)
            
            # Valeur si on attend (espérance actualisée)
            valeur_attente = discount * (p * valeurs[i] + (1 - p) * valeurs[i + 1])
            
            # Valeur si on exerce maintenant
            if option_type == "call":
                valeur_exercice = max(prix_spot - K, 0)
            else:
                valeur_exercice = max(K - prix_spot, 0)
            
            # On prend le max des deux : c'est ça la clé de l'option américaine !
            valeur_noeud = max(valeur_attente, valeur_exercice)
            
            nouvelles_valeurs.append(valeur_noeud)
        
        valeurs = nouvelles_valeurs
    
    # À la fin, il ne reste qu'une seule valeur : le prix aujourd'hui
    return valeurs[0]


def prix_europeen(S, K, T, r, sigma, N, option_type="call"):
    """
    Prix d'une option européenne par arbre binomial.
    C'est la même chose mais SANS le max avec l'exercice anticipé.
    """
    
    dt = T / N
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    p = (math.exp(r * dt) - d) / (u - d)
    discount = math.exp(-r * dt)
    
    # Payoff à maturité
    valeurs = []
    for i in range(N + 1):
        prix_spot = S * (u ** (N - i)) * (d ** i)
        if option_type == "call":
            payoff = max(prix_spot - K, 0)
        else:
            payoff = max(K - prix_spot, 0)
        valeurs.append(payoff)
    
    # Backward induction SANS exercice anticipé
    for step in range(N - 1, -1, -1):
        nouvelles_valeurs = []
        for i in range(step + 1):
            valeur = discount * (p * valeurs[i] + (1 - p) * valeurs[i + 1])
            nouvelles_valeurs.append(valeur)
        valeurs = nouvelles_valeurs
    
    return valeurs[0]


# =============================================================
#                    TESTS ET COMPARAISONS
# =============================================================

if __name__ == "__main__":
    
    # Paramètres
    S = 100
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2
    N = 500   # nombre de pas (500 c'est déjà bien)
    
    print("=" * 60)
    print("  PRICING D'OPTIONS AMÉRICAINES (Arbre binomial CRR)")
    print("=" * 60)
    print(f"  S = {S}  |  K = {K}  |  T = {T}")
    print(f"  r = {r}  |  sigma = {sigma}  |  N = {N} pas")
    print("-" * 60)
    
    # --- Call ---
    call_amer = prix_americain(S, K, T, r, sigma, N, "call")
    call_euro = prix_europeen(S, K, T, r, sigma, N, "call")
    
    print(f"\n  CALL :")
    print(f"    Prix américain  = {call_amer:.4f}")
    print(f"    Prix européen   = {call_euro:.4f}")
    print(f"    Différence      = {call_amer - call_euro:.6f}")
    print(f"    --> Les deux sont égaux ! (comme on l'a prouvé)")
    
    # --- Put ---
    put_amer = prix_americain(S, K, T, r, sigma, N, "put")
    put_euro = prix_europeen(S, K, T, r, sigma, N, "put")
    
    print(f"\n  PUT :")
    print(f"    Prix américain  = {put_amer:.4f}")
    print(f"    Prix européen   = {put_euro:.4f}")
    print(f"    Différence      = {put_amer - put_euro:.4f}")
    print(f"    Prime exercice  = {(put_amer - put_euro) / put_euro * 100:.2f}%")
    print(f"    --> L'américain vaut plus (prime d'exercice anticipé)")
    
    # --- Convergence : on regarde comment le prix change avec N ---
    print(f"\n  CONVERGENCE (put américain) :")
    print(f"  {'N':>6s}  |  {'Prix':>10s}")
    print(f"  " + "-" * 22)
    for n in [10, 50, 100, 200, 500, 1000]:
        p = prix_americain(S, K, T, r, sigma, n, "put")
        print(f"  {n:>6d}  |  {p:>10.4f}")
    
    print("=" * 60)
