import pygame
import pytmx
import pyscroll
import sys
import os
import math
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.constante import (
    Resolution,
    boss_hp_level3,
    boss_damage_level3,
    boss_projectile_speed_lvl3,
    boss_projectile_damage_lvl3,
    boss_projectile_cooldown_lvl3,
    boss_shoot_range_level3,
    smoke_size_level3,
    smoke_max_distance_level3,
    smoke_fade_start_level3,
)
from scenes.game_over import cinematique_mort
from entities.monster import Monster

pygame.init()

THROW_SPRITE_FILE = "golem_attack1.png"


def load_animation(path, cols, rows, scale=1.0, target_size=None):
    if not os.path.exists(path):
        return [pygame.Surface((32, 32), pygame.SRCALPHA)]

    sheet = pygame.image.load(path).convert_alpha()
    frame_w = sheet.get_width() // cols
    frame_h = sheet.get_height() // rows

    frames = []
    for row in range(rows):
        for col in range(cols):
            frame = sheet.subsurface((col * frame_w, row * frame_h, frame_w, frame_h))

            if target_size:
                frame = pygame.transform.scale(frame, target_size)
            elif scale != 1.0:
                new_w = int(frame_w * scale)
                new_h = int(frame_h * scale)
                frame = pygame.transform.scale(frame, (new_w, new_h))

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
        self.at1_frames = load_animation(os.path.join(sprites_dir, "golem_attack1.png"), 5, 4, target_size=target)
        self.at2_frames = load_animation(os.path.join(sprites_dir, "golem_attack2.png"), 6, 6, target_size=target)

        self.throw_frames = load_animation(
            os.path.join(sprites_dir, THROW_SPRITE_FILE),
            5, 4,
            target_size=target
        )[:-1]

        self.current_animation = self.idle_frames
        self.is_moving = False
        self.is_attacking = False
        self.is_throwing = False
        self.attack_type = None
        self.flip = False

        self.current_frame = 0
        self.image = self.current_animation[0]
        self.rect = self.image.get_rect()

        self.position = [800, 800]
        self.rect.center = self.position

        self.hp = 100
        self.hp_max = 100

        self.hitbox = pygame.Rect(0, 0, 50, 30)
        self.update_hitbox()

        self.animation_speed = 0.17
        self.timer = 0

        self.snowball_cooldown = 1800
        self.last_snowball_time = 0
        self.throw_ready = False
        self.throw_has_spawned = False
        self.throw_start_time = 0

        self.attack_start_time = 0

    def update_hitbox(self):
        self.hitbox.center = (self.position[0], self.position[1] + 60)

    def attack1(self):
        if not self.is_attacking and not self.is_throwing:
            self.is_attacking = True
            self.attack_type = 1
            self.current_frame = 0
            self.timer = 0

    def attack2(self):
        if not self.is_attacking and not self.is_throwing:
            self.is_attacking = True
            self.attack_type = 2
            self.current_frame = 0
            self.timer = 0

    def start_throw(self):
        if not self.is_throwing and not self.is_attacking:
            self.is_throwing = True
            self.current_frame = 0
            self.timer = 0
            self.throw_ready = False
            self.throw_has_spawned = False
            self.throw_start_time = pygame.time.get_ticks()

    def save_location(self):
        self.old_position = self.position.copy()

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

        if dx:
            self.position[0] += dx
            self.update_hitbox()
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    self.position[0] -= dx
                    self.update_hitbox()
                    break

        if dy:
            self.position[1] += dy
            self.update_hitbox()
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    self.position[1] -= dy
                    self.update_hitbox()
                    break

        self.position[0] = max(0, min(self.position[0], map_w))
        self.position[1] = max(0, min(self.position[1], map_h))
        self.update_hitbox()
        self.rect.center = self.position

    def update(self):
        self.rect.center = self.position

        target = self.idle_frames
        if self.is_throwing:
            target = self.throw_frames
        elif self.is_attacking:
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

            if self.is_throwing:
                current_time = pygame.time.get_ticks()

                if current_time - self.throw_start_time >= 1000 and not self.throw_has_spawned:
                    self.throw_ready = True
                    self.throw_has_spawned = True

                if self.current_frame >= len(self.throw_frames):
                    self.is_throwing = False
                    self.current_frame = 0
                    self.throw_ready = False
                    self.throw_has_spawned = False

            elif self.is_attacking and self.current_frame >= len(self.current_animation):
                self.is_attacking = False
                self.current_frame = 0

            else:
                self.current_frame %= len(self.current_animation)

        img = self.current_animation[min(self.current_frame, len(self.current_animation) - 1)]
        self.image = pygame.transform.flip(img, self.flip, False)

    def back_to_old_position(self):
        self.position = self.old_position.copy()
        self.update_hitbox()
        self.rect.center = self.position


