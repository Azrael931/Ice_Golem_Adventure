import pygame
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import *


# -------------------------------------------------------
# CREATION D'UN PROJECTILE
# Chaque projectile est un dictionnaire avec :
#   x, y       -> position courante
#   vx, vy     -> vitesse courante (vx=horizontal, vy=vertical)
#   frames_vie -> compteur de durée de vie restante
# -------------------------------------------------------
def creer_projectile(origine_x, origine_y, cible_x, cible_y):
    """
    Crée un projectile lancé depuis (origine_x, origine_y)
    en direction du point (cible_x, cible_y).
    Retourne un dictionnaire représentant le projectile.
    """
    dx = cible_x - origine_x
    dy = cible_y - origine_y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        vx = projectile_vitesse
        vy = 0.0
    else:
        vx = (dx / distance) * projectile_vitesse
        vy = (dy / distance) * projectile_vitesse

    projectile = {}
    projectile["x"]         = float(origine_x)
    projectile["y"]         = float(origine_y)
    projectile["vx"]        = vx
    projectile["vy"]        = vy
    projectile["frames_vie"] = projectile_duree_vie

    return projectile


# -------------------------------------------------------
# MISE A JOUR DE TOUS LES PROJECTILES
# Applique la gravité, déplace, et supprime hors-écran / expirés
# -------------------------------------------------------
def mettre_a_jour_projectiles(projectiles, largeur_ecran, hauteur_ecran):
    """
    Met à jour la liste de projectiles en place :
    - Applique la gravité (physique parabolique)
    - Déplace chaque projectile
    - Supprime les projectiles hors écran ou expirés
    Modifie directement la liste 'projectiles'.
    """
    i = 0
    while i < len(projectiles):
        p = projectiles[i]

        # Physique parabolique : la gravité incurve la trajectoire vers le bas
        p["vy"] += projectile_gravite

        # Déplacement
        p["x"] += p["vx"]
        p["y"] += p["vy"]

        # Décompte de la durée de vie
        p["frames_vie"] -= 1

        # Supprimer si hors écran ou durée de vie épuisée
        hors_ecran = (p["x"] < -20 or p["x"] > largeur_ecran + 20
                      or p["y"] < -20 or p["y"] > hauteur_ecran + 20)
        expire = p["frames_vie"] <= 0

        if hors_ecran or expire:
            del projectiles[i]
        else:
            i += 1


# -------------------------------------------------------
# DESSIN DE TOUS LES PROJECTILES
# -------------------------------------------------------
def dessiner_projectiles(fenetre, projectiles):
    """
    Dessine chaque projectile sous forme d'un cercle bleu glacé
    avec un halo lumineux.
    """
    for p in projectiles:
        cx = int(p["x"])
        cy = int(p["y"])

        # Halo extérieur (légèrement transparent via une surface)
        halo_surf = pygame.Surface((projectile_rayon * 4, projectile_rayon * 4), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (100, 180, 255, 60),
                           (projectile_rayon * 2, projectile_rayon * 2),
                           projectile_rayon * 2)
        fenetre.blit(halo_surf, (cx - projectile_rayon * 2, cy - projectile_rayon * 2))

        # Corps du projectile
        pygame.draw.circle(fenetre, projectile_couleur, (cx, cy), projectile_rayon)

        # Bordure lumineuse
        pygame.draw.circle(fenetre, projectile_contour, (cx, cy), projectile_rayon, 2)


# -------------------------------------------------------
# DETECTION DE COLLISION D'UN PROJECTILE AVEC UN RECT
# -------------------------------------------------------
def projectile_touche_rect(p, rect):
    """
    Retourne True si le projectile p est en collision avec quelque chose.
    """

        #à méditer


    return 
