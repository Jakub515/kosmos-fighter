import pygame
import load_images
import space_ship
from sky import SpaceBackground
import enemy_ship
import time
import os
from collections import defaultdict
from functions import Event
from enemy_ship import EnemyManager

# --- INICJALIZACJA ---
pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
FPS = 60
window = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Kosmos")

image_load = load_images.ImageLoad()

# --- ŁADOWANIE ZASOBÓW ---
base_folder = os.path.join(os.getcwd(), "images")
files_by_ext = defaultdict(list)
if os.path.exists(base_folder):
    for root, _, files in os.walk(base_folder):
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            rel_path = os.path.relpath(os.path.join(root, file), os.getcwd()).replace("\\", "/")
            files_by_ext[ext].append(rel_path)

space_frames = sorted(files_by_ext.get(".png", []))
audio_files = sorted(files_by_ext.get(".wav", []))

loaded_space_frames = {path: image_load.get_image(path, 40) for path in space_frames}
space_parts = []

# --- KONFIGURACJA ŚWIATA (LOGICZNA GRANICA) ---
# WORLD_RADIUS to punkt "odbicia"
WORLD_RADIUS = 10_000    
# FADE_ZONE to dystans PRZED krawędzią, gdzie pojawia się światło (1500px)
FADE_ZONE = 5000
WORLD_CENTER = pygame.Vector2(5000, 5000) 
TILE_WIDTH, TILE_HEIGHT = 1920, 1080

# --- OBIEKTY GRY ---
bg = SpaceBackground(tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT, screen_width=1920, screen_height=1080, num_stars=50)
player_pos = [WORLD_CENTER.x, WORLD_CENTER.y] 

player = space_ship.SpaceShip(loaded_space_frames, space_parts, audio_files, 1920, 1080, player_pos)
enemy_manager = EnemyManager(loaded_space_frames, player, max_enemies=10)
event = Event()

# --- AUDIO ---
if os.path.exists("images/audio/star_wars.mp3"):
    pygame.mixer.music.load("images/audio/star_wars.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# --- PĘTLA GŁÓWNA ---
running = True
while running:
    dt = clock.tick(FPS) / 1000
    event.update()

    if event.system_exit or event.key_escape:
        running = False

    # 1. UPDATE POZYCJI
    player_pos_raw = player.update(event.key_up, event.key_down, event.key_right, event.key_left, event.key_space, 
                                  [event.key_1, event.key_2, event.key_3, event.key_4, event.key_5], dt, event.backquote)
    
    current_pos = pygame.Vector2(player.player_pos.x, player.player_pos.y)
    distance = current_pos.distance_to(WORLD_CENTER)

    # 2. LOGIKA ODBICIA OD KOŁA (Fizyczna bariera)
    if distance > WORLD_RADIUS:
        normal = (current_pos - WORLD_CENTER).normalize()
        clamped_pos = WORLD_CENTER + normal * WORLD_RADIUS
        player.player_pos.x, player.player_pos.y = clamped_pos.x, clamped_pos.y
        
        if hasattr(player, 'velocity') and player.velocity.length() > 0:
            dot = player.velocity.dot(normal)
            if dot > 0:
                player.velocity -= 2 * dot * normal * 0.7 # Odbicie

    enemy_manager.update(dt)

    # 3. RYSOWANIE
    
    # Tło (Warstwa 0)
    bg.draw(window, [player.player_pos.x, player.player_pos.y])
    
    camera_x = player.player_pos.x - (TILE_WIDTH // 2)
    camera_y = player.player_pos.y - (TILE_HEIGHT // 2)

    # Granica energetyczna (Warstwa 1 - pod graczem, nad tłem)
    # Sprawdzamy, czy gracz jest w strefie 1500px od krawędzi
    start_warning_dist = WORLD_RADIUS - FADE_ZONE
    
    if distance > start_warning_dist:
        # Obliczamy intensywność (0.0 na początku strefy, 1.0 na krawędzi świata)
        intensity = (distance - start_warning_dist) / FADE_ZONE
        intensity = max(0, min(1.0, intensity))
        alpha = int(intensity * 255)
        
        rel_x = int(WORLD_CENTER.x - camera_x)
        rel_y = int(WORLD_CENTER.y - camera_y)
        
        # Powierzchnia dla efektów przeźroczystości
        temp_surface = pygame.Surface((1920, 1080), pygame.SRCALPHA)
        
        # Rysujemy 3 warstwy okręgu dla efektu "Glow":
        # A. Szeroka, słaba poświata (zewnętrzna)
        pygame.draw.circle(temp_surface, (255, 0, 0, alpha // 4), (rel_x, rel_y), WORLD_RADIUS, 1980)
        # B. Główna bariera (środkowa)
        pygame.draw.circle(temp_surface, (255, 0, 0, alpha // 2), (rel_x, rel_y), WORLD_RADIUS, 80)
        # C. Ostra krawędź (wewnętrzna)
        pygame.draw.circle(temp_surface, (255, 50, 50, alpha), (rel_x, rel_y), WORLD_RADIUS, 10)
        
        window.blit(temp_surface, (0, 0))

    # Statki i przeciwnicy (Warstwa 2)
    player.draw(window)
    enemy_manager.draw(window, camera_x, camera_y)

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()