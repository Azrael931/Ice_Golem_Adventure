import pygame
import os


# ── Constantes de découpe dans le tileset Graveyard_Set ──
STATUE_REPLIEE_X = 16
STATUE_REPLIEE_Y = 224
STATUE_DEPLOYEE_X = 65
STATUE_DEPLOYEE_Y = 224
STATUE_W_REPLIEE = 49
STATUE_H_REPLIEE = 81
STATUE_W_DEPLOYEE = 77
STATUE_H_DEPLOYEE = 81

# ── Distance d'interaction en pixels ────────────────────
DISTANCE_INTERACTION = 120

# ── Vitesse de poussée de la statue (pixels/frame) ──────
VITESSE_POUSSEE = 2

# ── Tolérance pour considérer la statue sur sa cible ────
TOLERANCE_CIBLE = 80


def charger_tileset(chemin):
    """Charge le tileset depuis le chemin donné et le retourne comme Surface Pygame."""
    chemin_absolu = os.path.join(os.path.dirname(__file__), '..', chemin)
    tileset = pygame.image.load(chemin_absolu).convert_alpha()
    return tileset


def extract_sprite(tileset, x, y, w, h):
    """Extrait un sprite rectangulaire depuis le tileset aux coordonnées (x, y) de taille (w, h)."""
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    surface.blit(tileset, (0, 0), (x, y, w, h))
    return surface


def creer_statue(tileset, pos_x, pos_y, echelle=1.0, cible=None):
    """Crée une statue sous forme de dictionnaire.

    Paramètres :
        tileset  -- la surface du tileset chargé
        pos_x    -- position X en pixels sur l'écran / le niveau
        pos_y    -- position Y en pixels sur l'écran / le niveau
        echelle  -- facteur de mise à l'échelle (1.0 = taille originale)
        cible    -- tuple (x, y) de la position cible où la statue se déploie,
                    ou None si pas de cible

    Retourne un dict avec les clés :
        image_repliee, image_deployee, image, rect, ancre, active, cible
    """
    # Extraction des deux sprites depuis le tileset
    img_repliee = extract_sprite(tileset, STATUE_REPLIEE_X, STATUE_REPLIEE_Y, STATUE_W_REPLIEE, STATUE_H_REPLIEE)
    img_deployee = extract_sprite(tileset, STATUE_DEPLOYEE_X, STATUE_DEPLOYEE_Y, STATUE_W_DEPLOYEE, STATUE_H_DEPLOYEE)

    # Mise à l'échelle si nécessaire
    if echelle != 1.0:
        new_w_r = int(STATUE_W_REPLIEE * echelle)
        new_h_r = int(STATUE_H_REPLIEE * echelle)
        new_w_d = int(STATUE_W_DEPLOYEE * echelle)
        new_h_d = int(STATUE_H_DEPLOYEE * echelle)
        img_repliee = pygame.transform.scale(img_repliee, (new_w_r, new_h_r))
        img_deployee = pygame.transform.scale(img_deployee, (new_w_d, new_h_d))

    # On ancre la statue par le centre bas (pieds du socle)
    rect_init = img_repliee.get_rect(topleft=(pos_x, pos_y))
    ancre_x = rect_init.midbottom[0]
    ancre_y = rect_init.midbottom[1]

    # Hitbox de collision = uniquement le socle (tiers inférieur de l'image)
    hb_h = rect_init.height // 3
    hitbox_init = pygame.Rect(
        rect_init.x,
        rect_init.bottom - hb_h,
        rect_init.width,
        hb_h
    )

    statue = {
        "image_repliee": img_repliee,
        "image_deployee": img_deployee,
        "image": img_repliee,           # image courante (ailes repliées par défaut)
        "rect": rect_init,
        "hitbox": hitbox_init,           # hitbox de collision (socle)
        "ancre": (ancre_x, ancre_y),    # point d'ancrage = centre bas du socle
        "active": False,                # True = ailes déployées
        "cible": cible                  # (x, y) cible ou None
    }
    return statue


def est_proche(rect_joueur, rect_statue, distance=DISTANCE_INTERACTION):
    """Vérifie si le joueur est assez proche de la statue pour interagir.

    Calcule la distance entre les centres des deux rectangles.
    Retourne True si la distance est inférieure ou égale au seuil.
    """
    cx_joueur = rect_joueur.centerx
    cy_joueur = rect_joueur.centery
    cx_statue = rect_statue.centerx
    cy_statue = rect_statue.centery

    dx = cx_joueur - cx_statue
    dy = cy_joueur - cy_statue
    dist = (dx * dx + dy * dy) ** 0.5

    return dist <= distance


def interagir_statue(statue, rect_joueur):
    """Gère l'interaction joueur/statue quand la touche E est pressée.

    Si le joueur est proche, bascule l'état actif de la statue
    (ailes repliées <-> ailes déployées).
    Retourne True si l'interaction a eu lieu, False sinon.
    """
    if not est_proche(rect_joueur, statue["rect"]):
        return False

    # Bascule l'état
    statue["active"] = not statue["active"]

    # Met à jour l'image courante et recale le rect sur l'ancre
    if statue["active"]:
        statue["image"] = statue["image_deployee"]
    else:
        statue["image"] = statue["image_repliee"]

    statue["rect"] = statue["image"].get_rect(midbottom=statue["ancre"])

    return True


