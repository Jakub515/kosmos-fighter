import pygame
import math
import time

class Shoot():
    def __init__(self, images: dict):
        self.images = images
        self.shots = []
        # Ładowanie klatek eksplozji
        self.explosion_frames = [
            self.images[f"images/dym/Explosion/tile_{str(i).zfill(2)}.png"] for i in range(16)
        ]

    def create_missle(self, data: dict):
        # Dodajemy czas powstania i początkowy indeks klatki animacji
        data["spawn_time"] = time.time()
        data["is_exploding"] = False
        data["frame_index"] = 0
        self.shots.append(data)

    def update(self):
        current_time = time.time()
        
        for shot in self.shots[:]:  # Iterujemy po kopii listy, aby móc usuwać elementy
            # 1. Sprawdzenie czasu życia (2 sekunda do wybuchu)
            if (not shot["is_exploding"] and current_time - shot["spawn_time"] > 2):
                if shot.get("rocket"):
                    shot["is_exploding"] = True
                else:
                    self.shots.remove(shot)
                    continue

            # 2. Fizyka pocisku
            if not shot["is_exploding"]:
                if shot.get("rocket"):
                    # Przyspieszanie: dodajemy wektor kierunku pomnożony przez siłę ciągu
                    # Zakładamy, że shot["dir"] to kąt w stopniach
                    rad = math.radians(shot["dir"])
                    acceleration = 1  # Siła przyspieszenia pocisku
                    shot["vel"].x += math.cos(rad) * acceleration
                    shot["vel"].y -= math.sin(rad) * acceleration
                
                shot["pos"] += shot["vel"]
            else:
                # 3. Logika animacji eksplozji
                shot["frame_index"] += 0.5  # Szybkość animacji dymu
                if shot["frame_index"] >= len(self.explosion_frames):
                    self.shots.remove(shot)

        # Ograniczenie liczby pocisków
        if len(self.shots) > 150:
            self.shots.pop(0)

    def draw(self, window: pygame.Surface, offset_x: float, offset_y: float):
        for shot in self.shots:
            s_x = shot["pos"].x - offset_x
            s_y = shot["pos"].y - offset_y
            
            if not shot["is_exploding"]:
                # Rysowanie lecącego pocisku
                rotated_laser = pygame.transform.rotate(shot["img"], shot["dir"] + 90)
                laser_rect = rotated_laser.get_rect(center=(int(s_x), int(s_y)))
                window.blit(rotated_laser, laser_rect)
            else:
                # Rysowanie klatki eksplozji
                frame = self.explosion_frames[int(shot["frame_index"])]
                rect = frame.get_rect(center=(int(s_x), int(s_y)))
                window.blit(frame, rect)