import pygame

class Shoot():
    def __init__(self):
        self.shots = []

    def create_missle(self, data):
        self.shots.append(data)

    def update(self):
        for shot in self.shots:
            shot["pos"] += shot["vel"]
        if len(self.shots) > 50: self.shots.pop(0)        

    def draw(self, window, offset_x, offset_y):
        for shot in self.shots:
            s_x = shot["pos"].x - offset_x
            s_y = shot["pos"].y - offset_y
            rotated_laser = pygame.transform.rotate(shot["img"], shot["dir"] + 90)
            laser_rect = rotated_laser.get_rect(center=(int(s_x), int(s_y)))
            window.blit(rotated_laser, laser_rect)