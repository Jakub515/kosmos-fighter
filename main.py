import pygame
import load_images
import space_ship
from sky import SpaceBackground
import os
import collisions
from collections import defaultdict
from functions import Event
from enemy_ship import EnemyManager
import music
import shoot
import radar
import ui

# --- INICJALIZACJA ---
pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
FPS = 60
# Ustawienie trybu pełnoekranowego
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
cxx, cyy = window.get_size()
pygame.display.set_caption("Kosmos")

image_load = load_images.ImageLoad()

# --- KONFIGURACJA ŚWIATA ---
WORLD_CENTER = pygame.math.Vector2(0, 0)
WORLD_RADIUS = 10000    # Fizyczna granica
FADE_ZONE = 2000       # Dystans, od którego pojawia się ostrzeżenie

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

# Ładowanie obrazów z optymalizacją (convert_alpha wywoływane w ImageLoad)
loaded_space_frames = {path: image_load.get_image(path, 40) for path in space_frames}
loaded_space_frames_full = {path: image_load.get_image(path, 100) for path in space_frames}

music_obj = music.MusicManager(audio_files)

# --- OBIEKTY GRY ---
bg = SpaceBackground(tile_width=cxx, tile_height=cyy, screen_width=cxx, screen_height=cyy, num_stars=50)
shoot_obj = shoot.Shoot(loaded_space_frames)

# Startujemy gracza w centrum świata
player_start_pos = [WORLD_CENTER.x, WORLD_CENTER.y]
player = space_ship.SpaceShip(loaded_space_frames, [], audio_files, cxx, cyy, player_start_pos, music_obj, shoot_obj)

# Manager wrogów (przekazujemy shoot_obj do obsługi ich pocisków)
enemy_manager = EnemyManager(loaded_space_frames, player, music_obj, 20, shoot_obj)
events_obj = Event()
colision_obj = collisions.Collision(music_obj)
radar_obj = radar.Radar(cxx,cyy,radar_size=200,world_radius=WORLD_RADIUS,zoom_radius=4000)

game_controller = ui.GameController(events_obj, player, cxx, cyy, loaded_space_frames_full)

# Inicjalizacja pozycji kamery
cam_x, cam_y = player.player_pos.x, player.player_pos.y

# --- PĘTLA GŁÓWNA ---
running = True
# Spawnujemy cele testowe (nieruchome, zoptymalizowane pod kątem update)
# enemy_manager.spawn_test_targets(5)

while running:
    # dt w sekundach
    dt = clock.tick(FPS) / 1000.0 
    
    # 1. EVENTY
    events_obj.update() 

    if events_obj.key_escape or events_obj.system_exit:
        music_obj.at_exit()
        running = False
        break

    game_controller.update(dt)

    # 2. AKTUALIZACJA LOGIKI
    player.update(dt)
    enemy_manager.update(dt)
    shoot_obj.update()

    # --- FIZYKA BARIERY ŚWIATA ---
    distance = player.player_pos.distance_to(WORLD_CENTER)
    if distance > WORLD_RADIUS:
        outward_dir = (player.player_pos - WORLD_CENTER).normalize()
        player.player_pos = WORLD_CENTER + outward_dir * WORLD_RADIUS
        player.velocity *= -0.3 # Odbicie od niewidzialnej ściany

    # 3. KOLIZJE (zgodne z Twoją nową klasą Collision)
    # Zwraca True, jeśli HP gracza spadnie do 0
    if colision_obj.check_collisions(player, enemy_manager, shoot_obj):
        print("GAME OVER - PLAYER DESTROYED")
        # Tu można dodać restart: player.hp = 100, player.player_pos = WORLD_CENTER.copy()

    # 4. KAMERA (Płynne podążanie)
    cam_x += (player.player_pos.x - cam_x) * 0.1
    cam_y += (player.player_pos.y - cam_y) * 0.1

    # Offsety do rysowania obiektów względem kamery
    screen_off_x = cam_x - (cxx // 2)
    screen_off_y = cam_y - (cyy // 2)

    # 5. RYSOWANIE
    # A. Tło
    bg.draw(window, (cam_x, cam_y))

    # B. Wizualna bariera świata
    start_warning_dist = WORLD_RADIUS - FADE_ZONE
    if distance > start_warning_dist:
        intensity = (distance - start_warning_dist) / FADE_ZONE
        intensity = max(0, min(1.0, intensity))
        alpha = int(intensity * 255)
        
        rel_center_x = int(WORLD_CENTER.x - screen_off_x)
        rel_center_y = int(WORLD_CENTER.y - screen_off_y)
        
        # Tworzymy powierzchnię alpha tylko gdy jest potrzebna
        temp_surface = pygame.Surface((cxx, cyy), pygame.SRCALPHA)
        # Efekt poświaty
        pygame.draw.circle(temp_surface, (255, 0, 0, alpha // 4), (rel_center_x, rel_center_y), WORLD_RADIUS, 500)
        # Ostra krawędź
        pygame.draw.circle(temp_surface, (255, 50, 50, alpha), (rel_center_x, rel_center_y), WORLD_RADIUS, 15)
        window.blit(temp_surface, (0, 0))

    # C. Pociski (zintegrowane z kamerą)
    # Przekazujemy offsety kamery, aby pociski poruszały się wraz ze światem
    shoot_obj.draw(window, screen_off_x, screen_off_y)

    # D. Przeciwnicy
    enemy_manager.draw(window, screen_off_x, screen_off_y)

    # E. Gracz
    # Rysujemy gracza na środku ekranu, uwzględniając drobne przesunięcia względem "wygładzonej" kamery
    player_draw_x = (cxx // 2) + (player.player_pos.x - cam_x)
    player_draw_y = (cyy // 2) + (player.player_pos.y - cam_y)
    player.draw(window, player_draw_x, player_draw_y)
    radar_obj.draw(window, player, enemy_manager, dt)
    game_controller.draw(window)

    # 6. ODŚWIEŻENIE
    pygame.display.flip()

pygame.font.quit()
pygame.quit()