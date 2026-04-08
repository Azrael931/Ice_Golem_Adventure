import math

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





# -------------------------------------------------------
# CALCUL DE VECTEUR VITESSE (BALISTIQUE / PROJECTILES)
# -------------------------------------------------------
def calculer_vecteur_vitesse(origine_x, origine_y, cible_x, cible_y, vitesse_max):
    """
    Calcule le vecteur de vélocité (vx, vy) pour aller d'un point A 
    à un point B avec une vitesse donnée. Utile pour les tirs.
    Retourne le tuple (vx, vy).
    """
    dx = cible_x - origine_x
    dy = cible_y - origine_y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        return vitesse_max, 0.0

    vx = (dx / distance) * vitesse_max
    vy = (dy / distance) * vitesse_max

    return vx, vy
