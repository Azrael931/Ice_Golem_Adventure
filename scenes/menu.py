import pygame
import sys
import os

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities.constante import *
from scenes.level1 import lancer_niveau_1
from scenes.cutscene import cinematique_intro


def menu_principal(fenetre):
    """
    Affiche le menu principal.
    """
    horloge = pygame.time.Clock()

    # Musique de fond du menu
    pygame.mixer.music.load(musique_menu)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # -1 = boucle infinie

    # Chargement et adaptation du fond du menu
    fond = pygame.image.load(fond_menu).convert()
    fond = pygame.transform.scale(fond, Resolution)
    fond_rect = fond.get_rect(center=(Resolution[0] // 2, Resolution[1] // 2))

    # Chargement et redimensionnement des boutons
    bouton_normalpl = pygame.image.load(bouton_jouer).convert_alpha()
    bouton_normalpl = pygame.transform.scale(bouton_normalpl, (149, 104))
    bouton_hoverpl = pygame.image.load(bouton_jouer_2).convert_alpha()
    bouton_hoverpl = pygame.transform.scale(bouton_hoverpl, (149, 104))

    bouton_normalst = pygame.image.load(bouton_setting_2).convert_alpha()
    bouton_normalst = pygame.transform.scale(bouton_normalst, (149, 104))
    bouton_hoverst = pygame.image.load(bouton_setting).convert_alpha()
    bouton_hoverst = pygame.transform.scale(bouton_hoverst, (149, 104))

    bouton_rect = bouton_normalpl.get_rect(center=(512, 300))
    bouton_rect2 = bouton_normalst.get_rect(center=(512, 400))

    # --- Réglages du volume ---
    volume_actuel = 0.5  # valeur entre 0.0 et 1.0

    # Slider : barre + curseur
    slider_largeur = 300
    slider_hauteur = 10
    slider_x = Resolution[0] // 2 - slider_largeur // 2
    slider_y = Resolution[1] // 2
    slider_rect = pygame.Rect(slider_x, slider_y, slider_largeur, slider_hauteur)

    # Curseur du slider
    curseur_rayon = 14
    curseur_x = slider_x + int(volume_actuel * slider_largeur)

    # Police
    police = pygame.font.SysFont("Arial", 32, bold=True)
    police_petite = pygame.font.SysFont("Arial", 22)

    # Bouton Retour (paramètres → menu)
    bouton_normal_retour = pygame.image.load(bouton_retour).convert_alpha()
    bouton_normal_retour = pygame.transform.scale(bouton_normal_retour, (149, 104))
    bouton_hover_retour = pygame.image.load(bouton_retour_2).convert_alpha()
    bouton_hover_retour = pygame.transform.scale(bouton_hover_retour, (149, 104))
    retour_rect = bouton_normal_retour.get_rect(center=(Resolution[0] // 2, slider_y + 80))

    # État : "menu" ou "parametres"
    etat = "menu"
    glissement = False  # True si la souris glisse le curseur

    en_cours = True
    while en_cours:
        souris_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ---- ÉTAT MENU ----
            if etat == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Bouton Jouer
                    if bouton_rect.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        ok = cinematique_intro(fenetre)
                        if not ok:
                            pygame.quit()
                            sys.exit()
                        result = lancer_niveau_1(fenetre)
                        if not result:
                            pygame.quit()
                            sys.exit()
                        # Retour au menu : relancer la musique avec le volume sauvegardé
                        pygame.mixer.music.load(musique_menu)
                        pygame.mixer.music.set_volume(volume_actuel)
                        pygame.mixer.music.play(-1)

                    # Bouton Paramètre → passer à l'écran paramètres
                    if bouton_rect2.collidepoint(event.pos):
                        etat = "parametres"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        en_cours = False

            # ---- ÉTAT PARAMÈTRES ----
            elif etat == "parametres":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Clic sur le curseur du slider
                    dist = ((souris_pos[0] - curseur_x) ** 2 + (souris_pos[1] - (slider_y + slider_hauteur // 2)) ** 2) ** 0.5
                    if dist <= curseur_rayon * 2 or slider_rect.collidepoint(souris_pos):
                        glissement = True

                    # Bouton Retour
                    if retour_rect.collidepoint(event.pos):
                        etat = "menu"

                if event.type == pygame.MOUSEBUTTONUP:
                    glissement = False

                if event.type == pygame.MOUSEMOTION and glissement:
                    # Mettre à jour la position du curseur
                    curseur_x = max(slider_x, min(slider_x + slider_largeur, souris_pos[0]))
                    volume_actuel = (curseur_x - slider_x) / slider_largeur
                    pygame.mixer.music.set_volume(volume_actuel)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        etat = "menu"

        # ---- DESSIN ----
        fenetre.blit(fond, fond_rect)

        if etat == "menu":
            # Effet hover bouton Jouer
            if bouton_rect.collidepoint(souris_pos):
                bouton_actuel = bouton_hoverpl
            else:
                bouton_actuel = bouton_normalpl

            # Effet hover bouton Paramètre
            if bouton_rect2.collidepoint(souris_pos):
                bouton_actuel2 = bouton_hoverst
            else:
                bouton_actuel2 = bouton_normalst

            fenetre.blit(bouton_actuel, bouton_rect)
            fenetre.blit(bouton_actuel2, bouton_rect2)

        elif etat == "parametres":
            # Titre
            titre_surf = police.render("Volume de la musique", True, (255, 255, 255))
            titre_rect = titre_surf.get_rect(center=(Resolution[0] // 2, slider_y - 50))
            fenetre.blit(titre_surf, titre_rect)

            # Pourcentage
            pct = int(volume_actuel * 100)
            pct_surf = police_petite.render("{} %".format(pct), True, (200, 230, 255))
            pct_rect = pct_surf.get_rect(center=(Resolution[0] // 2, slider_y - 20))
            fenetre.blit(pct_surf, pct_rect)

            # Barre du slider (fond gris)
            pygame.draw.rect(fenetre, (80, 80, 100), slider_rect, border_radius=5)

            # Partie remplie (bleue)
            rempli_rect = pygame.Rect(slider_x, slider_y, curseur_x - slider_x, slider_hauteur)
            pygame.draw.rect(fenetre, (100, 180, 255), rempli_rect, border_radius=5)

            # Curseur
            pygame.draw.circle(fenetre, (255, 255, 255), (curseur_x, slider_y + slider_hauteur // 2), curseur_rayon)
            pygame.draw.circle(fenetre, (100, 180, 255), (curseur_x, slider_y + slider_hauteur // 2), curseur_rayon - 4)

            # Bouton Retour
            if retour_rect.collidepoint(souris_pos):
                bouton_actuel_retour = bouton_hover_retour
            else:
                bouton_actuel_retour = bouton_normal_retour
            fenetre.blit(bouton_actuel_retour, retour_rect)

        pygame.display.flip()
        horloge.tick(FPS)
