import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import *


# -------------------------------------------------------
# CREATION DE L'ETAT DU JOUEUR (DICTIONNAIRE)
# -------------------------------------------------------
def creer_joueur():
    """Crée et retourne le dictionnaire d'état du joueur."""
    joueur = {}
    joueur["hp"]       = player_hp_max
    joueur["mort"]     = False
    joueur["rect"]     = pygame.Rect(player_spawn[0], player_spawn[1], 40, 64)
    joueur["vitesse_x"] = 0
    joueur["vitesse_y"] = 0
    joueur["nb_sauts"]  = 0
    joueur["etat"]      = "idle"
    joueur["orientation"] = "droite"
    joueur["frame"]     = 0
    joueur["compteur"]  = 0

    # Chargement des sprites
    joueur["sprite_droite"] = pygame.image.load("assets/sprites/golem4.png").convert_alpha()
    joueur["sprite_gauche"] = pygame.image.load("assets/sprites/golem6.png").convert_alpha()
    return joueur


# -------------------------------------------------------
# INFLIGER DES DEGATS AU JOUEUR
# -------------------------------------------------------
def infliger_degats(joueur, degats):
    """
    Réduit les HP du joueur. Si les HP tombent à 0 ou moins,
    marque le joueur comme mort.
    """
    joueur["hp"] -= degats
    if joueur["hp"] <= 0:
        joueur["hp"] = 0
        joueur["mort"] = True


# -------------------------------------------------------
# GESTION DES EVENEMENTS DU JOUEUR
# -------------------------------------------------------
def gerer_evenements_joueur(joueur, event):
    """
    Traite un événement clavier pour le joueur.
    Retourne 'quitter' si QUIT, 'menu' si ESCAPE, sinon None.
    """
    if event.type == pygame.QUIT:
        return "quitter"

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP and joueur["nb_sauts"] < 2:
            joueur["vitesse_y"] = -player_jump
            joueur["nb_sauts"] += 1
        if event.key == pygame.K_ESCAPE:
            return "menu"

        # --- [TEST] Touche T pour infliger 34 dégâts ---
        if event.key == pygame.K_t:
            infliger_degats(joueur, 34)

    return None


# -------------------------------------------------------
# DEPLACEMENT DU JOUEUR
# -------------------------------------------------------
def deplacer_joueur(joueur, largeur_niveau=Resolution[0]):
    """
    Gère le déplacement horizontal, la gravité et l'animation
    du joueur. Met à jour le dictionnaire joueur.
    """
    touches = pygame.key.get_pressed()
    joueur["vitesse_x"] = 0
    joueur["etat"] = "idle"

    if touches[pygame.K_LEFT]:
        joueur["vitesse_x"] = -player_speed
        joueur["etat"] = "marche"
        joueur["orientation"] = "gauche"
    if touches[pygame.K_RIGHT]:
        joueur["vitesse_x"] = player_speed
        joueur["etat"] = "marche"
        joueur["orientation"] = "droite"

    golem_rect = joueur["rect"]

    # Déplacement horizontal
    golem_rect.x += joueur["vitesse_x"]

    # Limites du niveau (horizontal)
    if golem_rect.x < 0:
        golem_rect.x = 0
    if golem_rect.x > largeur_niveau - 40:
        golem_rect.x = largeur_niveau - 40

    # Gravité
    joueur["vitesse_y"] += gravite
    golem_rect.y += joueur["vitesse_y"]
    if joueur["vitesse_y"] < 0:
        joueur["etat"] = "saut"

    # Limiter sortie par le haut
    if golem_rect.top < 0:
        golem_rect.top = 0
        joueur["vitesse_y"] = 1

    # Animation
    joueur["compteur"] += 1
    if joueur["compteur"] >= 10:
        joueur["compteur"] = 0
        joueur["frame"] += 1
    if joueur["frame"] >= 6:
        joueur["frame"] = 0


# -------------------------------------------------------
# AFFICHAGE DU JOUEUR
# -------------------------------------------------------
def afficher_joueur(fenetre, joueur, camera_x=0, camera_y=0):
    """Dessine le sprite animé du joueur sur la fenêtre avec décalage caméra."""
    # Ligne de la sprite sheet selon l'état
    if joueur["etat"] == "idle":
        ligne_y = 0
    elif joueur["etat"] == "marche":
        ligne_y = 256
    elif joueur["etat"] == "saut":
        ligne_y = 512
    elif joueur["etat"] == "attaque":
        ligne_y = 768
    else:
        ligne_y = 0

    if joueur["orientation"] == "gauche":
        frame = joueur["sprite_gauche"].subsurface(
            pygame.Rect(joueur["frame"] * 256, ligne_y, 256, 256)
        )
    else:
        frame = joueur["sprite_droite"].subsurface(
            pygame.Rect(joueur["frame"] * 256, ligne_y, 256, 256)
        )

    frame = pygame.transform.scale(frame, (40, 64))
    fenetre.blit(frame, (joueur["rect"].x - camera_x, joueur["rect"].y + 10 - camera_y), special_flags=0)


# -------------------------------------------------------
# DESSIN DE LA BARRE DE VIE
# -------------------------------------------------------
def dessiner_barre_de_vie(fenetre, joueur):
    """Dessine une barre de vie en haut à gauche de l'écran."""
    barre_x      = 20
    barre_y      = 20
    barre_largeur = 200
    barre_hauteur = 18
    rayon        = 6
    ratio_hp     = joueur["hp"] / player_hp_max
    largeur_hp   = int(barre_largeur * ratio_hp)

    # Fond de la barre (noir semi-transparent)
    fond_surf = pygame.Surface((barre_largeur + 4, barre_hauteur + 4), pygame.SRCALPHA)
    fond_surf.fill((0, 0, 0, 160))
    fenetre.blit(fond_surf, (barre_x - 2, barre_y - 2))

    # Fond gris (vie perdue)
    pygame.draw.rect(fenetre, (60, 20, 20), (barre_x, barre_y, barre_largeur, barre_hauteur), border_radius=rayon)

    # Barre de vie (couleur selon le niveau de HP)
    if ratio_hp > 0.5:
        couleur_hp = (50, 200, 80)
    elif ratio_hp > 0.25:
        couleur_hp = (220, 180, 0)
    else:
        couleur_hp = (220, 40, 40)

    if largeur_hp > 0:
        pygame.draw.rect(fenetre, couleur_hp, (barre_x, barre_y, largeur_hp, barre_hauteur), border_radius=rayon)

    # Contour
    pygame.draw.rect(fenetre, (180, 220, 255), (barre_x, barre_y, barre_largeur, barre_hauteur), 2, border_radius=rayon)

    # Texte HP
    pygame.font.init()
    police_hp = pygame.font.SysFont("Consolas", 13)
    texte_hp = police_hp.render("{} / {} HP".format(joueur["hp"], player_hp_max), True, (220, 230, 255))
    fenetre.blit(texte_hp, (barre_x + barre_largeur + 8, barre_y + 2))