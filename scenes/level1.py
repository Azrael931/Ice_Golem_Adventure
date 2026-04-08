import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import *
from entities.player_side import creer_joueur, infliger_degats, gerer_evenements_joueur
from entities.player_side import deplacer_joueur, afficher_joueur, dessiner_barre_de_vie
from entities import platform_sol
from scenes.game_over import cinematique_mort


# -------------------------------------------------------
# BOUCLE PRINCIPALE DU NIVEAU 1 (VUE DE COTE - PARKOUR)
# -------------------------------------------------------
def lancer_niveau_1(fenetre, volume_musique=0.5):
    """Lance le niveau 1 en vue de côté.
    Retourne True pour revenir au menu, False pour quitter.
    """
    horloge = pygame.time.Clock()

    # --- Musique de fond niveau 1 ---
    if os.path.exists('assets/audio/musique_level1.mp3'):
        pygame.mixer.music.load('assets/audio/musique_level1.mp3')
        pygame.mixer.music.set_volume(volume_musique)
        pygame.mixer.music.play(-1)


    # --- Dimensions du niveau ---
    largeur_niveau = 3600

    # --- Création du joueur ---
    joueur = creer_joueur()

    # --- Environnement : sol général (trous possibles si on veut pour le parkour, ici on met un long sol avec des trous) ---
    sols = [
        pygame.Rect(0, 550, 800, 20),
        pygame.Rect(1100, 550, 600, 20),
        pygame.Rect(2300, 550, 600, 20),
        pygame.Rect(3200, 550, 400, 20)
    ]

    # --- Environnement : plateformes statiques ---
    plateformes_statiques = [
        platform_sol.creer_plateforme_statique(300, 450, 100, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(500, 350, 100, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(700, 250, 80, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(1300, 350, 120, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(1600, 250, 100, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(1900, 400, 80, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(2600, 300, 100, 20, (80, 60, 40), (100, 80, 60)),
        platform_sol.creer_plateforme_statique(2900, 200, 100, 20, (80, 60, 40), (100, 80, 60))
    ]

    # --- Environnement : plateformes mobiles ---
    plateformes_mobiles = []
    pf1 = platform_sol.creer_plateforme_mobile(850, 350, 120, 16, 2, 200, "horizontal")
    pf2 = platform_sol.creer_plateforme_mobile(2100, 450, 100, 16, 1.5, 250, "vertical")
    plateformes_mobiles.append(pf1)
    plateformes_mobiles.append(pf2)

    # --- Objet de fin ---
    objet_fin = pygame.Rect(3400, 480, 40, 70)

    # --- Font pour indication touche E ---
    pygame.font.init()
    police = pygame.font.SysFont("Consolas", 16, bold=True)

    # --- Boucle de jeu ---
    running = True
    while running:

        # ---- EVENEMENTS ----
        for event in pygame.event.get():
            resultat = gerer_evenements_joueur(joueur, event)
            if resultat == "quitter":
                return False
            if resultat == "menu":
                return True

        # ---- DEPLACEMENT DU JOUEUR ----
        deplacer_joueur(joueur, largeur_niveau)
        golem_rect = joueur["rect"]

        # ---- LIMITES INFERIEURES (Trous) ----
        if golem_rect.top > Resolution[1]:
            infliger_degats(joueur, player_hp_max)

        if joueur["mort"]:
            running = False

        # ---- COLLISIONS ENVIRONNEMENT ----
        
        # Collision sols
        en_collision_sol = False
        for sol_rect in sols:
            if (golem_rect.bottom >= sol_rect.top
                and golem_rect.right >= sol_rect.left
                and golem_rect.left <= sol_rect.right
                and joueur["vitesse_y"] > 0
                and golem_rect.bottom - joueur["vitesse_y"] <= sol_rect.top + 10):
                joueur["vitesse_y"] = 0
                golem_rect.bottom = sol_rect.top
                joueur["nb_sauts"] = 0
                en_collision_sol = True

        # Collision plateformes statiques
        for pf in plateformes_statiques:
            joueur["vitesse_y"], joueur["nb_sauts"] = platform_sol.collision_plateforme_statique(
                golem_rect, pf["rect"], joueur["vitesse_y"], joueur["nb_sauts"]
            )

        # Collision plateformes mobiles
        i = 0
        while i < len(plateformes_mobiles):
            pf = plateformes_mobiles[i]
            dx_pf, dy_pf = platform_sol.deplacer_plateforme(pf)
            joueur["vitesse_y"], joueur["nb_sauts"] = platform_sol.collision_plateforme_mobile(
                golem_rect, pf, joueur["vitesse_y"], joueur["nb_sauts"], dx_pf, dy_pf
            )
            i += 1

        # ---- INTERACTION OBJET DE FIN ----
        texte_indication = None
        if golem_rect.colliderect(objet_fin):
            texte_indication = police.render("Appuyez sur 'E' pour entrer", True, (255, 255, 255))
            touches = pygame.key.get_pressed()
            if touches[pygame.K_e]:
                pygame.mixer.music.stop()
                from scenes.cutscene import cinematique_transition_niveau_1
                ok = cinematique_transition_niveau_1(fenetre)
                if not ok:
                    pygame.quit()
                    sys.exit()
                from entities.player_top import Game
                game = Game()
                game.run()
                return False  # Quitte après player_top (car player_top calls pygame.quit)

        # ---- GESTION CAMERA ----
        camera_x = max(0, min(golem_rect.centerx - Resolution[0] // 2, largeur_niveau - Resolution[0]))

        # ---- DESSIN ----
        fenetre.fill((40, 50, 70))

        # Sols
        for sol_rect in sols:
            sol_ecran = pygame.Rect(sol_rect.x - camera_x, sol_rect.y, sol_rect.width, sol_rect.height)
            pygame.draw.rect(fenetre, (90, 100, 110), sol_ecran)

        # Plateformes statiques
        for pf in plateformes_statiques:
            platform_sol.dessiner_plateforme_statique(fenetre, pf, camera_x, 0)

        # Plateformes mobiles
        j = 0
        while j < len(plateformes_mobiles):
            platform_sol.dessiner_plateforme(fenetre, plateformes_mobiles[j], camera_x, 0)
            j += 1
            
        # Objet de fin
        objet_ecran = pygame.Rect(objet_fin.x - camera_x, objet_fin.y, objet_fin.width, objet_fin.height)
        pygame.draw.rect(fenetre, (255, 215, 0), objet_ecran)
        pygame.draw.rect(fenetre, (200, 150, 0), objet_ecran, 2)

        # Joueur
        afficher_joueur(fenetre, joueur, camera_x, 0)

        # Indication texte
        if texte_indication:
            fenetre.blit(texte_indication, (golem_rect.x - camera_x - 30, golem_rect.y - 30))

        # Barre de vie
        dessiner_barre_de_vie(fenetre, joueur)

        pygame.display.flip()
        horloge.tick(FPS)

    # ---- CINEMATIQUE DE MORT ----
    if joueur["mort"]:
        pygame.mixer.music.stop()
        cinematique_mort(fenetre)
        return True

    return True
