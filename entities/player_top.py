import pygame
import pytmx
import pyscroll
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import Resolution

# Initialisation de Pygame
pygame.init()

class Game:
    def __init__(self):
        self.fenetre = pygame.display.set_mode(Resolution)
        pygame.display.set_caption("Niveau Player Top")

        tmx_path = os.path.join(os.path.dirname(__file__), "..", "assets", "mapdessus.tmx")
        tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        
        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight

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

                # Détection du CLIC DROIT pour l'attaque
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: # 3 correspond au clic droit dans Pygame
                        self.player.attack()

            self.group.update(self.map_width, self.map_height)
            self.group.center(self.player.rect.center)
            self.group.draw(self.fenetre)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 2.5

        # --- CHARGEMENT DES ANIMATIONS ---
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        path_idle = os.path.join(assets_dir, "RagerIdle.png")
        path_move = os.path.join(assets_dir, "RagerMove.png")
        path_attack = os.path.join(assets_dir, "RagerAttack.png")

        # On charge les animations (5 images par défaut)
        self.idle_frames = self.load_animation(path_idle, 32, 32, 5, 2)
        self.move_frames = self.load_animation(path_move, 32, 32, 5, 2)
        self.attack_frames = self.load_animation(path_attack, 32, 32, 5, 2)

        # États
        self.current_animation = self.idle_frames
        self.is_moving = False
        self.is_attacking = False
        self.flip = False

        self.current_frame = 0
        self.image = self.current_animation[0]
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 400

        self.animation_speed = 0.14
        self.timer = 0

    def load_animation(self, path, width, height, count, scale):
        if not os.path.exists(path):
            print(f"ERREUR : Fichier introuvable {path}. Retourne l'animation idle par défaut.")
            return self.idle_frames

        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(count):
            frame = sheet.subsurface((i * width, 0, width, height))
            frame = pygame.transform.scale(frame, (int(width * scale), int(height * scale)))
            frames.append(frame)
        return frames

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            self.timer = 0

    def move(self, map_w, map_h):
        if self.is_attacking:
            return

        keys = pygame.key.get_pressed()
        self.is_moving = False
        move_x, move_y = 0, 0

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            move_x, self.is_moving, self.flip = -self.speed, True, True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x, self.is_moving, self.flip = self.speed, True, False
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            move_y, self.is_moving = -self.speed, True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y, self.is_moving = self.speed, True

        self.rect.x += move_x
        self.rect.y += move_y
        self.rect.x = max(0, min(self.rect.x, map_w - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, map_h - self.rect.height))

    def update(self, map_w, map_h):
        old_animation_set = self.current_animation
        self.move(map_w, map_h)

        target_animation_set = self.idle_frames
        if self.is_attacking:
            target_animation_set = self.attack_frames
        elif self.is_moving:
            target_animation_set = self.move_frames

        if self.current_animation != target_animation_set:
            if not (old_animation_set == self.move_frames and target_animation_set == self.idle_frames):
                self.current_frame = 0
            self.timer = 0
            self.current_animation = target_animation_set

        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame += 1

            if self.is_attacking:
                if self.current_frame >= len(self.attack_frames):
                    self.is_attacking = False
                    self.current_frame = 0
                    self.current_animation = self.idle_frames if not self.is_moving else self.move_frames
                else:
                    self.current_frame %= len(self.attack_frames)
            else:
                self.current_frame %= len(self.current_animation)

        # Appliquer le flip à TOUTES les animations si nécessaire
        image_to_display = self.current_animation[min(self.current_frame, len(self.current_animation)-1)]

        if self.flip:
            self.image = pygame.transform.flip(image_to_display, True, False)
        else:
            self.image = image_to_display

if __name__ == "__main__":
    game = Game()
    game.run()
