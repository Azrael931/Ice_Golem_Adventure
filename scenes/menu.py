import pygame
import sys
import os

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities.constante import *
from entities.player_side import lancer_jeu_side
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
    bouton_normalst = pygame.transform.scale(bouton_normalst,(149,104))
    bouton_hoverst = pygame.image.load(bouton_setting).convert_alpha()
    bouton_hoverst = pygame.transform.scale(bouton_hoverst, (149,104))
    
    
    bouton_rect = bouton_normalpl.get_rect(center=(512, 300))
    bouton_actuel2 = bouton_normalpl

    bouton_rect2 = bouton_normalst.get_rect(center=(512, 400))
    bouton_actuel2 = bouton_normalst

    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si le clic est sur le bouton Jouer
                if bouton_rect.collidepoint(event.pos):
                    # Arrêter la musique du menu avant la cinématique
                    pygame.mixer.music.stop()
                    # Lancer la cinématique d'intro
                    ok = cinematique_intro(fenetre)
                    if not ok:
                        pygame.quit()
                        sys.exit()
                    # Lancer directement le niveau 1 après la cinématique
                    result = lancer_jeu_side(fenetre)
                    if not result:  # Si le joueur a fermé la fenêtre
                        pygame.quit()
                        sys.exit()
                    # Retour au menu : relancer la musique
                    pygame.mixer.music.load(musique_menu)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
        
        # Vérifier si la souris est au-dessus du bouton
        souris_pos = pygame.mouse.get_pos()
        if bouton_rect.collidepoint(souris_pos):
            bouton_actuel = bouton_hoverpl
        else:
            bouton_actuel = bouton_normalpl
        
        if bouton_rect2.collidepoint(souris_pos):
            bouton_actuel2 = bouton_hoverst
        else :
            bouton_actuel2 = bouton_normalst
        
        

        fenetre.blit(fond, fond_rect)
        
        # Afficher le bouton Jouer au centre
        fenetre.blit(bouton_actuel, bouton_rect)
        fenetre.blit(bouton_actuel2, bouton_rect2)

        pygame.display.flip()
        horloge.tick(FPS)
