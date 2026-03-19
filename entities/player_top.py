import pygame
import pytmx
import pyscroll
from entities.constante import Resolution

# limite de l'ecran
SCREEN_WIDTH, SCREEN_HEIGHT = Resolution


class Game:
    def __init__(self):
        self.fenetre = pygame.display.set_mode(Resolution)
        pygame.display.set_caption("Niveau Player Top")

        tmx_data = pytmx.util_pygame.load_pygame("../assets/mapdessus.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.fenetre.get_size())

        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=1)
        self.player = Player()
        self.group.add(self.player)
        self.clock = pygame.time.Clock()
    def run(self):
        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            self.group.update()
            self.group.center(self.player.rect.center)

            self.group.draw(self.fenetre)
            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.speed = 2
        self.sprite_sheet = pygame.image.load('../assets/RagerIdle.png')

        frame_width = 32
        frame_height = 32
        scale = 2
        frame_count = 5

        self.frames = []
        for i in range(frame_count):
            frame = self.sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(
                frame,
                (int(frame_width * scale), int(frame_height * scale))
            )
            frame.set_colorkey((0, 0, 0))
            self.frames.append(frame)

        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100

        self.animation_speed = 0.14
        self.timer = 0

    def get_image(self, x, y):
        image= pygame.Surface([80,80])
        image.blit(self.sprite_sheet, (0, 0), (x, y,80,80))
        return image


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

horloge = pygame.time.Clock()
game=Game()
game.run()

