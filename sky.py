import pygame
import random

class SpaceBackground:
    def __init__(self, width, height, screen_width, screen_height, num_stars=200):
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Powierzchnia tła
        self.surface = pygame.Surface((width, height))
        
        # Losowe tło (czarne z lekkim niebieskim odcieniem)
        base_color = (0, 0, random.randint(10, 30))
        self.surface.fill(base_color)
        
        # Tworzymy gwiazdki
        for _ in range(num_stars):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            size = random.choice([1, 2, 3])
            color = random.choice([(255,255,255),(255,255,200)])
            pygame.draw.rect(self.surface, color, (x, y, size, size))
    
    def draw(self, screen, player_pos):
        px, py = player_pos
        offset_x = int(px - self.screen_width / 2)
        offset_y = int(py - self.screen_height / 2)
        
        # Zapobiegamy wychodzeniu poza granice tła
        offset_x = max(0, min(offset_x, self.width - self.screen_width))
        offset_y = max(0, min(offset_y, self.height - self.screen_height))
        
        # Rysujemy fragment tła na ekranie
        screen.blit(self.surface, (0, 0), (offset_x, offset_y, self.screen_width, self.screen_height))