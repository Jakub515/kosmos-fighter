import pygame
import os

pygame.init()

class ImageLoad:
    def __init__(self):
        pass            

    def get_image(self, name, scale):
        image = pygame.image.load(name)
        # Sprawdzanie, czy obrazek ma kanał alfa i konwersja
        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()
        ret = None
        if not image:
            ret = None
        elif isinstance(scale, (list, tuple)):
            if len(scale) == 2:
                width, height = scale
                ret = pygame.transform.scale(image, (width, height))
            elif len(scale) == 1:
                percent = scale[0] / 100
                width = int(image.get_width() * percent)
                height = int(image.get_height() * percent)
                ret = pygame.transform.scale(image, (width, height))
        elif isinstance(scale, (int, float)):
            percent = scale / 100
            width = int(image.get_width() * percent)
            height = int(image.get_height() * percent)
            ret = pygame.transform.scale(image, (width, height))
        
        return ret
        