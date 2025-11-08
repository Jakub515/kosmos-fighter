import pygame
import math

class SpaceShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path, cxx, cyy, player_pos):
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path
        self.laser_music = pygame.mixer.Sound("images/audio/sfx_laser1.wav")
        self.laser_music.set_volume(0.7)
        
        self.actual_frame = pygame.transform.rotate(
            self.ship_frames["images/space_ships/playerShip1_blue.png"], -90
        )
        self.cxx = cxx
        self.cyy = cyy

        self.player_pos = pygame.math.Vector2(player_pos[0], player_pos[1])
        self.angle = 90
        self.speed = 0
        self.max_speed = 15

        self.player_rect = None

        # Wgrane bronie: [obrazek, prędkość, damage, reload]
        self.weapons = [
            [self.ship_frames["images/Lasers/laserBlue12.png"], 60, 5, 0.5],
            [self.ship_frames["images/Lasers/laserBlue13.png"], 65, 4, 0.4],
            [self.ship_frames["images/Lasers/laserBlue14.png"], 70, 3, 0.3],
            [self.ship_frames["images/Lasers/laserBlue15.png"], 75, 2, 0.2],
            [self.ship_frames["images/Lasers/laserBlue16.png"], 80, 1, 0.1]
        ]
        self.weapon_timers = [0.0 for _ in self.weapons]  # timer reloadu dla każdej broni

        self.shots = []
        self.current_weapon = 0

    def update(self, key_up, key_down, key_right, key_left, space, numbers, dt):
        """
        dt - delta time w sekundach od ostatniej klatki
        """
        # Zmiana broni
        for index, i in enumerate(numbers):
            if i:
                self.current_weapon = index

        # Sterowanie statkiem
        if key_right:
            self.angle -= 1.5
        if key_left:
            self.angle += 1.5
        if key_up:
            if self.speed < self.max_speed:
                self.speed += 0.1
        else:
            if self.speed > 0:
                self.speed -= 0.05
            else:
                self.speed = 0
        if key_down:
            self.speed -= 0.05
            if self.speed < 0:
                self.speed = 0

        # Ruch statku
        direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.player_pos += direction * self.speed

        # Aktualizacja timerów reloadu broni
        for i in range(len(self.weapon_timers)):
            self.weapon_timers[i] += dt

        # Strzał w kierunku statku
        if space:
            weapon_data = self.weapons[self.current_weapon]
            reload_time = weapon_data[3]

            if self.weapon_timers[self.current_weapon] >= reload_time:
                self.weapon_timers[self.current_weapon] = 0.0

                # Kierunek pocisku = kierunek statku
                shot_direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
                direction_angle = self.angle  # do obrotu obrazka pocisku

                # Startowa pozycja = dokładny środek obrotu statku w świecie
                shot_start_pos = self.player_pos.copy()

                self.shots.append({
                    "pos": shot_start_pos,
                    "vel": shot_direction * weapon_data[1],
                    "img": weapon_data[0],
                    "damage": weapon_data[2],
                    "dir": direction_angle
                })
                self.laser_music.play()

        # Aktualizacja pocisków
        for shot in self.shots:
            shot["pos"] += shot["vel"]

        return [self.player_pos.x, self.player_pos.y]


    def draw(self, window):
        # Obrót statku wokół środka sprite'a
        rotated_image = pygame.transform.rotate(self.actual_frame, self.angle)
        rect = rotated_image.get_rect(center=(self.cxx // 2+5, self.cyy // 2+35))  # zawsze środek ekranu

        # Kamera
        camera_x = self.player_pos.x - (self.cxx // 2)
        camera_y = self.player_pos.y - (self.cyy // 2)

        # Rysowanie pocisków
        for shot in self.shots:
            screen_x = shot["pos"].x - camera_x
            screen_y = shot["pos"].y - camera_y
            window.blit(pygame.transform.rotate(shot["img"], shot["dir"]+90), (screen_x, screen_y))

        # Rysowanie statku
        window.blit(rotated_image, rect.topleft)
