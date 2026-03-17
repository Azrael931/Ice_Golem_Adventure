import pygame
import sys
import os

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities.constante import Resolution, FPS, fond_menu, bouton_jouer, bouton_jouer_2
from entities.player_side import lancer_jeu_side



def menu_principal(fenetre):
    """
    Affiche le menu principal.
    """
    horloge = pygame.time.Clock()

    # Chargement et adaptation du fond du menu
    fond = pygame.image.load(fond_menu).convert()
    fond = pygame.transform.scale(fond, Resolution)
    fond_rect = fond.get_rect(center=(Resolution[0] // 2, Resolution[1] // 2))
    
    # Chargement et redimensionnement des boutons
    bouton_normal = pygame.image.load(bouton_jouer).convert_alpha()
    bouton_normal = pygame.transform.scale(bouton_normal, (149, 104))
    bouton_hover = pygame.image.load(bouton_jouer_2).convert_alpha()
    bouton_hover = pygame.transform.scale(bouton_hover, (149, 104))
    
    bouton_rect = bouton_normal.get_rect(center=(512, 330))
    bouton_actuel = bouton_normal

    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si le clic est sur le bouton Jouer
                if bouton_rect.collidepoint(event.pos):
                    result = lancer_jeu_side(fenetre)
                    if not result:  # Si le joueur a fermé la fenêtre
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
        
        # Vérifier si la souris est au-dessus du bouton
        souris_pos = pygame.mouse.get_pos()
        if bouton_rect.collidepoint(souris_pos):
            bouton_actuel = bouton_hover
        else:
            bouton_actuel = bouton_normal

        fenetre.blit(fond, fond_rect)
        
        # Afficher le bouton Jouer au centre
        fenetre.blit(bouton_actuel, bouton_rect)

        pygame.display.flip()
        horloge.tick(FPS)
