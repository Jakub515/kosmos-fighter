import pygame

class SpaceShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path,cxx,cyy,player_pos):
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path

        self.actual_frame = pygame.transform.rotate(ship_frames[0],-90)

        self.cxx = cxx
        self.cyy = cyy

        self.player_pos = pygame.math.Vector2(player_pos[0],player_pos[1])

        self.angle = 90
        self.speed = 0

        self.max_speed = 25
        

    def update(self,key_up, key_down, key_right, key_left):
        if key_right:
            self.angle -= 0.5
        if key_left:
            self.angle += 0.5
        if key_up:
            if not self.speed > self.max_speed:
                self.speed += 0.1
        else:
            if self.speed > 0:
                self.speed -= 0.05
            #else:
            #    self.speed = 0
        if key_down:
            self.speed -= 0.05
            if self.speed < 0:
                self.speed = 0
        direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.player_pos += direction * self.speed
        return [self.player_pos.x, self.player_pos.y]

    def draw(self,window):
        window.blit(pygame.transform.rotate(self.actual_frame, self.angle),(self.cxx//2,self.cyy/2))