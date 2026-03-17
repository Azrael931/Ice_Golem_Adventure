import pygame
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importation des constantes et des scènes
from entities.constante import Resolution
from scenes.cutscene import cinematique_logo
from scenes.menu import menu_principal


def executer_jeu():
    # Initialisation de Pygame
    pygame.init()

    # Création de la fenêtre
    fenetre = pygame.display.set_mode(Resolution)
    pygame.display.set_caption("Ice Golem Adventure")

    # Lancement de la cinématique du logo
    # La fonction retourne False si l'utilisateur quitte pendant la cinématique
    termine_normalement = cinematique_logo(fenetre)

    if termine_normalement:
        # Lancement du menu principal
        menu_principal(fenetre)

    # Quitter proprement
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    executer_jeu()


