import pygame
import math

class SpaceShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path, cxx, cyy, player_pos):
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path
        
        # Audio
        self.laser_music = pygame.mixer.Sound("images/audio/sfx_laser1.wav")
        self.laser_music.set_volume(0.7)
        
        # Grafika podstawowa
        self.actual_frame = pygame.transform.rotate(
            self.ship_frames["images/space_ships/playerShip1_blue.png"], -90
        )
        self.cxx = cxx
        self.cyy = cyy

        # --- FIZYKA ZAAWANSOWANA ---
        self.player_pos = pygame.math.Vector2(player_pos[0], player_pos[1])
        self.velocity = pygame.math.Vector2(0, 0)  
        self.angle = 90                            
        
        # Parametry obrotu
        self.angular_velocity = 0                  
        self.angular_acceleration = 0.4            
        self.angular_friction = 0.92               
        self.max_angular_velocity = 6.0            

        # Parametry ruchu liniowego
        self.thrust_power = 0.3                    
        self.max_speed = 12.0                      # Prędkość normalna
        self.boost_speed = 30.0                    # Prędkość maksymalna na boostcie
        self.linear_friction = 0.995               # Tarcie w próżni (dryf)
        self.braking_force = 0.96                  # Siła aktywnego hamowania (key_down)
        self.speed_decay = 0.98                    # Powrót z boosta do max_speed

        # --- SYSTEM BRONI ---
        self.weapons = [
            [self.ship_frames["images/Lasers/laserBlue12.png"], 60, 5, 0.5],
            [self.ship_frames["images/Lasers/laserBlue13.png"], 65, 4, 0.4],
            [self.ship_frames["images/Lasers/laserBlue14.png"], 70, 3, 0.3],
            [self.ship_frames["images/Lasers/laserBlue15.png"], 75, 2, 0.2],
            [self.ship_frames["images/Lasers/laserBlue16.png"], 80, 1, 0.1]
        ]
        self.weapon_timers = [0.0 for _ in self.weapons]
        self.shots = []
        self.current_weapon = 0

    def update(self, key_up, key_down, key_right, key_left, space, numbers, dt, speedup):
        # 1. Zmiana broni
        for index, i in enumerate(numbers):
            if i:
                self.current_weapon = index

        # 2. FIZYKA OBROTU
        if key_left:
            self.angular_velocity += self.angular_acceleration
        if key_right:
            self.angular_velocity -= self.angular_acceleration

        self.angular_velocity *= self.angular_friction
        
        if abs(self.angular_velocity) > self.max_angular_velocity:
            self.angular_velocity = math.copysign(self.max_angular_velocity, self.angular_velocity)
        
        self.angle += self.angular_velocity

        # 3. FIZYKA RUCHU
        rad = math.radians(-self.angle)
        forward_direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))

        # Przyśpieszanie
        if key_up:
            accel = self.thrust_power
            if speedup:
                accel += 0.5  # Dodatkowa moc boosta
            self.velocity += forward_direction * accel
        
        # Hamowanie i bieg wsteczny
        if key_down:
            if self.velocity.length() > 1.0:
                # Aktywne hamowanie (przeciwciąg) - znacznie mocniejsze niż tarcie
                self.velocity *= self.braking_force
            else:
                # Powolne cofanie
                self.velocity -= forward_direction * (self.thrust_power * 0.4)

        # --- LOGIKA LIMITU PRĘDKOŚCI I POWROTU Z BOOST ---
        current_speed = self.velocity.length()
        
        if speedup:
            # Limit dla boosta
            if current_speed > self.boost_speed:
                self.velocity.scale_to_length(self.boost_speed)
        else:
            # Jeśli nie trzymamy boosta, a lecimy szybciej niż max_speed
            if current_speed > self.max_speed:
                # Płynne wytracanie prędkości nadmiarowej
                self.velocity *= self.speed_decay
            else:
                # Normalne tarcie w kosmosie
                self.velocity *= self.linear_friction

        # Martwa strefa (zatrzymanie całkowite)
        if current_speed < 0.1:
            self.velocity = pygame.math.Vector2(0, 0)

        # Aktualizacja pozycji
        self.player_pos += self.velocity

        # 4. AKTUALIZACJA TIMERÓW RELOADU
        for i in range(len(self.weapon_timers)):
            self.weapon_timers[i] += dt

        # 5. STRZELANIE
        if space:
            weapon_data = self.weapons[self.current_weapon]
            reload_time = weapon_data[3]

            if self.weapon_timers[self.current_weapon] >= reload_time:
                self.weapon_timers[self.current_weapon] = 0.0
                shot_direction = forward_direction.copy()
                velocity_of_shot = shot_direction * weapon_data[1]

                self.shots.append({
                    "pos": self.player_pos.copy(),
                    "vel": velocity_of_shot,
                    "img": weapon_data[0],
                    "damage": weapon_data[2],
                    "dir": self.angle
                })
                self.laser_music.play()

        # 6. AKTUALIZACJA POCISKÓW
        for shot in self.shots:
            shot["pos"] += shot["vel"]

        return [self.player_pos.x, self.player_pos.y]

    def draw(self, window):
        rotated_image = pygame.transform.rotate(self.actual_frame, self.angle)
        rect = rotated_image.get_rect(center=(self.cxx // 2, self.cyy // 2))

        camera_x = self.player_pos.x - (self.cxx // 2)
        camera_y = self.player_pos.y - (self.cyy // 2)

        for shot in self.shots:
            screen_x = shot["pos"].x - camera_x
            screen_y = shot["pos"].y - camera_y
            rotated_laser = pygame.transform.rotate(shot["img"], shot["dir"] + 90)
            window.blit(rotated_laser, (screen_x, screen_y))

        window.blit(rotated_image, rect.topleft)