# ==========================================
# CLASSE BOSS
# ==========================================
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        sprites_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")

        # taille
        self.frames = load_animation(
            os.path.join(sprites_dir, "bossnuages.png"),
            2, 1,
            scale=0.65
        )

        self.current_frame = 0
        self.timer = 0
        self.animation_speed = 0.1

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.position = [float(x), float(y)]

        self.hp = boss_hp_level3
        self.hp_max = boss_hp_level3
        self.hit_by_current_attack = False
        self.is_boss = True

        self.damage = boss_damage_level3
        self.attack_range = 0
        self.attack_cooldown = 0
        self.last_attack_time = 0

        self.stunned_until = 0

        self.shoot_range = boss_shoot_range_level3
        self.projectile_cooldown = boss_projectile_cooldown_lvl3
        self.last_projectile_time = 0

    def update(self, player):
        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(int(self.position[0]), int(self.position[1])))

# ==========================================
# BOULE DE NEIGE
# ==========================================
class Snowball:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_x = float(start_x)
        self.start_y = float(start_y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)

        self.progress = 0.0
        self.speed = 0.035
        self.arc_height = 24
        self.radius = 10
        self.damage = 2
        self.active = True

        self.world_x = self.start_x
        self.world_y = self.start_y

    def update(self):
        if not self.active:
            return

        self.progress += self.speed

        if self.progress >= 1:
            self.progress = 1
            self.active = False

        self.world_x = self.start_x + (self.target_x - self.start_x) * self.progress
        self.world_y = self.start_y + (self.target_y - self.start_y) * self.progress

    def get_draw_position(self, offset_x, offset_y):
        arc_offset = math.sin(self.progress * math.pi) * self.arc_height
        draw_x = self.world_x + offset_x
        draw_y = self.world_y + offset_y - arc_offset
        return draw_x, draw_y

    def draw(self, fenetre, offset_x, offset_y):
        if not self.active:
            return

        draw_x, draw_y = self.get_draw_position(offset_x, offset_y)
        pygame.draw.circle(fenetre, (240, 248, 255), (int(draw_x), int(draw_y)), self.radius)
        pygame.draw.circle(fenetre, (170, 215, 255), (int(draw_x), int(draw_y)), self.radius, 2)

    def collides_with_enemy(self, enemy):
        dx = self.world_x - enemy.position[0]
        dy = self.world_y - enemy.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        hit_radius = 35
        if getattr(enemy, "is_boss", False):
            hit_radius = 95

        return distance <= hit_radius


