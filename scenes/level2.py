import pygame
import pytmx
import pyscroll
import sys
import os
import random

# Configuration du chemin pour l'import des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import Resolution
from entities import statue as statue_mod

# Initialisation de Pygame
pygame.init()

# ── Chemin du tileset des statues ───────────────────────
TILESET_CHEMIN = 'assets/maps/Graveyard_Set.png'

# ── Nombre de statues à placer aléatoirement ────────────
NB_STATUES = 3


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
        self.position = [1615, 3155]
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
# CLASSE PRINCIPALE (Game) - Niveau 2
# ==========================================
class Game:
    def __init__(self):
        self.fenetre = pygame.display.set_mode(Resolution)
        pygame.display.set_caption("Niveau 2 - Château")

        tmx_path = os.path.join(os.path.dirname(__file__), "..", "assets", "maps", "niveau2", "mapchateau.tmx")
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

        print("Collisions chargees: {}".format(len(self.walls)))

        self.player = Player()
        self.group.add(self.player)
        self.clock = pygame.time.Clock()

        # ── Chargement du tileset et création des statues ──
        self.tileset_statues = statue_mod.charger_tileset(TILESET_CHEMIN)

        # Dimensions de la carte en pixels
        self.map_w = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_h = self.tmx_data.height * self.tmx_data.tileheight

        # Création de 3 statues : (position_depart, cible ou None)
        # La statue 1 doit être poussée vers la cible (2640, 1650)
        statues_config = [
            {"pos": (2700, 1765), "cible": (2685, 1769)},
            {"pos": (2550, 670), "cible": None},
            {"pos": (670, 1393), "cible": (925, 1306)},
        ]
        self.statues = []
        i = 0
        while i < len(statues_config):
            cfg = statues_config[i]
            s = statue_mod.creer_statue(
                self.tileset_statues,
                cfg["pos"][0], cfg["pos"][1],
                echelle=2.0,
                cible=cfg["cible"]
            )
            self.statues.append(s)
            print("Statue {} placee en ({}, {})".format(i + 1, cfg["pos"][0], cfg["pos"][1]))
            i += 1

        # La statue 2 (index 1) est déjà déployée au départ
        self.statues[1]["active"] = True
        self.statues[1]["image"] = self.statues[1]["image_deployee"]
        statue_mod.update_statue(self.statues[1])

        # Police pour afficher les indications
        pygame.font.init()
        self.police = pygame.font.SysFont("Consolas", 16, bold=True)

        # Portail
        portail_path = os.path.join(os.path.dirname(__file__), "..", "assets", "maps", "portail.png")
        if os.path.exists(portail_path):
            self.image_portail = pygame.image.load(portail_path).convert_alpha()
            self.image_portail = pygame.transform.scale(self.image_portail, (120, 120))
            self.rect_portail = self.image_portail.get_rect(center=(1864, 1135))
        else:
            self.image_portail = None

    def run(self):
        running = True
        while running:
            # ── EVENEMENTS ──────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: self.player.attack1() # Click Droit
                    if event.button == 1: self.player.attack2() # Click Gauche


            # ── DEPLACEMENT JOUEUR ──────────────────────
            self.player.move(self.walls, self.map_w, self.map_h)

            # ── AFFICHAGE POSITION JOUEUR DANS LA CONSOLE ──
            print("Joueur : x={}, y={}          ".format(int(self.player.position[0]), int(self.player.position[1])), end="\r")

            # ── POUSSEE DES STATUES (collision joueur) ─────
            p = 0
            while p < len(self.statues):
                poussee, corr_x, corr_y = statue_mod.pousser_statue(self.statues[p], self.player.hitbox)
                if poussee:
                    # Repousser le joueur pour qu'il ne traverse pas la statue
                    self.player.position[0] = self.player.position[0] + corr_x
                    self.player.position[1] = self.player.position[1] + corr_y
                    self.player.update_hitbox()
                    self.player.rect.center = self.player.position
                p += 1

            # ── UPDATE STATUES ──────────────────────────
            k = 0
            while k < len(self.statues):
                statue_mod.update_statue(self.statues[k])
                k += 1

            # ── RENDU ───────────────────────────────────
            self.group.update()
            self.group.center(self.player.rect.center)
            self.group.draw(self.fenetre)

            # Récupération du décalage caméra réel depuis pyscroll
            offset_x, offset_y = self.group._map_layer.get_center_offset()

            # Dessin des statues par-dessus la carte (coordonnées monde -> écran)
            n = 0
            while n < len(self.statues):
                ecran_x = self.statues[n]["rect"].x + offset_x
                ecran_y = self.statues[n]["rect"].y + offset_y
                self.fenetre.blit(self.statues[n]["image"], (ecran_x, ecran_y))

                # Afficher indication si le joueur est proche (statue non déployée)
                if not self.statues[n]["active"] and statue_mod.est_proche(self.player.hitbox, self.statues[n]["hitbox"], 150):
                    txt_e = self.police.render("Poussez la statue", True, (220, 220, 255))
                    txt_x = self.statues[n]["rect"].centerx + offset_x - txt_e.get_width() // 2
                    txt_y = self.statues[n]["rect"].top + offset_y - 25
                    self.fenetre.blit(txt_e, (txt_x, txt_y))
                n += 1

            # Affichage du portail et condition de victoire
            toutes_deployees = True
            for s in self.statues:
                if not s["active"]:
                    toutes_deployees = False
                    break
            
            if toutes_deployees and getattr(self, "image_portail", None) is not None:
                ecran_portail_x = self.rect_portail.x + offset_x
                ecran_portail_y = self.rect_portail.y + offset_y
                self.fenetre.blit(self.image_portail, (ecran_portail_x, ecran_portail_y))
                
                # Zone de collision (téléportation automatique)
                import math
                dist_joueur_portail = math.hypot(self.player.hitbox.centerx - self.rect_portail.centerx, 
                                                 self.player.hitbox.centery - self.rect_portail.centery)
                if dist_joueur_portail < 80:
                    from entities.player_top import Game as PlayerTopGame
                    next_game = PlayerTopGame()
                    next_game.run()
                    return

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
