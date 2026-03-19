import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import *

def lancer_jeu_side(fenetre):
    """Lance le jeu en vue de côté (player_side)"""
    horloge = pygame.time.Clock()
    
    golem_rect = pygame.Rect(player_spawn[0], player_spawn[1], 40, 64)
    vitesse_x = 0 
    vitesse_y = 0 
    sol_rect = pygame.Rect(0, 550, Resolution[0], 20)
    plateforme_rect = pygame.Rect(200, 350, 200, 20)
    
    nb_sauts = 0
    
    running = True 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Retourner False pour quitter le jeu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and nb_sauts < 2:  
                    vitesse_y = -player_jump
                    nb_sauts += 1
                if event.key == pygame.K_ESCAPE:
                    return True  # Retourner True pour revenir au menu

        # LOGIQUE 
        touches = pygame.key.get_pressed()
        vitesse_x = 0 
        #déplacement horizontal
        if touches[pygame.K_LEFT]:
            vitesse_x = -player_speed
        if touches[pygame.K_RIGHT]:
            vitesse_x = player_speed

        golem_rect.x += vitesse_x

        if golem_rect.x < 0:
            golem_rect.x = 0
        if golem_rect.x > Resolution[0] - 40 : 
            golem_rect.x = Resolution[0] - 40 


        # GRAVITÉ
        vitesse_y += gravite
        golem_rect.y += vitesse_y

        if golem_rect.bottom >= sol_rect.top:
            vitesse_y = 0
            golem_rect.bottom = sol_rect.top
            nb_sauts = 0

        if golem_rect.bottom >= plateforme_rect.top and golem_rect.right >= plateforme_rect.left and golem_rect.left <= plateforme_rect.right and vitesse_y > 0 and golem_rect.bottom - vitesse_y <= plateforme_rect.top:
            vitesse_y = 0
            golem_rect.bottom = plateforme_rect.top 
            nb_sauts = 0

        if golem_rect.top < 0: #détection de collision pour le saut pour pas que le golem puisse sortir par le haut
            golem_rect.top = 0
            vitesse_y = 1 #repart vers le bas immédiatement 

        
        

        # DESSIN
        fenetre.fill((30, 30, 40))
        pygame.draw.rect(fenetre, (120, 180, 100), golem_rect)
        pygame.draw.rect(fenetre, (80, 60, 40), sol_rect)
        pygame.draw.rect(fenetre, (80, 60, 40), plateforme_rect)
        
        pygame.display.flip()
        horloge.tick(FPS)
    
    return True

    if golem_rect.x < 0:#détection de collision pour pas que le golem sorte 
        golem_rect.x = 0

    if golem_rect.x > Resolution[0] - 40 : 
        golem_rect.x = Resolution[0] - 40 


   #GRAVITÉ
    vitesse_y += gravite #en python y vers le haut = négatif
    golem_rect.y += vitesse_y

    if golem_rect.bottom >= sol_rect.top:
        vitesse_y = 0
        golem_rect.bottom = sol_rect.top

    if golem_rect.bottom >= plateforme_rect.top and golem_rect.right >= plateforme_rect.left and golem_rect.left <= plateforme_rect.right and vitesse_y > 0 and golem_rect.bottom - vitesse_y <= plateforme_rect.top:
        vitesse_y = 0
        golem_rect.bottom = plateforme_rect.top

    if golem_rect.top < 0: #détection de collision pour le saut
        golem_rect.top = 0
        vitesse_y = 1  # repart vers le bas immédiatement



    #DESSIN
    fenetre.fill((30,30,40))
    pygame.draw.rect(fenetre, (120, 180, 100), golem_rect)
    pygame.draw.rect(fenetre, (80, 60, 40), sol_rect)
    pygame.draw.rect(fenetre, (80, 60, 40), plateforme_rect)

    
    pygame.display.flip()
    horloge.tick(FPS)






    