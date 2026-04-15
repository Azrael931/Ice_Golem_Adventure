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
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()

    # Création de la fenêtre
    fenetre = pygame.display.set_mode(Resolution)
    pygame.display.set_caption("Ice Golem Adventure")

    # Cinématique 1 : Logo avec fondu
    termine_normalement = cinematique_logo(fenetre)


    if termine_normalement:
        # Lancement du menu principal
        menu_principal(fenetre)

    # Quitter proprement
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    executer_jeu()



