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
    """
    Pobiera obrócony obrazek z pamięci podręcznej.
    Używamy precyzji 0.2 stopnia (precision=5), aby obrót był idealnie płynny przy 60 FPS.
    """
    precision = 5 
    angle = round(angle * precision) / precision % 360
    
    img_id = id(original_image)
    if img_id not in ROTATION_CACHE:
        ROTATION_CACHE[img_id] = {}
    
    if angle not in ROTATION_CACHE[img_id]:
        # transform.rotate jest kosztowne, dlatego robimy to tylko raz dla danego kąta
        ROTATION_CACHE[img_id][angle] = pygame.transform.rotate(original_image, angle)
    
    return ROTATION_CACHE[img_id][angle]

class Asteroid:
    def __init__(self, planet_images: list, meteor_images: list, center_pos: pygame.math.Vector2, spawn_radius: int, fixed_angle: float):
        # 1. Wybór grafiki (10% szans na planetę)
        if planet_images and random.random() < 0.1:
            self.original_image = random.choice(planet_images)
        else:
            self.original_image = random.choice(meteor_images)
        
        self.radius = self.original_image.get_width() / 2
        self.mass = self.radius * 0.1
        
        # 2. Logika naturalnej obramówki koła
        # jitter_angle sprawia, że odstępy nie są "zegarmistrzowskie"
        jitter_angle = random.uniform(-0.12, 0.12) 
        angle = fixed_angle + jitter_angle
        
        # Sigma 0.03 promienia daje ładny, zwarty pas, który widać że jest kołem
        distance = random.gauss(mu=spawn_radius, sigma=spawn_radius * 0.03)
        
        self.pos = pygame.math.Vector2(
            center_pos.x + math.cos(angle) * distance,
            center_pos.y + math.sin(angle) * distance
        )
        
        # 3. Fizyka i ruch
        # Mała prędkość dryfu, żeby pierścień był stabilny
        self.velocity = pygame.math.Vector2(random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15))
        self.angle = random.uniform(0, 360)
        
        # Prędkość obrotu – dobrana tak, by nawet wolne obiekty nie klatkowały
        self.rotation_speed = random.uniform(0.3, 0.8) * random.choice([-1, 1])
        
        self.gravity_range = self.radius * 8
        self.gravity_range_sq = self.gravity_range ** 2
        self.is_visible = False

    def _apply_gravity(self, target, dt: float):
        """Przyciąganie gracza i przeciwników."""
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
        # Ruch własny
        self.pos += self.velocity
        self.angle = (self.angle + self.rotation_speed) % 360

        # Grawitacja (tylko dla widocznych obiektów)
        if self.is_visible:
            self._apply_gravity(player, dt)
            for enemy in enemies:
                if not enemy.is_dead:
                    self._apply_gravity(enemy, dt)

    def draw(self, window: pygame.Surface, cam_x: float, cam_y: float, screen_w: float, screen_h: float):
        draw_x = self.pos.x - cam_x
        draw_y = self.pos.y - cam_y
        
        # Optymalizacja renderowania: rysuj tylko jeśli na ekranie (+ margines)
        margin = 150
        self.is_visible = -margin < draw_x < screen_w + margin and -margin < draw_y < screen_h + margin
        
        if self.is_visible:
            rotated = get_rotated_asteroid(self.original_image, self.angle)
            rect = rotated.get_rect(center=(draw_x, draw_y))
            window.blit(rotated, rect.topleft)

class AsteroidManager:
    def __init__(self, ship_frames: dict, zones_list: list):
        self.planet_images = []
        self.meteor_images = []
        
        # Filtrowanie i skalowanie grafik
        for path, image in ship_frames.items():
            if path.startswith("images/Meteors/"):
                if "planet" in path.lower():
                    rect = image.get_rect()
                    # Skalowanie planet na 25% oryginału
                    new_size = (int(rect.width * 0.25), int(rect.height * 0.25))
                    final_image = pygame.transform.smoothscale(image, new_size)
                    self.planet_images.append(final_image)
                else:
                    self.meteor_images.append(image)

        self.asteroids = []
        for zone in zones_list:
            count = zone["count"]
            # Równomierne rozłożenie kątowe
            angle_step = (2 * math.pi) / count
            
            for i in range(count):
                target_angle = i * angle_step
                self.asteroids.append(Asteroid(
                    self.planet_images, 
                    self.meteor_images, 
                    zone["pos"], 
                    zone["radius"], 
                    target_angle
                ))
        
        # Wstępne ułożenie kolizyjne
        for _ in range(15):
            self.resolve_overlaps(only_visible=False)

    def resolve_overlaps(self, only_visible=True):
        """Zapobiega nakładaniu się asteroid na siebie."""
        active_asteroids = [a for a in self.asteroids if a.is_visible] if only_visible else self.asteroids
        
        for i in range(len(active_asteroids)):
            for j in range(i + 1, len(active_asteroids)):
                ast1 = active_asteroids[i]
                ast2 = active_asteroids[j]
                
                diff = ast1.pos - ast2.pos
                dist_sq = diff.length_squared()
                min_dist = (ast1.radius + ast2.radius) * 1.15
                
                if 0 < dist_sq < min_dist**2:
                    dist = math.sqrt(dist_sq)
                    overlap = min_dist - dist
                    push = (diff / dist) * (overlap * 0.12)
                    ast1.pos += push
                    ast2.pos -= push

    def update(self, dt: float, player: "SpaceShip", enemy_manager: "EnemyManager"):
        # Aktualizacja kolizji co klatkę (płynne pływanie)
        self.resolve_overlaps(only_visible=True)
        
        enemies = enemy_manager.enemies
        for asteroid in self.asteroids:
            asteroid.update(dt, player, enemies)

    def draw(self, window: pygame.Surface, cam_x: float, cam_y: float):
        sw, sh = window.get_size()
        for asteroid in self.asteroids:
            asteroid.draw(window, cam_x, cam_y, sw, sh)