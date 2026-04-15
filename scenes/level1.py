import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import *
from entities.player_side import creer_joueur, infliger_degats, gerer_evenements_joueur
from entities.player_side import deplacer_joueur, afficher_joueur, dessiner_barre_de_vie
from entities import platform_sol
from scenes.game_over import cinematique_mort
import pytmx
import pyscroll


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

    # --- Chargement de la map Tiled ---
    tmx_path = os.path.join(os.path.dirname(__file__), "..", "assets", "maps", "niveau1", "mapniveau1.tmx")
    tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
    map_data = pyscroll.data.TiledMapData(tmx_data)
    map_layer = pyscroll.orthographic.BufferedRenderer(map_data, fenetre.get_size(), clamp_camera=True)
    group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=0)

    # --- Dimensions du niveau ---
    largeur_niveau = 3600

    # --- Création du joueur ---
    joueur = creer_joueur()
    joueur["rect"].bottom = 768  # Positionnement au niveau du sol (y=768)
    joueur["rect"].x = 100       # Optionnel : décalage horizontal de départ

    # --- Environnement : sol dynamique basé sur le calque "sol" du TMX ---
    sols = []
    pieges = []
    TUILES_MORTELLES = {30, 31} # ID des différents piques rouges
    
    layer_sol = tmx_data.get_layer_by_name("sol")
    for y in range(tmx_data.height):
        in_solid = False
        start_x = 0
        for x in range(tmx_data.width):
            gid = layer_sol.data[y][x]
            
            if gid in TUILES_MORTELLES:
                if in_solid:
                    rect = pygame.Rect(start_x * tmx_data.tilewidth, y * tmx_data.tileheight, (x - start_x) * tmx_data.tilewidth, tmx_data.tileheight)
                    sols.append(rect)
                    in_solid = False
                
                # Hitbox du piège plus petite (pour ne toucher que la lame du bas)
                r_piege = pygame.Rect(x * tmx_data.tilewidth + 4, y * tmx_data.tileheight + 16, tmx_data.tilewidth - 8, tmx_data.tileheight - 16)
                pieges.append(r_piege)
                
            elif gid != 0:
                if not in_solid:
                    in_solid = True
                    start_x = x
            else:
                if in_solid:
                    rect = pygame.Rect(start_x * tmx_data.tilewidth, y * tmx_data.tileheight, (x - start_x) * tmx_data.tilewidth, tmx_data.tileheight)
                    sols.append(rect)
                    in_solid = False
                    
        if in_solid:
            rect = pygame.Rect(start_x * tmx_data.tilewidth, y * tmx_data.tileheight, (tmx_data.width - start_x) * tmx_data.tilewidth, tmx_data.tileheight)
            sols.append(rect)

    # --- Environnement : parcours parkour (plateformes grises) ---
    plateformes_statiques = [
        platform_sol.creer_plateforme_statique(700, 600, 100, 20, (100, 100, 100), (150, 150, 150)),
        platform_sol.creer_plateforme_statique(950, 500, 100, 20, (100, 100, 100), (150, 150, 150)),
        platform_sol.creer_plateforme_statique(1450, 550, 120, 20, (100, 100, 100), (150, 150, 150)),
        platform_sol.creer_plateforme_statique(1750, 500, 100, 20, (100, 100, 100), (150, 150, 150)),
        platform_sol.creer_plateforme_statique(2100, 550, 100, 20, (100, 100, 100), (150, 150, 150)),
        platform_sol.creer_plateforme_statique(2450, 480, 100, 20, (100, 100, 100), (150, 150, 150)),
    ]
    
    plateformes_mobiles = [
        platform_sol.creer_plateforme_mobile(1150, 450, 100, 16, 2, 200, "horizontal"),
        platform_sol.creer_plateforme_mobile(1950, 400, 80, 16, 1.5, 200, "vertical"),
    ]

    # --- Objet de fin (décalé de +218) ---
    objet_fin = pygame.Rect(3400, 698, 40, 70)

    # --- Chargement de l'image du portail ---
    img_portail = None
    if os.path.exists('assets/maps/portail.png'):
        img_portail = pygame.image.load('assets/maps/portail.png').convert_alpha()
        img_portail = pygame.transform.scale(img_portail, (objet_fin.width, objet_fin.height))

    # --- Font pour indication touche E ---
    pygame.font.init()
    police = pygame.font.SysFont("Consolas", 16, bold=True)

    # --- Boucle de jeu ---
    last_pos = (None, None)
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

        # ---- LIMITES INFERIEURES (Trous) ET PIEGES ----
        if golem_rect.top > 960:
            infliger_degats(joueur, player_hp_max)
            
        for piege in pieges:
            if golem_rect.colliderect(piege):
                infliger_degats(joueur, player_hp_max)
                break

        if joueur["mort"]:
            running = False

        # ---- COLLISIONS ENVIRONNEMENT ----
        # (les collisions utilisent les world coordinates, inchangées)
        
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

        # ---- AFFICHAGE DES COORDONNEES DANS LE TERMINAL ----
        # On affiche uniquement lorsque le joueur bouge
        pos_actuelle = (golem_rect.centerx, golem_rect.bottom)
        if pos_actuelle != last_pos:
            print(f"Joueur : x {golem_rect.centerx} y {golem_rect.bottom}")
            last_pos = pos_actuelle

        # ---- INTERACTION OBJET DE FIN ----
        if golem_rect.colliderect(objet_fin):
            pygame.mixer.music.stop()
            from scenes.cutscene import cinematique_transition_niveau_1
            ok = cinematique_transition_niveau_1(fenetre)
            if not ok:
                return False
            from scenes.level2 import Game
            game = Game()
            game.run()
            return False  # Quitte après level2

        # ---- GESTION CAMERA ----
        camera_x = max(0, min(golem_rect.centerx - Resolution[0] // 2, largeur_niveau - Resolution[0]))
        camera_y = 192  # 960 (hauteur map) - 768 (vue) = 192

        # Centrage du pyscroll sur la vue de la camera_x et un y plus bas pour voir le bas de la map
        center_x = camera_x + Resolution[0] // 2
        center_y = camera_y + Resolution[1] // 2
        group.center((center_x, center_y))

        # ---- DESSIN ----
        fenetre.fill((40, 50, 70))
        group.draw(fenetre)

        # Objet de fin (Portail)
        if img_portail:
            fenetre.blit(img_portail, (objet_fin.x - camera_x, objet_fin.y - camera_y))
        else:
            objet_ecran = pygame.Rect(objet_fin.x - camera_x, objet_fin.y - camera_y, objet_fin.width, objet_fin.height)
            pygame.draw.rect(fenetre, (255, 215, 0), objet_ecran)
            pygame.draw.rect(fenetre, (200, 150, 0), objet_ecran, 2)

        # Plateformes statiques
        for pf in plateformes_statiques:
            platform_sol.dessiner_plateforme_statique(fenetre, pf, camera_x, camera_y)

        # Plateformes mobiles
        j = 0
        while j < len(plateformes_mobiles):
            platform_sol.dessiner_plateforme(fenetre, plateformes_mobiles[j], camera_x, camera_y)
            j += 1

        # Joueur
        afficher_joueur(fenetre, joueur, camera_x, camera_y)



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
