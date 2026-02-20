import pygame
import math
import random

class Enemy:
    def __init__(self, ship_frames, player_ref, music_obj, shoot_obj, enemy_manager, spawn_radius=1000, behavior=None):
        self.music_obj = music_obj
        self.ship_frames = ship_frames
        self.player_ref = player_ref
        self.shoot_obj = shoot_obj
        self.manager = enemy_manager

        self.behavior_type = behavior if behavior is not None else 0
            
        enemy_types = [
            ("images/Enemies/enemyBlack1.png", 0.3, 1),
            ("images/Enemies/enemyBlack2.png", 0.25, 1),
            ("images/Enemies/enemyBlack3.png", 0.2, 1)
        ]
        self.texture_path, self.thrust_power, self.hp = random.choice(enemy_types)
        self.image = pygame.transform.rotate(self.ship_frames[self.texture_path], -90)

        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(spawn_radius * 0.8, spawn_radius)
        self.pos = pygame.math.Vector2(
            self.player_ref.player_pos.x + math.cos(angle) * distance,
            self.player_ref.player_pos.y + math.sin(angle) * distance
        )
        
        # --- FIZYKA ---
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = random.uniform(0, 360)
        self.angular_velocity = 0
        self.angular_acceleration = 0.4
        self.angular_friction = 0.92
        self.max_angular_velocity = 6.0
        self.max_speed = 10.0
        self.linear_friction = 0.995
        self.speed_decay = 0.98

        self.weapons = [
            [self.ship_frames["images/Lasers/laserRed01.png"], 40, 5, 0.6],
            [self.ship_frames["images/Lasers/laserRed02.png"], 50, 3, 0.5],
            [self.ship_frames["images/Lasers/laserRed03.png"], 60, 2, 0.4],
            [self.ship_frames["images/Lasers/laserRed04.png"], 70, 1, 0.3],
            [self.ship_frames["images/Lasers/laserRed05.png"], 80, 0.5, 0.2],
        ]
        self.current_weapon = random.randint(0, len(self.weapons) - 1)
        self.weapon_timers = [0.0 for _ in range(len(self.weapons))]
        
        self.is_thrusting = False
        self.avoidance_side = random.choice([-1, 1])
        self.logic_timer = random.uniform(0, 0.1)

    def update(self, dt):
        if self.behavior_type == 3: 
            for i in range(len(self.weapon_timers)): self.weapon_timers[i] += dt
            return 

        for i in range(len(self.weapon_timers)):
            self.weapon_timers[i] += dt

        # --- 1. ANALIZA OTOCZENIA ---
        dir_to_player = (self.player_ref.player_pos - self.pos)
        dist_to_player = dir_to_player.length()
        if dist_to_player == 0: dist_to_player = 1
        
        target_angle = -math.degrees(math.atan2(dir_to_player.y, dir_to_player.x))
        base_target_angle = target_angle

        # --- 2. AKTYWNE UNIKANIE INNYCH BOTÓW ---
        avoid_neighbor_vector = pygame.math.Vector2(0, 0)
        too_close_to_someone = False
        
        for other in self.manager.enemies:
            if other is self: continue
            dist_to_other = self.pos.distance_to(other.pos)
            if dist_to_other < 180: 
                too_close_to_someone = True
                diff = self.pos - other.pos
                avoid_neighbor_vector += diff.normalize() * (200 - dist_to_other)

        if too_close_to_someone:
            avoid_angle = -math.degrees(math.atan2(avoid_neighbor_vector.y, avoid_neighbor_vector.x))
            target_angle = avoid_angle
        else:
            if dist_to_player < 450:
                target_angle = base_target_angle + (40 * self.avoidance_side)

        # --- 3. UNIKANIE KOLIZJI Z GRACZEM ---
        collision_danger_player = False
        if self.velocity.length() > 2:
            vel_dir = self.velocity.normalize()
            if vel_dir.dot(dir_to_player.normalize()) > 0.8: 
                collision_danger_player = True

        if dist_to_player < 280 and collision_danger_player:
            target_angle = base_target_angle + (90 * self.avoidance_side)

        # --- 4. FIZYKA OBROTU ---
        angle_diff = (target_angle - self.angle + 180) % 360 - 180

        if angle_diff > 4:
            self.angular_velocity += self.angular_acceleration
        elif angle_diff < -4:
            self.angular_velocity -= self.angular_acceleration
        
        self.angular_velocity *= self.angular_friction
        if abs(self.angular_velocity) > self.max_angular_velocity:
            self.angular_velocity = math.copysign(self.max_angular_velocity, self.angular_velocity)
        
        self.angle += self.angular_velocity

        # --- 5. CIĄG ---
        rad = math.radians(-self.angle)
        forward_dir = pygame.math.Vector2(math.cos(rad), math.sin(rad))

        self.is_thrusting = False
        
        if too_close_to_someone:
            if abs(angle_diff) < 90:
                self.is_thrusting = True
        elif (collision_danger_player and dist_to_player < 400):
            if abs(angle_diff) < 60: 
                self.is_thrusting = True
        elif abs(angle_diff) < 30 and dist_to_player > 380:
            self.is_thrusting = True

        if self.is_thrusting:
            self.velocity += forward_dir * self.thrust_power

        # --- 6. BEZWŁADNOŚĆ I POZYCJA ---
        current_speed = self.velocity.length()
        if current_speed > self.max_speed:
            self.velocity *= self.speed_decay
        else:
            self.velocity *= self.linear_friction

        self.pos += self.velocity

        # --- NOWE: LOGIKA BARIERY ŚWIATA ---
        # Używamy WORLD_RADIUS zdefiniowanego w EnemyManager
        if self.pos.length() > self.manager.world_radius:
            outward_dir = self.pos.normalize()
            self.pos = outward_dir * self.manager.world_radius
            self.velocity *= -0.5  # Odbicie od krawędzi
            self.avoidance_side *= -1  # Zmiana kierunku krążenia po uderzeniu

        # --- 7. STRZELANIE ---
        real_aim_diff = (base_target_angle - self.angle + 180) % 360 - 180
        if abs(real_aim_diff) < 15 and dist_to_player < 700:
            self.shoot()

    def shoot(self):
        weapon = self.weapons[self.current_weapon]
        if self.weapon_timers[self.current_weapon] >= weapon[3]:
            self.weapon_timers[self.current_weapon] = 0.0
            rad = math.radians(-self.angle)
            direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
            self.shoot_obj.create_missle({
                "pos": self.pos.copy(),
                "vel": direction * weapon[1],
                "img": weapon[0],
                "damage": weapon[2],
                "dir": self.angle,
                "is_enemy_shot": True
            })
            self.music_obj.play("images/audio/sfx_laser2.wav", 0.05)

    def draw(self, window, camera_x, camera_y):
        if self.is_thrusting:
            try:
                engine_img = self.ship_frames["images/Effects/fire03.png"]
                fire_rot = pygame.transform.rotate(engine_img, self.angle)
                fire_offset = pygame.math.Vector2(-35, 0).rotate(-self.angle)
                window.blit(fire_rot, fire_rot.get_rect(center=(self.pos.x - camera_x + fire_offset.x, self.pos.y - camera_y + fire_offset.y)))
            except KeyError: pass

        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.pos.x - camera_x, self.pos.y - camera_y))
        window.blit(rotated, rect.topleft)

class EnemyManager:
    def __init__(self, ship_frames, player_ref, music_obj, max_enemies, shoot_obj, world_radius=25000):
        self.music_obj = music_obj
        self.ship_frames = ship_frames
        self.player_ref = player_ref
        self.enemies = []
        self.max_enemies = max_enemies
        self.shoot_obj = shoot_obj
        self.world_radius = world_radius # Zapamiętujemy promień świata

    def update(self, dt):
        if len(self.enemies) < self.max_enemies and random.random() < 0.01:
            self.enemies.append(Enemy(self.ship_frames, self.player_ref, self.music_obj, self.shoot_obj, self))
        for enemy in self.enemies:
            enemy.update(dt)

    def draw(self, window, camera_x, camera_y):
        for enemy in self.enemies:
            enemy.draw(window, camera_x, camera_y)