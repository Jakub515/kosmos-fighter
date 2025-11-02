import pygame

class SpaceShip():
    def __init__(self, ship_frames, ship_parts, ship_audio_path,cxx,cyy):
        self.ship_frames = ship_frames
        self.ship_parts = ship_parts
        self.ship_audio_path = ship_audio_path

        self.actual_frame = ship_frames[0]

        self.cxx = cxx
        self.cyy = cyy

    def update(self):
        pass
    def draw(self,window):
        window.blit(self.actual_frame,(self.cxx//2,self.cyy/2))