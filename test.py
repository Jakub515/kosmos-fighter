import pygame

pygame.display.init()
driver = pygame.display.get_driver()
print(f"Używany sterownik wideo: {driver}")

# Lista wszystkich dostępnych sterowników w systemie
# (Wymaga pygame-ce w nowszej wersji)
try:
    print(f"Dostępne sterowniki: {pygame.display.get_desktop_sizes()}")
except:
    print("Nie można pobrać informacji o ekranie.")