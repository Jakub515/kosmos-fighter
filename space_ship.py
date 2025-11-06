import pygame

class SpaceShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path, cxx, cyy, player_pos):
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path
        
        self.actual_frame = pygame.transform.rotate(self.ship_frames["images/space_ships/playerShip1_blue.png"], -90)
        self.cxx = cxx
        self.cyy = cyy

        self.player_pos = pygame.math.Vector2(player_pos[0], player_pos[1])
        self.angle = 90
        self.speed = 0
        self.max_speed = 25

        # 🔧 przesunięcie środka obrotu (np. 20 px w dół)
        self.pivot_offset = pygame.Vector2(0, 0)

        self.weapons = [
            # Wgrane obrazki                  prędkość px/pętla, siła rażenia
            [self.ship_frames["images/Lasers/laserBlue12.png"], 30, 5],
            [self.ship_frames["images/Lasers/laserBlue13.png"], 35, 4],
            [self.ship_frames["images/Lasers/laserBlue14.png"], 40, 3],
            [self.ship_frames["images/Lasers/laserBlue15.png"], 45, 2],
            [self.ship_frames["images/Lasers/laserBlue16.png"], 50, 1]
        ]
        self.shots = []
        self.current_weapon = 0

    def update(self, key_up, key_down, key_right, key_left, space, mouse_x, mouse_y, numbers):
        for index, i in enumerate(numbers):
            if i:
                self.current_weapon = index

        if key_right:
            self.angle -= 1.5
        if key_left:
            self.angle += 1.5
        if key_up:
            if not self.speed > self.max_speed:
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

        direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.player_pos += direction * self.speed

        if space:
            mouse_pos = pygame.math.Vector2([mouse_x,mouse_y])
            direction = (mouse_pos - self.player_pos).normalize()
            data = self.weapons[self.current_weapon]
            self.shots.append([self.player_pos.copy(),mouse_pos,direction,data])

        return [self.player_pos.x, self.player_pos.y]

    def draw(self, window):
        # Obrót obrazka
        rotated_image = pygame.transform.rotozoom(self.actual_frame, self.angle, 1)

        # Obracamy przesunięcie pivotu
        offset_rotated = self.pivot_offset.rotate(self.angle)

        # Rysujemy NA ŚRODKU EKRANU (tak jak miałeś wcześniej), ale z poprawką pivotu
        center = pygame.Vector2(self.cxx // 2, self.cyy // 2) + offset_rotated

        rect = rotated_image.get_rect(center=center)

        for shot in self.shots:
            shot[0]+=

        window.blit(rotated_image, (rect.x-175,rect.y-100))
