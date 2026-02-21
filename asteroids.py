import pygame
import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space_ship import SpaceShip
    from enemy_ship import EnemyManager

# Globalny słownik na podręczną pamięć obróconych obrazków
ROTATION_CACHE = {}

def get_rotated_asteroid(original_image: pygame.Surface, angle: float):
    """Pobiera obrócony obrazek z cache lub tworzy nowy."""
    angle = int(angle % 360)
    img_id = id(original_image)
    
    if img_id not in ROTATION_CACHE:
        ROTATION_CACHE[img_id] = [pygame.transform.rotate(original_image, a) for a in range(360)]
    
    return ROTATION_CACHE[img_id][angle]

class Asteroid:
    def __init__(self, asteroid_images: dict, center_pos: pygame.math.Vector2, spawn_radius: int):
        self.image_key = random.choice(list(asteroid_images.keys()))
        self.original_image = asteroid_images[self.image_key]
        
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
        self.gravity_range_sq = self.gravity_range ** 2

    def _apply_gravity(self, target, dt: float):
        """Pomocnicza metoda obliczająca przyciąganie dla gracza lub wrogów."""
        target_pos = target.player_pos if hasattr(target, 'player_pos') else target.pos
        
        rel_x = self.pos.x - target_pos.x
        rel_y = self.pos.y - target_pos.y
        dist_sq = rel_x**2 + rel_y**2

        if 100 < dist_sq < self.gravity_range_sq:
            distance = math.sqrt(dist_sq)
            force_magnitude = self.mass / (distance * 0.5) 
            gravity_vector = pygame.math.Vector2(rel_x, rel_y) / distance * force_magnitude * dt * 50
            target.velocity += gravity_vector

    def update(self, dt: float, player: "SpaceShip", enemies: list):
        self.pos += self.velocity
        self.angle = (self.angle + self.rotation_speed) % 360

        # Grawitacja na gracza
        self._apply_gravity(player, dt)

        # Grawitacja na wrogów
        for enemy in enemies:
            if not enemy.is_dead:
                self._apply_gravity(enemy, dt)

    def draw(self, window: pygame.Surface, cam_x: float, cam_y: float, screen_w: float, screen_h: float):
        draw_x = self.pos.x - cam_x
        draw_y = self.pos.y - cam_y
        
        margin = 100
        if -margin < draw_x < screen_w + margin and -margin < draw_y < screen_h + margin:
            rotated = get_rotated_asteroid(self.original_image, self.angle)
            rect = rotated.get_rect(center=(draw_x, draw_y))
            window.blit(rotated, rect.topleft)

class AsteroidManager:
    def __init__(self, ship_frames: dict, zones_list: list):
        self.asteroid_images = {k: v for k, v in ship_frames.items() if "Meteors" in k}
        self.asteroids = []

        # Timer do optymalizacji odpychania (pole magnetyczne)
        self.push_timer = 0.0
        self.push_interval = 1.0  # Odpychanie co 1 sekundę

        for zone in zones_list:
            for _ in range(zone["count"]):
                self.asteroids.append(Asteroid(self.asteroid_images, zone["pos"], zone["radius"]))
        
        # Wstępne rozsunięcie przy starcie, żeby nie zaczynały na sobie
        for _ in range(3):
            self.resolve_overlaps()

    def resolve_overlaps(self):
        """Efekt pola magnetycznego: asteroidy odpychają się od siebie."""
        for i in range(len(self.asteroids)):
            for j in range(i + 1, len(self.asteroids)):
                ast1 = self.asteroids[i]
                ast2 = self.asteroids[j]
                
                diff = ast1.pos - ast2.pos
                dist_sq = diff.length_squared()
                
                # Odpychanie jeśli są bliżej niż suma promieni * margines
                min_dist = (ast1.radius + ast2.radius) * 1.3
                if 0 < dist_sq < min_dist**2:
                    dist = math.sqrt(dist_sq)
                    overlap = min_dist - dist
                    # Wektor odpychania (połowa przesunięcia dla każdej)
                    push = (diff / dist) * (overlap * 0.5)
                    ast1.pos += push
                    ast2.pos -= push

    def update(self, dt: float, player: "SpaceShip", enemy_manager: "EnemyManager"):
        # Logika timera dla pola magnetycznego
        self.push_timer += dt
        if self.push_timer >= self.push_interval:
            self.resolve_overlaps()
            self.push_timer = 0.0

        # Standardowa aktualizacja fizyki i grawitacji
        enemies = enemy_manager.enemies
        for asteroid in self.asteroids:
            asteroid.update(dt, player, enemies)

    def draw(self, window: pygame.Surface, cam_x: float, cam_y: float):
        sw, sh = window.get_size()
        for asteroid in self.asteroids:
            asteroid.draw(window, cam_x, cam_y, sw, sh)