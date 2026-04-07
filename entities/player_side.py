import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import *
from scenes.game_over import cinematique_mort
#test

# -------------------------------------------------------
# CREATION DE L'ETAT DU JOUEUR (DICTIONNAIRE)
# -------------------------------------------------------
def creer_joueur():
    """Crée et retourne le dictionnaire d'état du joueur."""
    joueur = {}
    joueur["hp"]       = player_hp_max
    joueur["mort"]     = False
    joueur["rect"]     = pygame.Rect(player_spawn[0], player_spawn[1], 40, 64)
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


# -------------------------------------------------------
# BOUCLE PRINCIPALE DU JEU (VUE DE COTE)
# -------------------------------------------------------
def lancer_jeu_side(fenetre):
    """Lance le jeu en vue de côté (player_side).
    Retourne 'menu' pour revenir au menu principal.
    """
    horloge = pygame.time.Clock()

    joueur     = creer_joueur()
    golem_rect = joueur["rect"]

    vitesse_x = 0
    vitesse_y = 0
    sol_rect         = pygame.Rect(0, 550, Resolution[0], 20)
    plateforme_rect  = pygame.Rect(200, 350, 200, 20)

    nb_sauts = 0

    sprite_sheet_droite = pygame.image.load("assets/sprites/golem4.png").convert_alpha()
    sprite_sheet_gauche = pygame.image.load("assets/sprites/golem6.png").convert_alpha()
    frame_actuelle = 0
    compteur = 0

    etat_du_golem = "idle"
    orientation_golem = "droite"


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and nb_sauts < 2:
                    vitesse_y = -player_jump
                    nb_sauts += 1
                if event.key == pygame.K_ESCAPE:
                    return True

                # --- [TEST] Touche T pour infliger 34 dégâts ---
                if event.key == pygame.K_t:
                    infliger_degats(joueur, 34)

        # --- LOGIQUE ---
        touches = pygame.key.get_pressed()
        vitesse_x = 0
        etat_du_golem = "idle" 

        if touches[pygame.K_LEFT]:
            vitesse_x = -player_speed
            etat_du_golem = "marche"
            orientation_golem = "gauche"
        if touches[pygame.K_RIGHT]:
            vitesse_x = player_speed
            etat_du_golem = "marche"
            orientation_golem = "droite"


        golem_rect.x += vitesse_x

        if golem_rect.x < 0:
            golem_rect.x = 0
        if golem_rect.x > Resolution[0] - 40:
            golem_rect.x = Resolution[0] - 40

        # GRAVITE
        vitesse_y += gravite
        golem_rect.y += vitesse_y
        if vitesse_y < 0:
            etat_du_golem = "saut"
        
        compteur += 1
        if compteur >= 10:
            compteur = 0
            frame_actuelle += 1
        if frame_actuelle >= 6:
            frame_actuelle = 0


        if etat_du_golem == "idle":
            ligne_y = 0
        if etat_du_golem == "marche":
            ligne_y = 256
        if etat_du_golem == "saut":
            ligne_y = 512
        if etat_du_golem == "attaque":
            ligne_y = 768

        if orientation_golem == "gauche":
            frame = sprite_sheet_gauche.subsurface(pygame.Rect(frame_actuelle * 256, ligne_y, 256, 256))
        else:
            frame = sprite_sheet_droite.subsurface(pygame.Rect(frame_actuelle * 256, ligne_y, 256, 256))
            
        frame = pygame.transform.scale(frame, (40, 64))

        # Collision sol
        if golem_rect.bottom >= sol_rect.top:
            vitesse_y = 0
            golem_rect.bottom = sol_rect.top
            nb_sauts = 0

        # Collision plateforme
        if (golem_rect.bottom >= plateforme_rect.top
                and golem_rect.right >= plateforme_rect.left
                and golem_rect.left <= plateforme_rect.right
                and vitesse_y > 0
                and golem_rect.bottom - vitesse_y <= plateforme_rect.top):
            vitesse_y = 0
            golem_rect.bottom = plateforme_rect.top
            nb_sauts = 0

        # Empêcher sortie par le haut
        if golem_rect.top < 0:
            golem_rect.top = 0
            vitesse_y = 1

        # -------------------------------------------------------
        # DETECTION DE LA MORT
        # Si le joueur tombe hors de l'ecran par le bas → mort
        # -------------------------------------------------------
        if golem_rect.top > Resolution[1]:
            infliger_degats(joueur, player_hp_max)   # vide les HP

        if joueur["mort"]:
            running = False

        # --- DESSIN ---
        fenetre.fill((30, 30, 40))
        fenetre.blit(frame, (golem_rect.x, golem_rect.y + 10), special_flags=0)
        pygame.draw.rect(fenetre, (80, 60, 40), sol_rect)
        pygame.draw.rect(fenetre, (80, 60, 40), plateforme_rect)

        # Barre de vie
        dessiner_barre_de_vie(fenetre, joueur)

        pygame.display.flip()
        horloge.tick(FPS)

    # -------------------------------------------------------
    # LANCEMENT DE LA CINEMATIQUE DE MORT
    # -------------------------------------------------------
    if joueur["mort"]:
        cinematique_mort(fenetre)
        return True   # Retour au menu après la cinématique

    return True