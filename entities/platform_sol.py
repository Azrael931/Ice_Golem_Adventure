import pygame


# -------------------------------------------------------
# CREATION D'UNE PLATEFORME MOBILE (DICTIONNAIRE)
# -------------------------------------------------------
def creer_plateforme_mobile(x, y, largeur, hauteur, vitesse, distance, axe):
    """
    Crée et retourne un dictionnaire représentant une plateforme mobile.

    x, y        : position initiale (coin haut-gauche)
    largeur     : largeur de la plateforme
    hauteur     : hauteur de la plateforme
    vitesse     : vitesse de déplacement (pixels/frame)
    distance    : distance totale du trajet (aller simple)
    axe         : "horizontal" ou "vertical"
    """
    plateforme = {}
    plateforme["rect"]       = pygame.Rect(x, y, largeur, hauteur)
    plateforme["vitesse"]    = vitesse
    plateforme["distance"]   = distance
    plateforme["axe"]        = axe
    plateforme["origine_x"]  = x
    plateforme["origine_y"]  = y
    plateforme["direction"]  = 1       # 1 = aller, -1 = retour
    plateforme["couleur"]    = (100, 140, 180)
    plateforme["contour"]    = (160, 200, 240)
    return plateforme


# -------------------------------------------------------
# MISE A JOUR DU DEPLACEMENT DE LA PLATEFORME
# -------------------------------------------------------
def deplacer_plateforme(plateforme):
    """
    Déplace la plateforme selon son axe et inverse la direction
    lorsqu'elle atteint les bornes de son trajet.
    Retourne le déplacement effectué (dx, dy).
    """
    dx = 0
    dy = 0

    if plateforme["axe"] == "horizontal":
        dx = plateforme["vitesse"] * plateforme["direction"]
        plateforme["rect"].x += dx

        # Vérifier les bornes
        if plateforme["rect"].x >= plateforme["origine_x"] + plateforme["distance"]:
            plateforme["rect"].x = plateforme["origine_x"] + plateforme["distance"]
            plateforme["direction"] = -1
        if plateforme["rect"].x <= plateforme["origine_x"]:
            plateforme["rect"].x = plateforme["origine_x"]
            plateforme["direction"] = 1

    if plateforme["axe"] == "vertical":
        dy = plateforme["vitesse"] * plateforme["direction"]
        plateforme["rect"].y += dy

        # Vérifier les bornes
        if plateforme["rect"].y >= plateforme["origine_y"] + plateforme["distance"]:
            plateforme["rect"].y = plateforme["origine_y"] + plateforme["distance"]
            plateforme["direction"] = -1
        if plateforme["rect"].y <= plateforme["origine_y"]:
            plateforme["rect"].y = plateforme["origine_y"]
            plateforme["direction"] = 1

    return dx, dy


# -------------------------------------------------------
# COLLISION JOUEUR / PLATEFORME MOBILE (4 COTES)
# -------------------------------------------------------
def collision_plateforme_mobile(golem_rect, plateforme, vitesse_y, nb_sauts, dx, dy):
    """
    Gère la collision entre le joueur et une plateforme mobile
    sur les 4 côtés (haut, bas, gauche, droite).

    golem_rect  : rect du joueur
    plateforme  : dictionnaire de la plateforme
    vitesse_y   : vitesse verticale actuelle du joueur
    nb_sauts    : compteur de sauts du joueur
    dx, dy      : déplacement de la plateforme ce frame

    Retourne : vitesse_y, nb_sauts (mis à jour)
    """
    rect_pf = plateforme["rect"]

    # Pas de collision si les rects ne se chevauchent pas
    if not golem_rect.colliderect(rect_pf):
        return vitesse_y, nb_sauts

    # Calculer le chevauchement sur chaque côté
    overlap_gauche = golem_rect.right - rect_pf.left
    overlap_droite = rect_pf.right - golem_rect.left
    overlap_haut   = golem_rect.bottom - rect_pf.top
    overlap_bas    = rect_pf.bottom - golem_rect.top

    # Trouver le plus petit chevauchement pour savoir
    # de quel côté le joueur entre dans la plateforme
    min_overlap = overlap_haut
    cote = "haut"

    if overlap_bas < min_overlap:
        min_overlap = overlap_bas
        cote = "bas"
    if overlap_gauche < min_overlap:
        min_overlap = overlap_gauche
        cote = "gauche"
    if overlap_droite < min_overlap:
        min_overlap = overlap_droite
        cote = "droite"

    # --- Résolution selon le côté ---

    if cote == "haut":
        # Le joueur atterrit sur la plateforme (par le haut)
        golem_rect.bottom = rect_pf.top
        vitesse_y = 0
        nb_sauts = 0
        # Le joueur suit le mouvement de la plateforme
        golem_rect.x += dx
        golem_rect.y += dy

    elif cote == "bas":
        # Le joueur se cogne la tête sous la plateforme
        golem_rect.top = rect_pf.bottom
        if vitesse_y < 0:
            vitesse_y = 1

    elif cote == "gauche":
        # Le joueur se cogne sur le côté gauche de la plateforme
        golem_rect.right = rect_pf.left

    elif cote == "droite":
        # Le joueur se cogne sur le côté droit de la plateforme
        golem_rect.left = rect_pf.right

    return vitesse_y, nb_sauts


