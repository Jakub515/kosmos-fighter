import pygame
import os

class MusicManager():
    def __init__(self, audio_files):
        self.audio_files = audio_files
        pygame.mixer.init()
        pygame.mixer.set_num_channels(1024)
        if os.path.exists("images/audio/star_wars.mp3"):
            pygame.mixer.music.load("images/audio/star_wars.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

    def play(self, path, volume):
        if path in self.audio_files:
            temp_music = pygame.mixer.Sound(path)
            temp_music.set_volume(volume)
            temp_music.play()

    def at_exit(self):
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()