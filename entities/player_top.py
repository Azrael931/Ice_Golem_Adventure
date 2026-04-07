import pygame
import pytmx
import pyscroll
import sys
import os

# Configuration du chemin pour l'import des constantes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import Resolution

# Initialisation de Pygame
pygame.init()

def load_animation(path, cols, rows, scale=1.0, target_size=None):
    """Fonction universelle pour charger et découper une sprite sheet"""
    if not os.path.exists(path):
        return [pygame.Surface((32, 32), pygame.SRCALPHA)]
    
    sheet = pygame.image.load(path).convert_alpha()
    frame_w, frame_h = sheet.get_width() // cols, sheet.get_height() // rows
    frames = []
    for row in range(rows):
        for col in range(cols):
            frame = sheet.subsurface((col * frame_w, row * frame_h, frame_w, frame_h))
            if target_size:
                frame = pygame.transform.scale(frame, target_size)
            elif scale != 1.0:
                frame = pygame.transform.scale(frame, (int(frame_w * scale), int(frame_h * scale)))
            frames.append(frame)
    return frames

# ==========================================
# CLASSE JOUEUR (Golem)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 5
        sprites_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
        
        target = (400, 250)
        self.idle_frames = load_animation(os.path.join(sprites_dir, "golem_idle.png"), 4, 4, target_size=target)
        self.move_frames = load_animation(os.path.join(sprites_dir, "golem_move.png"), 4, 4, target_size=target)
        self.at1_frames  = load_animation(os.path.join(sprites_dir, "golem_attack1.png"), 5, 4, target_size=target)
        self.at2_frames  = load_animation(os.path.join(sprites_dir, "golem_attack2.png"), 6, 6, target_size=target)

        self.current_animation = self.idle_frames
        self.is_moving = False
        self.is_attacking = False
        self.attack_type = None 
        self.flip = False

        self.current_frame = 0
        self.image = self.current_animation[0]
        self.rect  = self.image.get_rect()
        
        # Position initiale (Ajustée pour être dans le château)
        self.position = [700, 700]
        self.rect.center = self.position
        
        # Hitbox logique réelle aux pieds du Golem pour les collisions
        self.hitbox = pygame.Rect(0, 0, 50, 30)
        self.update_hitbox()

        self.animation_speed = 0.17
        self.timer = 0

    def update_hitbox(self):
        """Met à jour la position de la hitbox par rapport aux pieds du Golem"""
        self.hitbox.center = (self.position[0], self.position[1] + 60)

    def attack1(self):
        if not self.is_attacking: self.is_attacking, self.attack_type, self.current_frame, self.timer = True, 1, 0, 0
    def attack2(self):
        if not self.is_attacking: self.is_attacking, self.attack_type, self.current_frame, self.timer = True, 2, 0, 0

    def save_location(self): self.old_position = self.position.copy()

    def move(self, walls, map_w, map_h):
        if self.is_attacking:
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        self.is_moving = False

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.is_moving, self.flip = True, True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.is_moving, self.flip = True, False

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            dy -= self.speed
            self.is_moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
            self.is_moving = True

        # Axe X: bloque uniquement horizontalement si collision
        if dx:
            self.position[0] += dx
            self.update_hitbox()
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    self.position[0] -= dx
                    self.update_hitbox()
                    break

        # Axe Y: bloque uniquement verticalement si collision
        if dy:
            self.position[1] += dy
            self.update_hitbox()
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    self.position[1] -= dy
                    self.update_hitbox()
                    break

        # Garde le joueur dans les limites de la carte
        self.position[0] = max(0, min(self.position[0], map_w))
        self.position[1] = max(0, min(self.position[1], map_h))
        self.update_hitbox()
        self.rect.center = self.position

    def update(self):
        self.rect.center = self.position

        # Animation
        target = self.idle_frames
        if self.is_attacking:
            target = self.at2_frames if self.attack_type == 2 else self.at1_frames
        elif self.is_moving:
            target = self.move_frames

        if self.current_animation is not target:
            self.current_frame = 0
            self.timer = 0
            self.current_animation = target

        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame += 1
            if self.is_attacking and self.current_frame >= len(self.current_animation):
                self.is_attacking = False
                self.current_frame = 0
            else:
                self.current_frame %= len(self.current_animation)

        img = self.current_animation[min(self.current_frame, len(self.current_animation)-1)]
        self.image = pygame.transform.flip(img, self.flip, False)

    def back_to_old_position(self):
        self.position = self.old_position.copy()
        self.update_hitbox()
        self.rect.center = self.position

# ==========================================
# CLASSE PRINCIPALE (Game)
# ==========================================
class Game:
    def __init__(self):
        self.fenetre = pygame.display.set_mode(Resolution)
        pygame.display.set_caption("Niveau Player Top")

        tmx_path = os.path.join(os.path.dirname(__file__), "..", "assets", "maps", "niveau3", "mapfightfinalboss.tmx")
        self.tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        
        map_data  = pyscroll.data.TiledMapData(self.tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.fenetre.get_size())
        
        # default_layer=10 pour être au-dessus de TOUS les calques de la carte
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=10)

        # Extraction des collisions depuis le calque d'objets "collision"
        self.walls = []
        collision_layer = None
        for layer in self.tmx_data.layers:
            if getattr(layer, "name", "").lower() == "collision":
                collision_layer = layer
                break

        if collision_layer is not None:
            for obj in collision_layer:
                if getattr(obj, "width", 0) and getattr(obj, "height", 0):
                    self.walls.append(pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height)))

        print(f"Collisions chargees: {len(self.walls)}")

        self.player = Player()
        self.group.add(self.player)
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: self.player.attack1() # Click Droit
                    if event.button == 1: self.player.attack2() # Click Gauche

            self.player.move(self.walls, self.tmx_data.width * self.tmx_data.tilewidth, self.tmx_data.height * self.tmx_data.tileheight)

            self.group.update()
            self.group.center(self.player.rect.center)
            self.group.draw(self.fenetre)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