# -------------------------------------------------------
# DESSIN DE LA PLATEFORME
# -------------------------------------------------------
def dessiner_plateforme(fenetre, plateforme, camera_x, camera_y):
    """Dessine une plateforme mobile sur l'écran avec décalage caméra."""
    rect_ecran = pygame.Rect(
        plateforme["rect"].x - camera_x,
        plateforme["rect"].y - camera_y,
        plateforme["rect"].width,
        plateforme["rect"].height
    )
    pygame.draw.rect(fenetre, plateforme["couleur"], rect_ecran)
    pygame.draw.rect(fenetre, plateforme["contour"], rect_ecran, 2)


# -------------------------------------------------------
# CREATION D'UNE PLATEFORME STATIQUE
# -------------------------------------------------------
def creer_plateforme_statique(x, y, largeur, hauteur, couleur, contour):
    """Crée et retourne un dictionnaire pour une plateforme statique."""
    pf = {}
    pf["rect"]    = pygame.Rect(x, y, largeur, hauteur)
    pf["couleur"] = couleur
    pf["contour"] = contour
    return pf


# -------------------------------------------------------
# COLLISION JOUEUR / PLATEFORME STATIQUE (4 COTES)
# -------------------------------------------------------
def collision_plateforme_statique(golem_rect, rect_pf, vitesse_y, nb_sauts):
    """
    Gère la collision entre le joueur et un rect statique (4 côtés).
    Retourne : vitesse_y, nb_sauts (mis à jour)
    """
    if not golem_rect.colliderect(rect_pf):
        return vitesse_y, nb_sauts

    overlap_gauche = golem_rect.right - rect_pf.left
    overlap_droite = rect_pf.right - golem_rect.left
    overlap_haut   = golem_rect.bottom - rect_pf.top
    overlap_bas    = rect_pf.bottom - golem_rect.top

    min_overlap = overlap_haut
    cote = "haut"
    if overlap_bas < min_overlap:
        min_overlap = overlap_bas
        cote = "bas"
    if overlap_gauche < min_overlap:
        min_overlap = overlap_gauche
        cote = "gauche"
    if overlap_droite < min_overlap:
        min_overlap = overlap_droite
        cote = "droite"

    if cote == "haut":
        golem_rect.bottom = rect_pf.top
        vitesse_y = 0
        nb_sauts = 0
    elif cote == "bas":
        golem_rect.top = rect_pf.bottom
        if vitesse_y < 0:
            vitesse_y = 1
    elif cote == "gauche":
        golem_rect.right = rect_pf.left
    elif cote == "droite":
        golem_rect.left = rect_pf.right

    return vitesse_y, nb_sauts


# -------------------------------------------------------
# DESSIN D'UNE PLATEFORME STATIQUE
# -------------------------------------------------------
def dessiner_plateforme_statique(fenetre, pf, camera_x, camera_y):
    """Dessine une plateforme statique avec décalage caméra."""
    rect_ecran = pygame.Rect(
        pf["rect"].x - camera_x,
        pf["rect"].y - camera_y,
        pf["rect"].width,
        pf["rect"].height
    )
    pygame.draw.rect(fenetre, pf["couleur"], rect_ecran)
    pygame.draw.rect(fenetre, pf["contour"], rect_ecran, 2)