# ==========================================
# MINI NUAGE / CARRÉ ORANGE DU BOSS
# ==========================================
class SmokeProjectile:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.position = [float(start_x), float(start_y)]

        self.size = smoke_size_level3
        self.damage = boss_projectile_damage_lvl3
        self.speed = boss_projectile_speed_lvl3

        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance == 0:
            self.vx = 0
            self.vy = 0
        else:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed

        self.distance_travelled = 0
        self.max_distance = smoke_max_distance_level3
        self.fade_start_distance = smoke_fade_start_level3

        self.alpha = 255
        self.active = True

    def update(self, map_w, map_h):
        if not self.active:
            return

        self.position[0] += self.vx
        self.position[1] += self.vy

        self.distance_travelled += self.speed

        if self.distance_travelled >= self.fade_start_distance:
            fade_progress = self.distance_travelled - self.fade_start_distance
            fade_range = self.max_distance - self.fade_start_distance

            if fade_range > 0:
                self.alpha = max(0, int(255 * (1 - fade_progress / fade_range)))

        if self.distance_travelled >= self.max_distance or self.alpha <= 0:
            self.active = False
            return

        if self.position[0] < 0 or self.position[0] > map_w or self.position[1] < 0 or self.position[1] > map_h:
            self.active = False
            return

    def draw(self, fenetre, offset_x, offset_y):
        if not self.active:
            return

        x = int(self.position[0] + offset_x)
        y = int(self.position[1] + offset_y)

        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        surface.fill((255, 140, 0, max(0, int(self.alpha))))
        fenetre.blit(surface, (x - self.size // 2, y - self.size // 2))

    def collides_with_player(self, player):
        if not self.active:
            return False

        dx = self.position[0] - player.position[0]
        dy = self.position[1] - player.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance <= 30


# ==========================================
# DESSIN BARRE DE VIE JOUEUR
# ==========================================
def dessiner_barre_de_vie(fenetre, joueur):
    bar_w = 220
    bar_h = 22
    margin = 20

    bar_x = Resolution[0] - bar_w - margin
    bar_y = Resolution[1] - bar_h - margin

    pygame.draw.rect(fenetre, (35, 35, 35), (bar_x, bar_y, bar_w, bar_h))
    ratio = max(0, joueur.hp) / float(joueur.hp_max)
    pygame.draw.rect(fenetre, (40, 180, 60), (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(fenetre, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2)

    pygame.font.init()
    police = pygame.font.SysFont("Consolas", 18, bold=True)
    txt = police.render("HP Joueur", True, (255, 255, 255))
    fenetre.blit(txt, (bar_x, bar_y - 24))


# ==========================================
# CLASSE PRINCIPALE (Game) - Niveau 3
# ==========================================
class Game:
    def __init__(self):
        self.fenetre = pygame.display.set_mode(Resolution)
        pygame.display.set_caption("Niveau 3 - Boss Fight")

        tmx_path = os.path.join(os.path.dirname(__file__), "..", "assets", "maps", "niveau3", "mapfightfinalboss.tmx")
        self.tmx_data = pytmx.util_pygame.load_pygame(tmx_path)

        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.fenetre.get_size())

        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=10)

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

        self.player_attack_duration = 1600
        self.player_attack_has_hit = False
        self.player_attack_protection = True

        self.map_w = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_h = self.tmx_data.height * self.tmx_data.tileheight

        self.monsters = pygame.sprite.Group()
        self.nb_monstres = 20
        self.spawn_monstres_aleatoires()

        boss_x = self.map_w // 2 - 500
        boss_y = 400 - 120
        self.boss = Boss(boss_x, boss_y)
        self.group.add(self.boss)

        self.snowballs = []
        self.smoke_projectiles = []

        pygame.font.init()
        self.police_boss = pygame.font.SysFont("Consolas", 22, bold=True)

    def spawn_monstres_aleatoires(self):
        i = 0
        essais_total = 0

        while i < self.nb_monstres and essais_total < 1200:
            essais_total += 1

            x = random.randint(100, self.map_w - 100)
            y = random.randint(250, self.map_h - 100)

            dx = x - self.player.position[0]
            dy = y - self.player.position[1]
            distance_joueur = (dx ** 2 + dy ** 2) ** 0.5

            if distance_joueur < 220:
                continue

            dx_boss = x - (self.map_w // 2)
            dy_boss = y - 400
            if (dx_boss ** 2 + dy_boss ** 2) ** 0.5 < 220:
                continue

            test_rect = pygame.Rect(0, 0, 40, 40)
            test_rect.center = (x, y)

            collision = False
            for wall in self.walls:
                if test_rect.colliderect(wall):
                    collision = True
                    break

            if collision:
                continue

            monster = Monster(x, y)
            self.monsters.add(monster)
            self.group.add(monster)
            print("Monstre {} place en ({}, {})".format(i + 1, x, y))
            i += 1

    def get_all_enemies(self):
        enemies = list(self.monsters)
        if self.boss is not None:
            enemies.append(self.boss)
        return enemies

    def launch_snowball(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.player.last_snowball_time < self.player.snowball_cooldown:
            return

        offset_x, offset_y = self.group._map_layer.get_center_offset()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        target_x = mouse_x - offset_x
        target_y = mouse_y - offset_y

        start_x = self.player.position[0]
        start_y = self.player.position[1] - 20

        snowball = Snowball(start_x, start_y, target_x, target_y)
        self.snowballs.append(snowball)
        self.player.last_snowball_time = current_time

    def boss_launch_smoke(self):
        if self.boss is None:
            return

        current_time = pygame.time.get_ticks()

        if current_time < self.boss.stunned_until:
            return

        dx = self.player.position[0] - self.boss.position[0]
        dy = self.player.position[1] - self.boss.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > self.boss.shoot_range:
            return

        if current_time - self.boss.last_projectile_time < self.boss.projectile_cooldown:
            return

        start_x = self.boss.position[0]
        start_y = self.boss.position[1] + 20
        target_x = self.player.position[0]
        target_y = self.player.position[1]

        projectile = SmokeProjectile(start_x, start_y, target_x, target_y)
        self.smoke_projectiles.append(projectile)
        self.boss.last_projectile_time = current_time

    def handle_player_melee_attacks(self):
        attack_range = 100
        current_time = pygame.time.get_ticks()

        if not self.player.is_attacking:
            return

        if current_time - self.player.attack_start_time < self.player_attack_duration:
            return

        if self.player_attack_has_hit:
            self.player.is_attacking = False
            return

        for enemy in self.get_all_enemies():
            dx = self.player.position[0] - enemy.position[0]
            dy = self.player.position[1] - enemy.position[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= attack_range:
                enemy.hp -= 1
                self.player_attack_has_hit = True

                if getattr(enemy, "is_boss", False):
                    enemy.stunned_until = current_time + 1000
                    print("Boss touche ! HP restants :", enemy.hp)
                else:
                    enemy.stunned_until = current_time + 1600
                    if hasattr(enemy, "is_hit"):
                        enemy.is_hit = True
                    if hasattr(enemy, "is_attacking"):
                        enemy.is_attacking = False
                    if hasattr(enemy, "attack_has_hit"):
                        enemy.attack_has_hit = False
                    print("Monstre touche ! HP restants :", enemy.hp)

                if enemy.hp <= 0:
                    if getattr(enemy, "is_boss", False):
                        enemy.kill()
                        print("Boss vaincu !")
                        self.boss = None
                    else:
                        if hasattr(enemy, "is_dead"):
                            enemy.is_dead = True
                            enemy.current_frame = 0
                        else:
                            enemy.kill()
                        print("Monstre mort !")

        self.player.is_attacking = False

    def handle_snowballs(self):
        enemies = self.get_all_enemies()

        for snowball in list(self.snowballs):
            snowball.update()

            if not snowball.active:
                if snowball in self.snowballs:
                    self.snowballs.remove(snowball)
                continue

            for enemy in enemies:
                if enemy is None:
                    continue

                if snowball.collides_with_enemy(enemy):
                    enemy.hp -= snowball.damage

                    if getattr(enemy, "is_boss", False):
                        enemy.stunned_until = pygame.time.get_ticks() + 700
                    else:
                        enemy.stunned_until = pygame.time.get_ticks() + 1200
                        if hasattr(enemy, "is_hit"):
                            enemy.is_hit = True
                        if hasattr(enemy, "is_attacking"):
                            enemy.is_attacking = False
                        if hasattr(enemy, "attack_has_hit"):
                            enemy.attack_has_hit = False

                    snowball.active = False

                    if getattr(enemy, "is_boss", False):
                        print("Boss touche par boule de neige ! HP restants :", enemy.hp)
                    else:
                        print("Monstre touche par boule de neige ! HP restants :", enemy.hp)

                    if enemy.hp <= 0:
                        if getattr(enemy, "is_boss", False):
                            enemy.kill()
                            print("Boss vaincu !")
                            self.boss = None
                        else:
                            if hasattr(enemy, "is_dead"):
                                enemy.is_dead = True
                                enemy.current_frame = 0
                            else:
                                enemy.kill()
                            print("Monstre mort !")

                    if snowball in self.snowballs:
                        self.snowballs.remove(snowball)
                    break

    def handle_enemy_attacks(self):
        current_time = pygame.time.get_ticks()

        for monster in self.monsters:
            if getattr(monster, "is_dead", False):
                continue

            dx = self.player.position[0] - monster.position[0]
            dy = self.player.position[1] - monster.position[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if self.player.is_attacking and self.player_attack_protection:
                continue

            if current_time < monster.stunned_until:
                continue

            if monster.is_attacking:
                if (
                    not monster.attack_has_hit
                    and current_time - monster.attack_start_time >= monster.attack_hit_delay
                    and distance <= monster.attack_range
                ):
                    self.player.hp -= monster.damage
                    monster.attack_has_hit = True
                    monster.last_attack_time = current_time
                    print("Le joueur prend des degats ! HP :", self.player.hp)

                if monster.current_frame == len(monster.attack_frames) - 1:
                    if monster.attack_has_hit:
                        monster.is_attacking = False
                        monster.attack_has_hit = False

        self.boss_launch_smoke()

    def handle_smoke_projectiles(self):
        for projectile in list(self.smoke_projectiles):
            projectile.update(self.map_w, self.map_h)

            if not projectile.active:
                if projectile in self.smoke_projectiles:
                    self.smoke_projectiles.remove(projectile)
                continue

            if projectile.collides_with_player(self.player):
                self.player.hp -= projectile.damage
                projectile.active = False
                print("Projectile du boss touche ! HP joueur :", self.player.hp)

                if projectile in self.smoke_projectiles:
                    self.smoke_projectiles.remove(projectile)

    def update_enemies(self):
        for monster in self.monsters:
            monster.update(self.player, self.walls)

        if self.boss is not None:
            self.boss.update(self.player)

    def draw_ui(self):
        dessiner_barre_de_vie(self.fenetre, self.player)

        if self.boss is not None:
            boss_bar_w = 650
            boss_bar_h = 24
            boss_bar_x = (Resolution[0] - boss_bar_w) // 2
            boss_bar_y = 18

            pygame.draw.rect(self.fenetre, (35, 35, 35), (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h))
            hp_ratio = max(0, self.boss.hp) / float(self.boss.hp_max)
            pygame.draw.rect(self.fenetre, (130, 20, 20), (boss_bar_x, boss_bar_y, int(boss_bar_w * hp_ratio), boss_bar_h))
            pygame.draw.rect(self.fenetre, (255, 255, 255), (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h), 2)

            txt_boss = self.police_boss.render("BOSS", True, (255, 230, 230))
            self.fenetre.blit(txt_boss, (boss_bar_x + boss_bar_w // 2 - txt_boss.get_width() // 2, boss_bar_y - 28))

    def move_player_level3(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        self.player.is_moving = False

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            dx -= self.player.speed
            self.player.is_moving = True
            self.player.flip = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.player.speed
            self.player.is_moving = True
            self.player.flip = False

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            dy -= self.player.speed
            self.player.is_moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.player.speed
            self.player.is_moving = True

        if dx:
            self.player.position[0] += dx
            self.player.update_hitbox()
            for wall in self.walls:
                if self.player.hitbox.colliderect(wall):
                    self.player.position[0] -= dx
                    self.player.update_hitbox()
                    break

        if dy:
            self.player.position[1] += dy
            self.player.update_hitbox()
            for wall in self.walls:
                if self.player.hitbox.colliderect(wall):
                    self.player.position[1] -= dy
                    self.player.update_hitbox()
                    break

        self.player.position[0] = max(0, min(self.player.position[0], self.map_w))
        self.player.position[1] = max(0, min(self.player.position[1], self.map_h))
        self.player.update_hitbox()
        self.player.rect.center = self.player.position

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "menu"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

                    if event.key == pygame.K_e:
                        self.player.start_throw()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.player.attack1()
                        self.player.attack_start_time = pygame.time.get_ticks()
                        self.player_attack_has_hit = False

                    if event.button == 1:
                        self.player.attack2()
                        self.player.attack_start_time = pygame.time.get_ticks()
                        self.player_attack_has_hit = False

            self.move_player_level3()

            self.handle_player_melee_attacks()
            self.handle_snowballs()
            self.handle_enemy_attacks()
            self.handle_smoke_projectiles()

            if self.player.hp <= 0:
                return cinematique_mort(self.fenetre)

            self.player.update()

            if self.player.throw_ready:
                self.launch_snowball()
                self.player.throw_ready = False

            if self.boss is None:
                from scenes.cutscene import cinematique_fin_jeu
                cinematique_fin_jeu(self.fenetre)
                return "menu"

            self.update_enemies()

            self.group.center(self.player.rect.center)
            self.group.draw(self.fenetre)

            offset_x, offset_y = self.group._map_layer.get_center_offset()

            for snowball in self.snowballs:
                snowball.draw(self.fenetre, offset_x, offset_y)

            for projectile in self.smoke_projectiles:
                projectile.draw(self.fenetre, offset_x, offset_y)

            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()