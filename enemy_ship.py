import pygame
import random
import time

class EnemyShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path, cxx, cyy, player_pos):
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path
        
        self.actual_frame = pygame.transform.rotate(self.ship_frames["images/space_ships/spaceShips_009.png"], -90)
        self.cxx = cxx
        self.cyy = cyy

        self.player_pos = pygame.math.Vector2(player_pos[0], player_pos[1])
        self.angle = 90
        self.speed = 0
        self.max_speed = 15

        # 🔧 przesunięcie środka obrotu (np. 20 px w dół)
        self.pivot_offset = pygame.Vector2(0, 0)

        self.random_last_time = 0

        self.key_up = self.key_down = self.key_right = self.key_left = False

    def update(self):
        if (time.time() - self.random_last_time > 1) or self.random_last_time == 0:
            self.key_up = random.random() < 0.7
            self.key_down = random.random() < 0.3
            self.key_right = random.random() < 0.1
            self.key_left = random.random() < 0.1
            self.random_last_time = time.time()

        if self.key_right:
            self.angle -= 1.5
        if self.key_left:
            self.angle += 1.5
        if self.key_up:
            if not self.speed > self.max_speed:
                self.speed += 0.1
        else:
            if self.speed > 0:
                self.speed -= 0.05
        if self.key_down:
            self.speed -= 0.05
            if self.speed < 0:
                self.speed = 0

        direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.player_pos += direction * self.speed
        return [self.player_pos.x, self.player_pos.y]

    def draw(self, window, player_x, player_y):
        # Obrót obrazka
        rotated_image = pygame.transform.rotozoom(self.actual_frame, self.angle, 1)
        offset_rotated = self.pivot_offset.rotate(self.angle)

        # --- 📷 Kamera – pozycja gracza jako środek ekranu ---
        camera_x = player_x - (self.cxx // 2) + 25  # 25 = połowa szerokości gracza (50px)
        camera_y = player_y - (self.cyy // 2)

        # --- 🌍 Pozycja wroga na ekranie względem kamery ---
        screen_x = self.player_pos.x - camera_x
        screen_y = self.player_pos.y - camera_y

        # --- 🎯 Ustawienie środka sprite'a ---
        rect = rotated_image.get_rect(center=(screen_x, screen_y))
        window.blit(rotated_image, rect.topleft)
