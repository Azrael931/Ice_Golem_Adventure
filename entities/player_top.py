import pygame
import sys
from entities.constante import Resolution
class Game:
    def __init__(self):
        self.player=Player()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.speed = 2

        sheet = pygame.image.load('../assets/RagerIdle.png').convert_alpha()

        #  17 frames de 32px (544 / 32 = 17)
        frame_width = 32
        frame_height = 32
        scale=1.5
        frame_count = sheet.get_width() // frame_width  # calcul automatique = 17

        self.frames = []
        for i in range(frame_count):
            frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
            self.frames.append(frame)

        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x=100
        self.rect.y=100
        self.animation_speed = 0.10  #  ralenti pour 17 frames
        self.timer = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def update(self):
        self.move()
        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]


# Initialisation
pygame.init()
fenetre = pygame.display.set_mode(Resolution)
pygame.display.set_caption("Niveau Player Top")
horloge = pygame.time.Clock()

fond = pygame.image.load("../assets/Scene_Overview.png").convert()
game=Game() #  une seule instance et CHARGEMENT DU JEU!
all_sprites = pygame.sprite.Group(game.player)  #  on met player dedans, pas un gem inexistant

# Boucle principale
running = True
while running:

    # 1. EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False


    # 2. UPDATE
    all_sprites.update()

    # 3. DRAW (une seule fois par frame)   plus de double display.flip()
    fenetre.blit(fond, (-100, -50))
    all_sprites.draw(fenetre)

    pygame.display.flip()
    horloge.tick(60)

pygame.quit()
