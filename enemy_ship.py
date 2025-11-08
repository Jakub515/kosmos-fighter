import pygame
import math, random, time

class Enemy:
    def __init__(self, ship_frames, player_ref, spawn_radius=1000):
        self.ship_frames = ship_frames
        self.player_ref = player_ref

        # Typ zachowania: 0 = agresywny, 1 = neutralny, 2 = patrolujący
        self.base_behavior = random.choice([0, 1, 2])
        self.behavior_type = self.base_behavior  # aktualny tryb (może się zmieniać)
        self.aggressive_timer = 0  # ile sekund pozostało trybu agresywnego

        # Wygląd i statystyki
        enemy_types = [
            ("images/Enemies/enemyBlack1.png", 8, 60),
            ("images/Enemies/enemyBlack2.png", 5, 100),
            ("images/Enemies/enemyBlack3.png", 6, 80)
        ]
        self.texture_path, self.speed, self.hp = random.choice(enemy_types)
        self.image = pygame.transform.rotate(self.ship_frames[self.texture_path], -90)

        # Losowa pozycja wokół gracza
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(spawn_radius * 0.8, spawn_radius)
        self.pos = pygame.math.Vector2(
            self.player_ref.player_pos.x + math.cos(angle) * distance,
            self.player_ref.player_pos.y + math.sin(angle) * distance
        )

        self.angle = 0
        self.shots = []
        self.weapon_timers = [0.0 for _ in range(5)]

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

        # Do patrolowania
        self.patrol_angle = random.uniform(0, 360)
        self.patrol_speed = random.uniform(0.5, 1.5)

    def update(self, dt):
        # Jeśli aktywny tryb agresji (czasowy)
        if self.aggressive_timer > 0:
            self.aggressive_timer -= dt
            if self.aggressive_timer <= 0:
                self.behavior_type = self.base_behavior  # wraca do oryginalnego stylu

        # Aktualizacja timerów broni
        for i in range(len(self.weapon_timers)):
            self.weapon_timers[i] += dt

        # --- Zachowanie zależne od trybu ---
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

        # Aktualizacja pocisków
        for shot in self.shots:
            shot["pos"] += shot["vel"]

    def _move_toward_player(self, dt):
        direction = (self.player_ref.player_pos - self.pos)
        if direction.length() != 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt * 60
            dx, dy = direction.x, direction.y
            self.angle = -math.degrees(math.atan2(dy, dx))

    def _patrol_around_player(self, dt):
        # Krążenie wokół gracza
        center = self.player_ref.player_pos
        self.patrol_angle += self.patrol_speed * dt * 60
        radius = 400
        self.pos.x = center.x + math.cos(math.radians(self.patrol_angle)) * radius
        self.pos.y = center.y + math.sin(math.radians(self.patrol_angle)) * radius
        self.angle = -self.patrol_angle

    def _maybe_shoot(self, target_player=False):
        if random.random() < 0.02:  # losowa decyzja o strzale
            self.shoot(target_player)

    def shoot(self, target_player=False):
        weapon = self.weapons[self.current_weapon]
        reload_time = weapon[3]

        if self.weapon_timers[self.current_weapon] >= reload_time:
            self.weapon_timers[self.current_weapon] = 0.0

            # Kierunek pocisku
            if target_player:
                direction = (self.player_ref.player_pos - self.pos)
                if direction.length() != 0:
                    direction = direction.normalize()
                angle = -math.degrees(math.atan2(direction.y, direction.x))
            else:
                direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
                angle = self.angle

            shot = {
                "pos": self.pos.copy(),
                "vel": direction * weapon[1],
                "img": weapon[0],
                "damage": weapon[2],
                "dir": angle
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
        self.alarm_time = 0  # czas trwania alarmu (globalny dla wszystkich)

    def update(self, dt):
        # Generowanie nowych wrogów
        if len(self.enemies) < self.max_enemies and random.random() < 0.01:
            self.enemies.append(Enemy(self.ship_frames, self.player_ref))

        # Sprawdzenie dystansu gracza do wrogów — uruchamia alarm
        for enemy in self.enemies:
            distance = (enemy.pos - self.player_ref.player_pos).length()
            if distance < 300:  # jeśli gracz podejdzie zbyt blisko
                self.trigger_alarm(10.0)  # wszyscy agresywni przez 10 sekund
                break

        # Aktualizacja czasu alarmu
        if self.alarm_time > 0:
            self.alarm_time -= dt

        # Aktualizacja wszystkich wrogów
        for enemy in self.enemies:
            # Jeśli alarm aktywny, wymusza agresję
            if self.alarm_time > 0:
                enemy.behavior_type = 0
                enemy.aggressive_timer = self.alarm_time
            enemy.update(dt)

    def trigger_alarm(self, duration):
        self.alarm_time = duration
        for e in self.enemies:
            e.behavior_type = 0
            e.aggressive_timer = duration

    def draw(self, window, camera_x, camera_y):
        for enemy in self.enemies:
            enemy.draw(window, camera_x, camera_y)
