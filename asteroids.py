import pygame
import math
import random

class Asteroid:
    def __init__(self, asteroid_images, world_center, world_radius):
        # Wybór grafiki i nazwy klucza (do określenia rozmiaru)
        self.image_key = random.choice(list(asteroid_images.keys()))
        self.original_image = asteroid_images[self.image_key]
        self.image = self.original_image
        
        # --- ROZMIAR I MASA ---
        # Określamy masę na podstawie szerokości obrazka
        self.radius = self.original_image.get_width() / 2
        self.mass = self.radius * 1.5  # Im większy, tym silniejsza grawitacja
        
        # --- POZYCJA I RUCH ---
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, world_radius)
        self.pos = pygame.math.Vector2(
            world_center.x + math.cos(angle) * distance,
            world_center.y + math.sin(angle) * distance
        )
        
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        
        # --- ROTACJA ---
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-1.0, 1.0)
        
        # --- ZASIĘG GRAWITACJI ---
        self.gravity_range = self.radius * 8  # Pole grawitacyjne to 8x promień meteorytu

    def update(self, dt, player):
        # 1. Ruch własny meteorytu
        self.pos += self.velocity
        self.angle += self.rotation_speed

        # 2. Mechanika grawitacji (przyciąganie gracza)
        diff = self.pos - player.player_pos
        distance = diff.length()

        if distance < self.gravity_range and distance > 10:
            # Wzór na siłę: (G * m1) / r^2
            # Uproszczony model dla gry:
            force_magnitude = self.mass / (distance * 0.5) 
            gravity_vector = diff.normalize() * force_magnitude * dt * 50
            
            # Aplikujemy siłę bezpośrednio do prędkości gracza
            player.velocity += gravity_vector

    def draw(self, window, cam_x, cam_y):
        rotated = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated.get_rect(center=(self.pos.x - cam_x, self.pos.y - cam_y))
        window.blit(rotated, rect.topleft)

class AsteroidManager:
    def __init__(self, ship_frames, world_center, world_radius, count=40):
        # Filtrowanie meteorytów
        self.asteroid_images = {k: v for k, v in ship_frames.items() if "meteor" in k.lower()}
        if not self.asteroid_images:
            self.asteroid_images = ship_frames

        self.asteroids = [Asteroid(self.asteroid_images, world_center, world_radius) for _ in range(count)]

    def update(self, dt, player):
        for asteroid in self.asteroids:
            asteroid.update(dt, player)

    def draw(self, window, cam_x, cam_y):
        for asteroid in self.asteroids:
            asteroid.draw(window, cam_x, cam_y)