def pousser_statue(statue, hitbox_joueur):
    """Pousse la statue si le joueur entre en collision avec elle.

    Détecte le côté de collision et pousse la statue dans la direction
    cardinale correspondante (haut, bas, gauche, droite).
    Repousse aussi le joueur pour qu'il ne traverse pas la statue.
    Ne fait rien si la statue est déjà déployée (active).
    Retourne (poussee, correction_x, correction_y) :
        poussee      -- True si la statue a été poussée
        correction_x -- décalage X à appliquer au joueur
        correction_y -- décalage Y à appliquer au joueur
    """
    if statue["active"]:
        return False, 0, 0

    if not hitbox_joueur.colliderect(statue["hitbox"]):
        return False, 0, 0

    sr = statue["hitbox"]
    pr = hitbox_joueur

    # Calcul de la pénétration sur chaque axe
    overlap_gauche = pr.right - sr.left     # joueur vient de la gauche
    overlap_droite = sr.right - pr.left     # joueur vient de la droite
    overlap_haut   = pr.bottom - sr.top     # joueur vient du haut
    overlap_bas    = sr.bottom - pr.top     # joueur vient du bas

    # Trouver le côté avec la plus petite pénétration
    min_overlap = overlap_gauche
    direction = "gauche"

    if overlap_droite < min_overlap:
        min_overlap = overlap_droite
        direction = "droite"
    if overlap_haut < min_overlap:
        min_overlap = overlap_haut
        direction = "haut"
    if overlap_bas < min_overlap:
        min_overlap = overlap_bas
        direction = "bas"

    # Pousser la statue et corriger la position du joueur
    correction_x = 0
    correction_y = 0
    dep_x = 0
    dep_y = 0

    if direction == "gauche":
        # Le joueur pousse depuis la gauche -> statue va à droite
        dep_x = VITESSE_POUSSEE
        correction_x = -(overlap_gauche)
    elif direction == "droite":
        # Le joueur pousse depuis la droite -> statue va à gauche
        dep_x = -VITESSE_POUSSEE
        correction_x = overlap_droite
    elif direction == "haut":
        # Le joueur pousse depuis le haut -> statue va vers le bas
        dep_y = VITESSE_POUSSEE
        correction_y = -(overlap_haut)
    elif direction == "bas":
        # Le joueur pousse depuis le bas -> statue va vers le haut
        dep_y = -VITESSE_POUSSEE
        correction_y = overlap_bas

    # Déplacer la hitbox et le rect image ensemble
    statue["hitbox"].x = statue["hitbox"].x + dep_x
    statue["hitbox"].y = statue["hitbox"].y + dep_y
    statue["rect"].x = statue["rect"].x + dep_x
    statue["rect"].y = statue["rect"].y + dep_y

    # Mise à jour de l'ancre après déplacement
    statue["ancre"] = (statue["rect"].midbottom[0], statue["rect"].midbottom[1])

    return True, correction_x, correction_y


def verifier_cible(statue):
    """Vérifie si la statue a atteint sa position cible.

    Si la statue est sur sa cible, elle se déploie automatiquement.
    Retourne True si la statue vient de se déployer, False sinon.
    """
    if statue["cible"] is None:
        return False
    if statue["active"]:
        return False

    cx = statue["hitbox"].centerx
    cy = statue["hitbox"].centery
    tx = statue["cible"][0]
    ty = statue["cible"][1]

    dx = cx - tx
    dy = cy - ty
    dist = (dx * dx + dy * dy) ** 0.5

    if dist <= TOLERANCE_CIBLE:
        # La statue a atteint sa cible : déploiement automatique
        statue["active"] = True
        statue["image"] = statue["image_deployee"]
        statue["rect"] = statue["image"].get_rect(midbottom=statue["ancre"])
        # Resynchroniser la hitbox sur le nouveau rect
        hb_h = statue["rect"].height // 3
        statue["hitbox"] = pygame.Rect(
            statue["rect"].x,
            statue["rect"].bottom - hb_h,
            statue["rect"].width,
            hb_h
        )
        print("Statue deployee sur sa cible !")
        return True

    return False


def update_statue(statue):
    """Met à jour l'état de la statue à chaque frame.

    Vérifie si la statue a atteint sa cible, puis synchronise l'image.
    """
    # Vérifier si la statue atteint sa cible
    verifier_cible(statue)

    if statue["active"]:
        statue["image"] = statue["image_deployee"]
    else:
        statue["image"] = statue["image_repliee"]

    # Recaler le rect sur le point d'ancre (centre bas) pour éviter le décalage
    statue["rect"] = statue["image"].get_rect(midbottom=statue["ancre"])

    # Resynchroniser la hitbox (tiers inférieur du rect image)
    hb_h = statue["rect"].height // 3
    statue["hitbox"] = pygame.Rect(
        statue["rect"].x,
        statue["rect"].bottom - hb_h,
        statue["rect"].width,
        hb_h
    )


def draw_statue(surface, statue, camera_x=0, camera_y=0):
    """Dessine la statue sur la surface de rendu, décalée par la caméra.

    Paramètres :
        surface  -- la fenêtre / surface Pygame de destination
        statue   -- le dict représentant la statue
        camera_x -- décalage horizontal de la caméra
        camera_y -- décalage vertical de la caméra
    """
    dest_x = statue["rect"].x - camera_x
    dest_y = statue["rect"].y - camera_y
    surface.blit(statue["image"], (dest_x, dest_y))
