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

        tmx_path = os.path.join(os.path.dirname(__file__), "..", "assets", "mapchateau.tmx")
        tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        
        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.fenetre.get_size())

        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2)
        self.player = Player()
        self.group.add(self.player)

        # Ajouter le monstre Troll (position 400, 400)
        self.monster = Monster(400, 400)
        self.group.add(self.monster)

        self.clock = pygame.time.Clock()

    def draw_health_bar(self, surface, x, y, hp, max_hp, color, width=200, height=15):
        ratio = max(0, hp / max_hp)
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
        if hp > 0:
            pygame.draw.rect(surface, color, (x, y, width * ratio, height))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 1)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Clic Gauche
                        self.player.attack(attack_type=1)
                    elif event.button == 3: # Clic Droit
                        self.player.attack(attack_type=2)

            self.group.update(self.map_width, self.map_height)
            self.group.center(self.player.rect.center)
            self.group.draw(self.fenetre)

            # --- INTERFACE ET DÉGÂTS ---
            # Barre de vie du Joueur (Fixe)
            self.draw_health_bar(self.fenetre, 20, 20, self.player.health, self.player.max_health, (200, 20, 20))
            
            # Barre de vie du Monstre (Flottante)
            camera_offset = self.map_layer.view_rect
            m_pos = (self.monster.rect.x - camera_offset.x, self.monster.rect.y - camera_offset.y)
            self.draw_health_bar(self.fenetre, m_pos[0], m_pos[1] - 20, self.monster.health, self.monster.max_health, (255, 140, 0), width=64)

            # Logique de collision : Si attaque clic droit touche le monstre
            if self.player.is_attacking and self.player.current_attack_type == 2:
                if self.player.rect.colliderect(self.monster.rect):
                    self.monster.take_damage(0.5) # Dégâts continus pendant l'animation

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._layer = 2
        self.target_w = 128
        self.target_h = 128
        self.max_health = 100
        self.health = 100
        
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        path_troll = os.path.join(assets_dir, "troll_idle.png")
        
        # Le troll_idle est en 3x3 (9 frames)
        self.idle_frames = self.load_animation(path_troll, cols=3, rows=3, count=9)
        
        self.current_frame = 0
        self.image = self.idle_frames[0]
        self.rect = pygame.Rect(x, y, 64, 64)
        
        self.animation_speed = 0.1
        self.timer = 0

    def load_animation(self, path, cols, rows, count):
        if not os.path.exists(path):
            surf = pygame.Surface((self.target_w, self.target_h))
            surf.fill((0, 0, 255))
            return [surf]
            
        sheet = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()
        cell_w, cell_h = sheet_w // cols, sheet_h // rows
        
        frames = []
        for i in range(count):
            col, row = i % cols, i // cols
            frame = sheet.subsurface((col * cell_w, row * cell_h, cell_w, cell_h))
            frame = pygame.transform.scale(frame, (self.target_w, self.target_h))
            frames.append(frame)
        return frames

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def update(self, map_w, map_h):
        if self.health <= 0:
            self.kill() # Supprime le monstre s'il est mort
            return

        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.current_frame]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 3
        self._layer = 2  # Correction : Pyscroll utilise _layer avec un underscore
        self.max_health = 100
        self.health = 100

        # --- CONFIGURATION DES ANIMATIONS ---
        # Taille finale souhaitée pour le personnage en jeu
        self.target_w = 320  # Change this value to make sprite bigger (e.g., 192, 256, 320)
        self.target_h = 320  # Change this value to make sprite bigger

        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

        # Chemins vers les fichiers
        # Assurez-vous que golem_idle.png existe aussi en 4x4
        path_idle = os.path.join(assets_dir, "golem_idle.png") # Test avec move si idle manque
        path_move = os.path.join(assets_dir, "golem_move.png")
        path_attack = os.path.join(assets_dir, "golem_attack1.png")
        path_attack2 = os.path.join(assets_dir, "golem_attack2.png")

        # On passe le nombre de colonnes et de lignes au lieu des pixels fixes
        # Idle et Move sont en 4 colonnes, 4 lignes
        self.idle_frames = self.load_animation(path_idle, cols=4, rows=4, count=16)
        self.move_frames = self.load_animation(path_move, cols=4, rows=4, count=16)

        # L'attaque est en 5 colonnes, 4 lignes (19 frames)
        self.attack_frames = self.load_animation(path_attack, cols=5, rows=4, count=19)

        # L'attaque 2 est en 8 colonnes, 6 lignes (44 frames)
        self.attack2_frames = self.load_animation(path_attack2, cols=8, rows=6, count=44)

        # États
        self.current_animation = self.idle_frames
        self.is_moving = False
        self.is_attacking = False
        self.current_attack_type = 1
        self.flip = False

        self.current_frame = 0
        self.image = self.current_animation[0]
        self.rect = pygame.Rect(100, 100, 64, 64) # Rectangle de collision plus petit que l'image

        print(f"Player initialized - rect: {self.rect}, image size: {self.image.get_size()}")

        self.animation_speed = 0.14
        self.timer = 0

    def load_animation(self, path, cols, rows, count):
        if not os.path.exists(path):
            print(f"ERREUR : Fichier introuvable {path}")
            surf = pygame.Surface((self.target_w, self.target_h))
            surf.fill((255, 0, 0))
            return [surf]

        sheet = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()

        # On calcule la taille d'une cellule en divisant la taille totale par le nombre de colonnes/lignes
        cell_w = sheet_w // cols
        cell_h = sheet_h // rows

        frames = []
        for i in range(count):
            col = i % cols
            row = i // cols

            # On découpe la cellule entière
            frame = sheet.subsurface((col * cell_w, row * cell_h, cell_w, cell_h))
            # On redimensionne à la taille souhaitée en jeu (ex: 128x128)
            frame = pygame.transform.scale(frame, (self.target_w, self.target_h))
            frames.append(frame)
        return frames

    def attack(self, attack_type=1):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_attack_type = attack_type
            self.current_frame = 0
            self.timer = 0
            if attack_type == 1:
                self.current_animation = self.attack_frames
            else:
                self.current_animation = self.attack2_frames

    def move(self, map_w, map_h):
        if self.is_attacking: return

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
            target_animation_set = self.attack2_frames if self.current_attack_type == 2 else self.attack_frames
        elif self.is_moving:
            target_animation_set = self.move_frames

        if self.current_animation != target_animation_set:
            if not (old_animation_set == self.move_frames and target_animation_set == self.idle_frames):
                if not self.is_attacking: self.current_frame = 0
            self.current_animation = target_animation_set

        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame += 1

            if self.is_attacking:
                if self.current_frame >= len(self.current_animation):
                    self.is_attacking = False
                    self.current_frame = 0
                    self.current_animation = self.idle_frames if not self.is_moving else self.move_frames
            
            self.current_frame %= len(self.current_animation)

        image_to_display = self.current_animation[min(self.current_frame, len(self.current_animation)-1)]
        self.image = pygame.transform.flip(image_to_display, self.flip, False)

if __name__ == "__main__":
    game = Game()
    game.run()
