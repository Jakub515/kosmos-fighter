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

    def update(self, key_up, key_down, key_right, key_left):
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
        return [self.player_pos.x, self.player_pos.y]

    def draw(self, window):
        # Obrót obrazka
        rotated_image = pygame.transform.rotozoom(self.actual_frame, self.angle, 1)

        # Obracamy przesunięcie pivotu
        offset_rotated = self.pivot_offset.rotate(self.angle)

        # Rysujemy NA ŚRODKU EKRANU (tak jak miałeś wcześniej), ale z poprawką pivotu
        center = pygame.Vector2(self.cxx // 2, self.cyy // 2) + offset_rotated

        rect = rotated_image.get_rect(center=center)
        window.blit(rotated_image, (rect.x-175,rect.y-100))
