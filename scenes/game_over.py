import pygame
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import Resolution, FPS


# -------------------------------------------------------
# CINEMATIQUE DE MORT
# Affiche l'écran de game over avec fondu et effets visuels.
# Retourne "menu" pour retourner au menu principal.
# -------------------------------------------------------

def cinematique_mort(fenetre):
    """
    Lance la cinématique de mort du joueur.
    Affiche l'image gameover.png avec un fondu rouge dramatique,
    puis attend que le joueur appuie sur une touche.
    Retourne "menu" pour signaler le retour au menu.
    """
    screen_w, screen_h = fenetre.get_size()
    horloge = pygame.time.Clock()

    # --- Chargement de l'image de game over ---
    chemin_go = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ui', 'gameover.png')
    if os.path.exists(chemin_go):
        image_go = pygame.image.load(chemin_go).convert()
        image_go = pygame.transform.scale(image_go, (screen_w, screen_h))
    else:
        image_go = pygame.Surface((screen_w, screen_h))
        image_go.fill((15, 0, 0))

    # Surfaces utilitaires
    fond_noir = pygame.Surface((screen_w, screen_h))
    fond_noir.fill((0, 0, 0))

    voile_rouge = pygame.Surface((screen_w, screen_h))
    voile_rouge.fill((120, 0, 0))

    # Police pour l'indication de retour
    pygame.font.init()
    police_hint = pygame.font.SysFont("Consolas", 16)

    # -------------------------------------------------------
    # PHASE 1 : Eclair rouge (flash court)
    # -------------------------------------------------------
    voile_rouge.set_alpha(200)
    fenetre.fill((0, 0, 0))
    fenetre.blit(voile_rouge, (0, 0))
    pygame.display.flip()
    pygame.time.delay(80)

    for alpha_flash in range(200, 0, -10):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
        voile_rouge.set_alpha(alpha_flash)
        fenetre.fill((0, 0, 0))
        fenetre.blit(voile_rouge, (0, 0))
        pygame.display.flip()
        horloge.tick(FPS)

    # -------------------------------------------------------
    # PHASE 2 : Fade In de l'image game over depuis le noir
    # -------------------------------------------------------
    alpha = 255
    while alpha > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
        alpha -= 4
        if alpha < 0:
            alpha = 0
        fenetre.blit(image_go, (0, 0))
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        pygame.display.flip()
        horloge.tick(FPS)

    # -------------------------------------------------------
    # PHASE 3 : Attente et indication de retour au menu
    # -------------------------------------------------------
    en_attente = True
    while en_attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                en_attente = False

        ticks = pygame.time.get_ticks()
        fenetre.blit(image_go, (0, 0))

        if (ticks // 600) % 2 == 0:
            hint = police_hint.render("[ ESPACE / CLIC ] Retour au menu", True, (150, 100, 100))
            rect_hint = hint.get_rect(center=(screen_w // 2, screen_h - 60))
            fenetre.blit(hint, rect_hint)

        pygame.display.flip()
        horloge.tick(FPS)

    # -------------------------------------------------------
    # PHASE 4 : Fade Out vers le noir
    # -------------------------------------------------------
    alpha = 0
    while alpha < 255:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
        alpha += 6
        if alpha > 255:
            alpha = 255
        fenetre.blit(image_go, (0, 0))
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        pygame.display.flip()
        horloge.tick(FPS)

    return "menu"
