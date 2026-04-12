import pygame
import math

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Monstre temporaire pour test (représenté par un carré rouge)

        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))

        # Position du monstre dans le monde
        self.rect = self.image.get_rect(center=(x, y))
        self.position = [float(x), float(y)]
        self.speed = 1

        # hp du monstre
        self.hp = 2

        # Attaques des monstres
        self.damage = 15
        self.attack_range = 60
        self.attack_cooldown = 800
        self.last_attack_time = 0

        # Range des monstres
        self.detection_range = 300
        self.stop_range = 50

        # Permet d'éviter plusieurs dégâts sur une seule attaque
        self.hit_by_current_attack = False

    def update(self, player):
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Le monstre suit seulement si le joueur est détecté,
        # mais s'arrête s'il est trop proche
        if self.stop_range < distance <= self.detection_range:
            dx /= distance
            dy /= distance

            self.position[0] += dx * self.speed
            self.position[1] += dy * self.speed

            self.rect.center = (int(self.position[0]), int(self.position[1]))