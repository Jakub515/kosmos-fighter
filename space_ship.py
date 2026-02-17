import pygame
import math

class SpaceShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path, cxx, cyy, player_pos, music, shoot_obj):
        self.shoot_obj = shoot_obj
        self.music_obj = music
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path
        
        # --- GRAFIKA PODSTAWOWA ---
        self.original_image = self.ship_frames["images/space_ships/playerShip1_blue.png"]
        self.actual_frame = pygame.transform.rotate(self.original_image, -90)
        
        # --- OGIEŃ SILNIKA ---
        try:
            self.engine_image = self.ship_frames["images/Effects/fire03.png"]
        except KeyError:
            self.engine_image = pygame.Surface((20, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(self.engine_image, (255, 150, 0), (0,0,20,40))

        # --- FLAGI STEROWANIA (Zamiast czytania event_obj) ---
        self.is_thrusting = False
        self.is_braking = False
        self.is_boosting = False
        self.rotation_dir = 0  # 0: brak, 1: lewo, -1: prawo
        self.want_to_shoot = False

        # --- OSŁONY ---
        try:
            self.shield_frames = [
                self.ship_frames["images/Effects/shield1.png"],
                self.ship_frames["images/Effects/shield2.png"],
                self.ship_frames["images/Effects/shield3.png"]
            ]
        except KeyError:
            self.shield_frames = [self._create_placeholder_shield(r, (100, 200, 255)) for r in [50, 55, 60]]
            
        self.shield_active = False
        self.shield_timer = 0       
        self.shield_angle = 0       

        self.cxx = cxx
        self.cyy = cyy
        self.hp = 1
        self.max_hp = 1

        # --- FIZYKA ---
        self.player_pos = pygame.math.Vector2(player_pos[0], player_pos[1])
        self.velocity = pygame.math.Vector2(0, 0)  
        self.angle = 90                                     
        self.angular_velocity = 0                  
        self.angular_acceleration = 0.4            
        self.angular_friction = 0.92               
        self.max_angular_velocity = 6.0            
        self.thrust_power = 0.3                    
        self.max_speed = 12.0                      
        self.boost_speed = 30.0                    
        self.linear_friction = 0.995               
        self.braking_force = 0.96                  
        self.speed_decay = 0.98                    

        # --- SYSTEM BRONI ---
        self.weapons = [
            [self.ship_frames["images/Lasers/laserBlue12.png"], 60, 5,   0.1],
            [self.ship_frames["images/Lasers/laserBlue13.png"], 65, 4,   0.4],
            [self.ship_frames["images/Lasers/laserBlue14.png"], 70, 3,   0.3],
            [self.ship_frames["images/Lasers/laserBlue15.png"], 75, 2,   0.2],
            [self.ship_frames["images/Lasers/laserBlue16.png"], 80, 1,   0.1]
        ]
        self.weapons_2 = [
            [self.ship_frames["images/Missiles/spaceMissiles_001.png"], 40, 5,   3],
            [self.ship_frames["images/Missiles/spaceMissiles_004.png"], 40, 10,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_007.png"], 40, 15,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_010.png"], 40, 20,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_013.png"], 40, 25,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_016.png"], 40, 30,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_019.png"], 40, 35,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_022.png"], 40, 40,  3],
            [self.ship_frames["images/Missiles/spaceMissiles_025.png"], 40, 45,  3]
        ]
        
        self.weapon_timers = [0.0 for _ in self.weapons]
        self.weapon_timers_2 = [0.0 for _ in self.weapons_2]
        
        self.current_weapon = 0
        self.active_set = 1  # 1: Lasery, 2: Rakiety

    def _create_placeholder_shield(self, radius, color):
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (radius, radius), radius, 3)
        return s

    # --- NOWE METODY INTERFEJSU (Wywoływane przez Controller/Main) ---

    def thrust(self, active, boost=False):
        self.is_thrusting = active
        self.is_boosting = boost

    def rotate(self, direction):
        """direction: 1 dla lewo, -1 dla prawo, 0 dla stop"""
        self.rotation_dir = direction

    def brake(self, active):
        self.is_braking = active

    def fire(self, active):
        self.want_to_shoot = active

    def switch_weapon_set(self):
        self.active_set = 2 if self.active_set == 1 else 1
        self.current_weapon = 0

    def select_weapon(self, index):
        if self.active_set == 1 and index < len(self.weapons):
            self.current_weapon = index
        elif self.active_set == 2 and index < len(self.weapons_2):
            self.current_weapon = index

    def activate_shield(self, timer=250):
        self.shield_active = True
        self.shield_timer = timer

    # --- ZMODYFIKOWANY UPDATE (Bez event_obj) ---

    def update(self, dt):
        # 1. ROTACJA
        if self.rotation_dir == 1:
            self.angular_velocity += self.angular_acceleration
        elif self.rotation_dir == -1:
            self.angular_velocity -= self.angular_acceleration
        
        self.angular_velocity *= self.angular_friction
        if abs(self.angular_velocity) > self.max_angular_velocity:
            self.angular_velocity = math.copysign(self.max_angular_velocity, self.angular_velocity)
        
        self.angle += self.angular_velocity

        # 2. RUCH LINIOWY
        rad = math.radians(-self.angle)
        forward_direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))

        if self.is_thrusting:
            accel = self.thrust_power + (1.5 if self.is_boosting else 0)
            self.velocity += forward_direction * accel
        
        if self.is_braking:
            if self.velocity.length() > 1.0:
                self.velocity *= self.braking_force
            else:
                self.velocity -= forward_direction * (self.thrust_power * 0.4)

        # 3. TARCIE I LIMIT PRĘDKOŚCI
        current_speed = self.velocity.length()
        if self.is_boosting:
            if current_speed > self.boost_speed: self.velocity.scale_to_length(self.boost_speed)
        else:
            if current_speed > self.max_speed: self.velocity *= self.speed_decay
            else: self.velocity *= self.linear_friction

        if current_speed < 0.1: self.velocity = pygame.math.Vector2(0, 0)
        self.player_pos += self.velocity

        # 4. OSŁONY
        if self.shield_active:
            self.shield_angle += 25 
            self.shield_timer -= 1
            if self.shield_timer <= 0: self.shield_active = False

        # 5. STRZELANIE
        for i in range(len(self.weapon_timers)): self.weapon_timers[i] += dt
        for i in range(len(self.weapon_timers_2)): self.weapon_timers_2[i] += dt

        if self.want_to_shoot:
            if self.active_set == 1:
                weapon_data = self.weapons[self.current_weapon]
                if self.weapon_timers[self.current_weapon] >= weapon_data[3]:
                    self.weapon_timers[self.current_weapon] = 0.0
                    shot_vel = forward_direction * weapon_data[1]
                    self.shoot_obj.create_missle({
                        "pos": self.player_pos.copy(), "vel": shot_vel, "img": weapon_data[0],
                        "damage": weapon_data[2], "dir": self.angle
                    })
                    self.music_obj.play("images/audio/sfx_laser1.wav", 0.7)
            else:
                weapon_data = self.weapons_2[self.current_weapon]
                if self.weapon_timers_2[self.current_weapon] >= weapon_data[3]:
                    self.weapon_timers_2[self.current_weapon] = 0.0
                    shot_vel = forward_direction * weapon_data[1]
                    self.shoot_obj.create_missle({
                        "pos": self.player_pos.copy(), "vel": shot_vel, "img": weapon_data[0],
                        "damage": weapon_data[2], "dir": self.angle,
                        "rocket": True 
                    })
                    self.music_obj.play("images/audio/sfx_laser1.wav", 0.7)

        return [self.player_pos.x, self.player_pos.y]

    def draw(self, window, draw_x, draw_y):
        # Rysowanie pozostaje bez zmian
        if self.is_thrusting:
            fire_rot = pygame.transform.rotate(self.engine_image, self.angle)
            fire_offset = pygame.math.Vector2(-40, 0).rotate(-self.angle)
            fire_rect = fire_rot.get_rect(center=(int(draw_x + fire_offset.x), int(draw_y + fire_offset.y)))
            window.blit(fire_rot, fire_rect)

        rotated_image = pygame.transform.rotate(self.actual_frame, self.angle)
        rect = rotated_image.get_rect(center=(draw_x, draw_y))
        window.blit(rotated_image, rect.topleft)

        if self.shield_active:
            frame_idx = (self.shield_timer // 3) % 3
            shield_rot = pygame.transform.rotate(self.shield_frames[frame_idx], self.shield_angle)
            s_rect = shield_rot.get_rect(center=(draw_x, draw_y))
            shield_rot.set_alpha(150 + (self.shield_timer % 2) * 50)
            window.blit(shield_rot, s_rect)