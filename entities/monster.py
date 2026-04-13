import pygame
import math
import os

from entities.constante import (
    monster_hp_level3,
    monster_damage_level3,
    monster_speed_level3,
    monster_attack_range_level3,
    monster_attack_cooldown_lvl3,
    monster_detection_range_lvl3,
    monster_stop_range_lvl3,
)


def load_animation(path, cols, rows, target_size=None):
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
            frames.append(frame)

    return frames


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        sprites_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")

        frames = load_animation(
            os.path.join(sprites_dir, "ZombieSheet.png"),
            4, 4,
            target_size=(64, 64)
        )

        # Découpage du sheet
        self.side_frames = frames[0:4]
        self.up_frames = frames[4:8]
        self.down_frames = frames[8:12]
        self.attack_frames = frames[12:16]

        self.current_animation = self.side_frames
        self.current_frame = 0
        self.timer = 0
        self.animation_speed = 0.15

        self.image = self.current_animation[0]
        self.rect = self.image.get_rect(center=(x, y))

        self.position = [float(x), float(y)]
        self.speed = monster_speed_level3

        self.hp = monster_hp_level3

        # Combat
        self.damage = monster_damage_level3
        self.attack_range = monster_attack_range_level3
        self.attack_cooldown = monster_attack_cooldown_lvl3
        self.last_attack_time = 0
        self.stunned_until = 0

        # Retard d'impact de l'attaque
        self.attack_hit_delay = 1000
        self.attack_start_time = 0
        self.attack_has_hit = False

        # IA
        self.detection_range = monster_detection_range_lvl3
        self.stop_range = monster_stop_range_lvl3

        self.hit_by_current_attack = False
        self.is_attacking = False
        self.is_hit = False
        self.is_dead = False
        self.is_boss = False
        self.flip = False

        # Hitbox
        self.hitbox = pygame.Rect(0, 0, 30, 22)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.center = (int(self.position[0]), int(self.position[1]) + 12)

    def start_attack(self):
        if not self.is_attacking and not self.is_dead:
            self.is_attacking = True
            self.attack_start_time = pygame.time.get_ticks()
            self.attack_has_hit = False
            self.current_frame = 0
            self.timer = 0

    def update(self, player, walls=None):
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = math.hypot(dx, dy)

        current_time = pygame.time.get_ticks()

        # Si stun, le monstre arrête son attaque
        if current_time < self.stunned_until:
            self.is_attacking = False
            self.attack_has_hit = False

        # Choix direction
        if abs(dx) > abs(dy):
            move_anim = self.side_frames
            self.flip = dx < 0
        elif dy < 0:
            move_anim = self.up_frames
        else:
            move_anim = self.down_frames

        # Déclenche attaque si proche
        if (
            not self.is_dead
            and current_time >= self.stunned_until
            and distance <= self.attack_range
            and current_time - self.last_attack_time >= self.attack_cooldown
            and not self.is_attacking
        ):
            self.start_attack()

        # Déplacement seulement si pas en attaque
        if (
            not self.is_dead
            and not self.is_attacking
            and current_time >= self.stunned_until
            and self.stop_range < distance <= self.detection_range
            and distance != 0
        ):
            dx /= distance
            dy /= distance

            move_x = dx * self.speed
            move_y = dy * self.speed

            if walls is None:
                self.position[0] += move_x
                self.position[1] += move_y
            else:
                # Collision axe X
                self.position[0] += move_x
                self.update_hitbox()
                for wall in walls:
                    if self.hitbox.colliderect(wall):
                        self.position[0] -= move_x
                        self.update_hitbox()
                        break

                # Collision axe Y
                self.position[1] += move_y
                self.update_hitbox()
                for wall in walls:
                    if self.hitbox.colliderect(wall):
                        self.position[1] -= move_y
                        self.update_hitbox()
                        break

        # Animation choisie
        if self.is_dead:
            self.current_animation = [self.attack_frames[-1]]
        elif self.is_attacking:
            self.current_animation = self.attack_frames
        else:
            self.current_animation = move_anim

        # Animation frame
        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.current_frame += 1

            if self.is_attacking:
                if self.current_frame >= len(self.attack_frames):
                    self.current_frame = 0
            else:
                self.current_frame %= len(self.current_animation)

        img = self.current_animation[min(self.current_frame, len(self.current_animation) - 1)]
        self.image = pygame.transform.flip(img, self.flip, False)
        self.rect = self.image.get_rect(center=(int(self.position[0]), int(self.position[1])))
        self.update_hitbox()