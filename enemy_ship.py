import pygame
import math
import random

class Enemy:
    def __init__(self, ship_frames, player_ref, spawn_radius=1000, behavior=None):
        self.ship_frames = ship_frames
        self.player_ref = player_ref

        # Typ zachowania: 0=agresywny, 1=neutralny, 2=patrol, 3=STACJONARNY (TESTOWY)
        if behavior is not None:
            self.base_behavior = behavior
        else:
            self.base_behavior = random.choice([0, 1, 2])
            
        self.behavior_type = self.base_behavior
        self.aggressive_timer = 0

        # Wygląd i statystyki
        enemy_types = [
            ("images/Enemies/enemyBlack1.png", 1, 1),
            ("images/Enemies/enemyBlack2.png", 1, 1),
            ("images/Enemies/enemyBlack3.png", 1, 1)
        ]
        self.texture_path, self.speed, self.hp = random.choice(enemy_types)
        self.image = pygame.transform.rotate(self.ship_frames[self.texture_path], -90)

        # Pozycja
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(spawn_radius * 0.8, spawn_radius)
        self.pos = pygame.math.Vector2(
            self.player_ref.player_pos.x + math.cos(angle) * distance,
            self.player_ref.player_pos.y + math.sin(angle) * distance
        )

        self.angle = 0
        self.shots = []
        self.weapon_timers = [0.0 for _ in range(5)]

        # --- STATYSTYKI PATROLOWANIA ---
        self.patrol_angle = random.uniform(0, 360)
        self.patrol_speed = random.uniform(30, 80)
        self.patrol_radius = random.uniform(250, 500)
        self.patrol_direction = random.choice([-1, 1])

        # Broń
        self.weapons = [
            [self.ship_frames["images/Lasers/laserRed01.png"], 40, 5, 0.6],
            [self.ship_frames["images/Lasers/laserRed02.png"], 50, 3, 0.5],
            [self.ship_frames["images/Lasers/laserRed03.png"], 60, 2, 0.4],
            [self.ship_frames["images/Lasers/laserRed04.png"], 70, 1, 0.3],
            [self.ship_frames["images/Lasers/laserRed05.png"], 80, 0.5, 0.2],
        ]
        self.laser_sound = pygame.mixer.Sound("images/audio/sfx_laser2.wav")
        self.laser_sound.set_volume(0.4)
        self.current_weapon = random.randint(0, len(self.weapons) - 1)

    def update(self, dt):
        # Statyczny cel (type 3) nie reaguje na alarmy i nie rusza się
        if self.behavior_type == 3:
            # Aktualizacja pocisków (jeśli by strzelał, ale tu tylko stoi)
            self._update_shots()
            return

        if self.aggressive_timer > 0:
            self.aggressive_timer -= dt
            if self.aggressive_timer <= 0:
                self.behavior_type = self.base_behavior

        for i in range(len(self.weapon_timers)):
            self.weapon_timers[i] += dt

        # Logika ruchu
        if self.behavior_type == 0:
            self._move_toward_player(dt)
            self._maybe_shoot(target_player=True)
        elif self.behavior_type == 1:
            move_dir = pygame.math.Vector2(math.cos(math.radians(self.angle)),
                                         math.sin(math.radians(self.angle)))
            self.pos += move_dir * self.speed * dt * 60
            if random.random() < 0.01:
                self.angle += random.uniform(-15, 15)
        elif self.behavior_type == 2:
            self._patrol_around_player(dt)

        self._update_shots()

    def _update_shots(self):
        for shot in self.shots:
            shot["pos"] += shot["vel"]
        # Usuwanie dalekich pocisków
        self.shots = [s for s in self.shots if (s["pos"] - self.pos).length_squared() < 4000000]

    def _move_toward_player(self, dt):
        direction = (self.player_ref.player_pos - self.pos)
        if direction.length() != 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt * 60
            self.angle = -math.degrees(math.atan2(direction.y, direction.x))

    def _patrol_around_player(self, dt):
        center = self.player_ref.player_pos
        self.patrol_angle += self.patrol_speed * self.patrol_direction * dt
        rad = math.radians(self.patrol_angle)
        self.pos.x = center.x + math.cos(rad) * self.patrol_radius
        self.pos.y = center.y + math.sin(rad) * self.patrol_radius
        if self.patrol_direction == 1:
            self.angle = -self.patrol_angle - 90
        else:
            self.angle = -self.patrol_angle + 90

    def _maybe_shoot(self, target_player=False):
        if random.random() < 0.02:
            self.shoot(target_player)

    def shoot(self, target_player=False):
        weapon = self.weapons[self.current_weapon]
        reload_time = weapon[3]
        if self.weapon_timers[self.current_weapon] >= reload_time:
            self.weapon_timers[self.current_weapon] = 0.0
            if target_player:
                direction = (self.player_ref.player_pos - self.pos)
                if direction.length() != 0:
                    direction = direction.normalize()
                shot_angle = -math.degrees(math.atan2(direction.y, direction.x))
            else:
                direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
                shot_angle = self.angle

            shot = {
                "pos": self.pos.copy(),
                "vel": direction * weapon[1],
                "img": weapon[0],
                "damage": weapon[2],
                "dir": shot_angle
            }
            self.shots.append(shot)
            self.laser_sound.play()

    def draw(self, window, camera_x, camera_y):
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.pos.x - camera_x, self.pos.y - camera_y))
        window.blit(rotated, rect.topleft)

        for shot in self.shots:
            sx = shot["pos"].x - camera_x
            sy = shot["pos"].y - camera_y
            window.blit(pygame.transform.rotate(shot["img"], shot["dir"] + 90), (sx, sy))


class EnemyManager:
    def __init__(self, ship_frames, player_ref, max_enemies=10):
        self.ship_frames = ship_frames
        self.player_ref = player_ref
        self.enemies = []
        self.max_enemies = max_enemies
        self.alarm_time = 0

    def spawn_test_targets(self, count=5):
        """Tworzy nieruchome statki blisko gracza do testów strzelania"""
        for _ in range(count):
            # behavior=3 oznacza, że się nie ruszają
            target = Enemy(self.ship_frames, self.player_ref, spawn_radius=400, behavior=3)
            # Ustawiamy im przodem do góry dla estetyki
            target.angle = 90
            self.enemies.append(target)

    def update(self, dt):
        # Nie spawnuj nowych wrogów, jeśli przekroczymy limit (wliczając testowe)
        if len(self.enemies) < self.max_enemies and random.random() < 0.01:
            self.enemies.append(Enemy(self.ship_frames, self.player_ref))

        player_p = self.player_ref.player_pos
        for enemy in self.enemies:
            # Tylko ruchomi przeciwnicy (nie typu 3) wyzwalają alarm
            if enemy.behavior_type != 3:
                dist_sq = (enemy.pos - player_p).length_squared()
                if dist_sq < 90000:
                    self.trigger_alarm(10.0)
                    break

        if self.alarm_time > 0:
            self.alarm_time -= dt

        for enemy in self.enemies:
            # Alarm nie wpływa na cele testowe
            if self.alarm_time > 0 and enemy.behavior_type != 3:
                enemy.behavior_type = 0
                enemy.aggressive_timer = self.alarm_time
            enemy.update(dt)

    def trigger_alarm(self, duration):
        if self.alarm_time < duration:
            self.alarm_time = duration
            for e in self.enemies:
                if e.behavior_type != 3: # Cele testowe ignorują alarm
                    e.behavior_type = 0
                    e.aggressive_timer = duration

    def draw(self, window, camera_x, camera_y):
        for enemy in self.enemies:
            enemy.draw(window, camera_x, camera_y)