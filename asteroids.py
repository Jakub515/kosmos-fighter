import pygame
import math
import random

# Globalny słownik na podręczną pamięć obróconych obrazków
# Zapobiega to ponownemu przeliczaniu rotacji dla każdej asteroidy z osobna
ROTATION_CACHE = {}

def get_rotated_asteroid(original_image, angle):
    """Pobiera obrócony obrazek z cache lub tworzy nowy, jeśli nie istnieje."""
    angle = int(angle % 360)
    img_id = id(original_image) # Unikalny ID obrazka bazowego
    
    if img_id not in ROTATION_CACHE:
        ROTATION_CACHE[img_id] = [pygame.transform.rotate(original_image, a) for a in range(360)]
    
    return ROTATION_CACHE[img_id][angle]

class Asteroid:
    def __init__(self, asteroid_images, center_pos, spawn_radius):
        self.image_key = random.choice(list(asteroid_images.keys()))
        self.original_image = asteroid_images[self.image_key]
        
        # Wstępne wygenerowanie cache dla tego typu obrazka
        get_rotated_asteroid(self.original_image, 0)
        
        self.radius = self.original_image.get_width() / 2
        self.mass = self.radius * 0.1
        
        angle = random.uniform(0, 2 * math.pi)
        inner_limit = 0.9 
        distance = random.uniform(spawn_radius * inner_limit, spawn_radius)
        
        self.pos = pygame.math.Vector2(
            center_pos.x + math.cos(angle) * distance,
            center_pos.y + math.sin(angle) * distance
        )
        
        self.velocity = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-1.0, 1.0)
        self.gravity_range = self.radius * 8
        self.gravity_range_sq = self.gravity_range ** 2 # Używamy kwadratu do szybszych obliczeń

    def update(self, dt, player):
        self.pos += self.velocity
        self.angle = (self.angle + self.rotation_speed) % 360

        # OPTYMALIZACJA: Używamy kwadratu dystansu, aby uniknąć math.sqrt()
        rel_x = self.pos.x - player.player_pos.x
        rel_y = self.pos.y - player.player_pos.y
        dist_sq = rel_x**2 + rel_y**2

        if dist_sq < self.gravity_range_sq and dist_sq > 100:
            distance = math.sqrt(dist_sq)
            force_magnitude = self.mass / (distance * 0.5) 
            # Wektor przyciągania
            gravity_vector = pygame.math.Vector2(rel_x, rel_y) / distance * force_magnitude * dt * 50
            player.velocity += gravity_vector

    def draw(self, window, cam_x, cam_y, screen_w, screen_h):
        # OPTYMALIZACJA: Rysuj tylko, jeśli asteroida jest widoczna na ekranie (Culling)
        draw_x = self.pos.x - cam_x
        draw_y = self.pos.y - cam_y
        
        margin = 100 # Margines, aby nie znikały nagle na krawędziach
        if -margin < draw_x < screen_w + margin and -margin < draw_y < screen_h + margin:
            rotated = get_rotated_asteroid(self.original_image, self.angle)
            rect = rotated.get_rect(center=(draw_x, draw_y))
            window.blit(rotated, rect.topleft)

class AsteroidManager:
    def __init__(self, ship_frames, zones_list):
        self.asteroid_images = {
            "images/Meteors/meteorBrown_big1.png": ship_frames["images/Meteors/meteorBrown_big1.png"],
            "images/Meteors/meteorBrown_big2.png": ship_frames["images/Meteors/meteorBrown_big2.png"],
            "images/Meteors/meteorBrown_big3.png": ship_frames["images/Meteors/meteorBrown_big3.png"],
            "images/Meteors/meteorBrown_big4.png": ship_frames["images/Meteors/meteorBrown_big4.png"],
            "images/Meteors/meteorGrey_big1.png": ship_frames["images/Meteors/meteorGrey_big1.png"],
            "images/Meteors/meteorGrey_big2.png": ship_frames["images/Meteors/meteorGrey_big2.png"],
            "images/Meteors/meteorGrey_big3.png": ship_frames["images/Meteors/meteorGrey_big3.png"],
            "images/Meteors/meteorGrey_big4.png": ship_frames["images/Meteors/meteorGrey_big4.png"],
            "images/Meteors/spaceMeteors_001.png": ship_frames["images/Meteors/spaceMeteors_001.png"],
            "images/Meteors/spaceMeteors_002.png": ship_frames["images/Meteors/spaceMeteors_002.png"],
            "images/Meteors/spaceMeteors_003.png": ship_frames["images/Meteors/spaceMeteors_003.png"],
            "images/Meteors/spaceMeteors_004.png": ship_frames["images/Meteors/spaceMeteors_004.png"],
            "images/Meteors/meteorBrown_med1.png": ship_frames["images/Meteors/meteorBrown_med1.png"],
            "images/Meteors/meteorBrown_med3.png": ship_frames["images/Meteors/meteorBrown_med3.png"],
            "images/Meteors/meteorBrown_small1.png": ship_frames["images/Meteors/meteorBrown_small1.png"],
            "images/Meteors/meteorBrown_small2.png": ship_frames["images/Meteors/meteorBrown_small2.png"],
            "images/Meteors/meteorBrown_tiny1.png": ship_frames["images/Meteors/meteorBrown_tiny1.png"],
            "images/Meteors/meteorBrown_tiny2.png": ship_frames["images/Meteors/meteorBrown_tiny2.png"],
            "images/Meteors/meteorGrey_med1.png": ship_frames["images/Meteors/meteorGrey_med1.png"],
            "images/Meteors/meteorGrey_med2.png": ship_frames["images/Meteors/meteorGrey_med2.png"],
            "images/Meteors/meteorGrey_small2.png": ship_frames["images/Meteors/meteorGrey_small2.png"],
            "images/Meteors/meteorGrey_tiny1.png": ship_frames["images/Meteors/meteorGrey_tiny1.png"],
            "images/Meteors/meteorGrey_tiny2.png": ship_frames["images/Meteors/meteorGrey_tiny2.png"]
        }
        self.asteroids = []

        for zone in zones_list:
            for _ in range(zone["count"]):
                self.asteroids.append(Asteroid(self.asteroid_images, zone["pos"], zone["radius"]))

    def update(self, dt, player):
        # Przy 1000 sztukach można by rozważyć aktualizację co 2 klatki, 
        # ale cache rotacji powinien wystarczyć.
        for asteroid in self.asteroids:
            asteroid.update(dt, player)

    def draw(self, window, cam_x, cam_y):
        sw, sh = window.get_size()
        for asteroid in self.asteroids:
            asteroid.draw(window, cam_x, cam_y, sw, sh)