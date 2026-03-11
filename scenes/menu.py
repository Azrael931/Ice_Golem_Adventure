import pygame
import sys
# On importe les constantes en utilisant le chemin relatif ou absolu
# Ici on suppose que le dossier parent est dans le path
from entities.constante import Resolution, FPS, fond_menu

def menu_principal(fenetre):
    """
    Affiche le menu principal.
    """
    horloge = pygame.time.Clock()
    
    # Chargement du fond du menu
    fond = pygame.image.load(fond_menu).convert()

    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                else:
                    # Pour l'instant, n'importe quelle touche quitte le menu pour tester main.py
                    en_cours = False
        
        fenetre.blit(fond, (0, 0))
        
        # Texte simple
        font = pygame.font.SysFont('Arial', 48)
        texte = font.render("Ice Golem Adventure", True, (255, 255, 255))
        texte_rect = texte.get_rect(center=(Resolution[0] // 2, Resolution[1] // 4))
        fenetre.blit(texte, texte_rect)
        
        font_sm = pygame.font.SysFont('Arial', 24)
        instructions = font_sm.render("Pressez une touche pour commencer", True, (200, 200, 200))
        inst_rect = instructions.get_rect(center=(Resolution[0] // 2, Resolution[1] // 2))
        fenetre.blit(instructions, inst_rect)

        pygame.display.flip()
        horloge.tick(FPS)
