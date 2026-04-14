

# -------------------------------------------------------
# APPLICATION DE LA GRAVITE
# -------------------------------------------------------
def appliquer_gravite(vitesse_y, constante_gravite, vitesse_max_chute=15):
    """
    Applique la gravité à une vitesse verticale et la limite 
    pour éviter de traverser le sol (terminal velocity).
    Retourne la nouvelle vitesse_y.
    """
    vitesse_y += constante_gravite
    if vitesse_y > vitesse_max_chute:
        vitesse_y = vitesse_max_chute
    return vitesse_y
