import pygame
import load_images
import space_ship
from sky import SpaceBackground
import enemy_ship
import time

pygame.init()

clock = pygame.time.Clock()

window = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
pygame.display.set_caption("Kosmos")

image_load = load_images.ImageLoad()

space_frames = ["images/space_ships/playerShip1_blue.png","images/space_ships/playerShip1_green.png","images/space_ships/playerShip1_orange.png","images/space_ships/playerShip1_red.png","images/space_ships/playerShip2_blue.png","images/space_ships/playerShip2_green.png","images/space_ships/playerShip2_orange.png","images/space_ships/playerShip2_red.png","images/space_ships/playerShip3_blue.png","images/space_ships/playerShip3_green.png","images/space_ships/playerShip3_orange.png","images/space_ships/playerShip3_red.png","images/space_ships/spaceShips_001.png","images/space_ships/spaceShips_002.png","images/space_ships/spaceShips_003.png","images/space_ships/spaceShips_004.png","images/space_ships/spaceShips_005.png","images/space_ships/spaceShips_006.png","images/space_ships/spaceShips_007.png","images/space_ships/spaceShips_008.png","images/space_ships/spaceShips_009.png","images/space_ships/ufoBlue.png","images/space_ships/ufoGreen.png","images/space_ships/ufoRed.png","images/space_ships/ufoYellow.png"]
space_parts = []
audio_files = []

loaded_space_frames = []
for i in space_frames:
    loaded_space_frames.append(image_load.get_image(i,100))


WORLD_SIZE = 5000000 # To jest tylko logiczna granica, nie fizyczna powierzchnia
TILE_WIDTH = 1920
TILE_HEIGHT = 1080

#bg = SpaceBackground(width=100000, height=100000, screen_width=1920, screen_height=1080,num_stars=10000)
bg = SpaceBackground(tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT, screen_width=1920, screen_height=1080, num_stars=50)
player_pos = [WORLD_SIZE // 2, WORLD_SIZE // 2] # Utrzymaj gracza w środku logicznego świata
player_pos = [5000,5000]

player = space_ship.SpaceShip(loaded_space_frames,space_parts,audio_files,1920,1080, player_pos)

audio_files = []
enemie = enemy_ship.EnemyShip(loaded_space_frames,space_parts,audio_files,1920,1080, player_pos)

running = True

scroll_up = False
scroll_down = False



clock = pygame.time.Clock()
FPS = 60

key_up = key_down = key_right = key_left = False
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                key_left = True
            elif event.key == pygame.K_RIGHT:
                key_right = True
            elif event.key == pygame.K_UP:
                key_up = True
            elif event.key == pygame.K_DOWN:
                key_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                key_left = False
            elif event.key == pygame.K_RIGHT:
                key_right = False
            elif event.key == pygame.K_UP:
                key_up = False
            elif event.key == pygame.K_DOWN:
                key_down = False

    """# Aktualizacja pozycji gracza
    if moving_left:
        player_pos[0] -= 5
    if moving_right:
        player_pos[0] += 5
    if moving_up:
        player_pos[1] -= 5
    if moving_down:
        player_pos[1] += 5"""
    player_pos = player.update(key_up, key_down, key_right, key_left)
    enemy_update = enemie.update()
    
    bg.draw(window, player_pos)
    player.draw(window)
    enemie.draw(window,player_pos[0],player_pos[1])

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()