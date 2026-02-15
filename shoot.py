import pygame

class Shoot():
    def __init__(self):
        self.shots = []
        """self.explosion_frames = [
            self.ship_frames["images/dym/tile_00.png"],
            self.ship_frames["images/dym/tile_01.png"],
            self.ship_frames["images/dym/tile_02.png"],
            self.ship_frames["images/dym/tile_03.png"],
            self.ship_frames["images/dym/tile_04.png"],
            self.ship_frames["images/dym/tile_05.png"],
            self.ship_frames["images/dym/tile_06.png"],
            self.ship_frames["images/dym/tile_07.png"],
            self.ship_frames["images/dym/tile_08.png"],
            self.ship_frames["images/dym/tile_09.png"],
            self.ship_frames["images/dym/tile_10.png"],
            self.ship_frames["images/dym/tile_11.png"],
            self.ship_frames["images/dym/tile_12.png"],
            self.ship_frames["images/dym/tile_13.png"],
            self.ship_frames["images/dym/tile_14.png"],
            self.ship_frames["images/dym/tile_15.png"]
        ]"""

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
