import pygame 
from constante import *
pygame.init() #démarrer le moteur de pygame
fenetre = pygame.display.set_mode(Resolution)
horloge = pygame.time.Clock()#crée un objet horloge qui va me permettre de contrôler le nombre de frames par seconde


golem_rect = pygame.Rect(player_spawn[0], player_spawn[1], 40, 64) #pygame.Rect(x, y, largeur, hauteur)
vitesse_x = 0 
vitesse_y = 0 
sol_rect = pygame.Rect(0, 550, Resolution[0], 20)
plateforme_rect = pygame.Rect(200, 350, 200, 20)

running = True 
while running :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                vitesse_y = -player_jump

    #LOGIQUE 
    touches = pygame.key.get_pressed()

    vitesse_x = 0 

    if touches[pygame.K_LEFT]:
        vitesse_x = -player_speed
    if touches[pygame.K_RIGHT]:
        vitesse_x = player_speed

    golem_rect.x += vitesse_x

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


# fenetre.fill((R, G, B)) — efface l'écran à chaque frame
# pygame.draw.rect(surface, couleur_RGB, rect) — dessine un rectangle
# pygame.display.flip() — affiche tout ce qui a été dessiné en coulisses
# horloge.tick(FPS) — bloque le jeu à 60 FPS








