import pygame
import load_images
import space_ship
from sky import SpaceBackground
import enemy_ship
import os
import collisions
from collections import defaultdict
from functions import Event
from enemy_ship import EnemyManager
import music

# --- INICJALIZACJA ---
pygame.init()

clock = pygame.time.Clock()
FPS = 60
window = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Kosmos")

cxx, cyy = window.get_size()
image_load = load_images.ImageLoad()

# --- KONFIGURACJA ŚWIATA ---
WORLD_CENTER = pygame.math.Vector2(0, 0)
WORLD_RADIUS = 10000    # Fizyczna granica
FADE_ZONE = 2000       # Kiedy zaczyna świecić na czerwono

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

music_obj = music.MusicManager(audio_files)

# --- OBIEKTY GRY ---
bg = SpaceBackground(tile_width=cxx, tile_height=cyy, screen_width=cxx, screen_height=cyy, num_stars=50)

# Startujemy gracza w centrum świata
player_start_pos = [WORLD_CENTER.x, WORLD_CENTER.y]
player = space_ship.SpaceShip(loaded_space_frames, [], audio_files, cxx, cyy, player_start_pos, music_obj)
enemy_manager = EnemyManager(loaded_space_frames, player, music_obj, max_enemies=15)
events_obj = Event()
colision_obj = collisions.Collision(music_obj)



# Inicjalizacja pozycji kamery na graczu
cam_x, cam_y = player.player_pos.x, player.player_pos.y

# --- PĘTLA GŁÓWNA ---
running = True
enemy_manager.spawn_test_targets(5)
while running:
    dt = clock.tick(FPS) / 1000.0 
    
    events_obj.update() # Przekazujemy pojedynczy event do klasy Event

    if events_obj.key_escape or events_obj.system_exit:
        music_obj.at_exit()
        running = False
        break

    # 2. AKTUALIZACJA LOGIKI
    player.update(dt, events_obj)
    enemy_manager.update(dt)

    # --- FIZYKA BARIERY ŚWIATA ---
    distance = player.player_pos.distance_to(WORLD_CENTER)
    if distance > WORLD_RADIUS:
        # Oblicz wektor odpychający (od środka do gracza)
        outward_dir = (player.player_pos - WORLD_CENTER).normalize()
        # Cofnij gracza na krawędź
        player.player_pos = WORLD_CENTER + outward_dir * WORLD_RADIUS
        # Odbicie (odwrócenie prędkości i jej osłabienie)
        player.velocity *= -0.3 

    # 3. KOLIZJE
    if colision_obj.check_collisions(player, enemy_manager):
        print("PLAYER DESTROYED")
        # Tu można dodać logikę restartu

    # 4. MIĘKKA KAMERA (Smoothing)
    cam_x += (player.player_pos.x - cam_x) * 0.175
    cam_y += (player.player_pos.y - cam_y) * 0.175

    # Offset dla rysowania obiektów świata
    screen_off_x = cam_x - (cxx // 2)
    screen_off_y = cam_y - (cyy // 2)

    # 5. RYSOWANIE
    # A. Niekończące się tło gwiazd
    bg.draw(window, (cam_x, cam_y))

    # B. Wizualna bariera (Glow)
    start_warning_dist = WORLD_RADIUS - FADE_ZONE
    if distance > start_warning_dist:
        intensity = (distance - start_warning_dist) / FADE_ZONE
        intensity = max(0, min(1.0, intensity))
        alpha = int(intensity * 255)
        
        # Pozycja środka świata na ekranie
        rel_center_x = int(WORLD_CENTER.x - screen_off_x)
        rel_center_y = int(WORLD_CENTER.y - screen_off_y)
        
        # Rysujemy barierę na warstwie z alpha
        temp_surface = pygame.Surface((cxx, cyy), pygame.SRCALPHA)
        # Czerwona poświata krawędziowa
        pygame.draw.circle(temp_surface, (255, 0, 0, alpha // 4), (rel_center_x, rel_center_y), WORLD_RADIUS, 1980)

        # B. Główna bariera (środkowa)

        pygame.draw.circle(temp_surface, (255, 0, 0, alpha // 2), (rel_center_x, rel_center_y), WORLD_RADIUS, 80)

        # C. Ostra krawędź (wewnętrzna)

        pygame.draw.circle(temp_surface, (255, 50, 50, alpha), (rel_center_x, rel_center_y), WORLD_RADIUS, 10)
        window.blit(temp_surface, (0, 0))

    # C. Przeciwnicy
    for enemy in enemy_manager.enemies:
        enemy.draw(window, screen_off_x, screen_off_y)

    # D. Gracz (z poprawką na pozycję kamery)
    player_draw_x = (cxx // 2) + (player.player_pos.x - cam_x)
    player_draw_y = (cyy // 2) + (player.player_pos.y - cam_y)
    player.draw(window, player_draw_x, player_draw_y)

    # 6. ODŚWIEŻENIE
    pygame.display.flip()

pygame.quit()