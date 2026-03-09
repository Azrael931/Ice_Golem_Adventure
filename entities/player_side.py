import pygame
from settings import *
pygame.init()
fenetre = pygame.display.set_mode((800, 600))
horloge = pygame.time.Clock()

golem_rect = pygame.Rect(400, 300, 40, 40)
sol_rect = pygame.Rect(0, 550, 800, 50) 


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    touches = pygame.key.get_pressed()
    ancienne_pos = golem_rect.copy()

    if touches[pygame.K_LEFT]:
        golem_rect.x -= player_speed
    if touches[pygame.K_RIGHT]:
        golem_rect.x += player_speed
    if touches[pygame.K_UP]:
        golem_rect.y -= player_speed
    if touches[pygame.K_DOWN]:
        golem_rect.y += player_speed

    if golem_rect.colliderect(sol_rect):
        golem_rect = ancienne_pos

    if golem_rect.left < 0: golem_rect.left = 0
    if golem_rect.right > 800: golem_rect.right = 800
    if golem_rect.top < 0: golem_rect.top = 0
    if golem_rect.bottom > 600: golem_rect.bottom = 600

    fenetre.fill((50, 50, 50)) 
    pygame.draw.rect(fenetre, (34, 139, 34), sol_rect)
    pygame.draw.rect(fenetre, (173, 216, 230), golem_rect)
    
    pygame.display.flip()
    horloge.tick(60)

pygame.quit()