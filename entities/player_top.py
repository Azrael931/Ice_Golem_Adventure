import pygame
import sys
from entities.constante import Resolution

# limite de l'ecran
SCREEN_WIDTH, SCREEN_HEIGHT = Resolution


class Game:
    def __init__(self):
        self.player = Player()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.speed = 2

        sheet = pygame.image.load('../assets/ice_golem_v3_spritesheet.png').convert_alpha()

        frame_width = 80
        frame_height = 80
        scale = 0.75
        frame_count = 5

        self.frames = []
        for i in range(frame_count):
            frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(
                frame,
                (int(frame_width * scale), int(frame_height * scale))
            )
            self.frames.append(frame)

        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100

        self.animation_speed = 0.14
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

        # Limites de l'écran
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

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

game = Game()
all_sprites = pygame.sprite.Group(game.player)

# Boucle principale
running = True
while running:

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # UPDATE
    all_sprites.update()

    # DRAW
    fenetre.blit(fond, (-100, -50))
    all_sprites.draw(fenetre)

    pygame.display.flip()
    horloge.tick(60)

pygame.quit()