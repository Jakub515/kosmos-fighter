import pygame
import os
from collections import defaultdict

class ImageLoad:
    def __init__(self):
        pass            

    def get_image(self, name: str, scale: int | float | list | tuple):
        try:
            image = pygame.image.load(name)
        except pygame.error as e:
            print(f"Nie można załadować obrazu {name}: {e}")
            return None

        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()

        # Tworzymy roboczą zmienną, którą na pewno wypełnimy liczbą
        final_scale_value: float = 0.0

        # Skalowanie
        if isinstance(scale, (list, tuple)):
            if len(scale) == 2:
                # Jeśli podano [szerokość, wysokość], skalujemy i kończymy funkcję
                width, height = scale
                return pygame.transform.scale(image, (width, height))
            elif len(scale) == 1:
                # Jeśli podano [procent], wyciągamy go
                final_scale_value = float(scale[0])
            else:
                final_scale_value = 100.0 # Wartość domyślna
        else:
            # Jeśli scale od początku było int lub float
            final_scale_value = float(scale)
        
        # Teraz używamy zmiennej, która na 100% jest floatem
        percent = final_scale_value / 100
        width = int(image.get_width() * percent)
        height = int(image.get_height() * percent)
        return pygame.transform.scale(image, (width, height))

    def load_all_assets(self, base_folder_name="images"):
        """
        Skanuje folder i ładuje zasoby. 
        Zwraca: (dict_gfx_40, dict_gfx_100, list_audio)
        """
        base_folder = os.path.join(os.getcwd(), base_folder_name)
        files_by_ext = defaultdict(list)

        if os.path.exists(base_folder):
            for root, _, files in os.walk(base_folder):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    rel_path = os.path.relpath(os.path.join(root, file), os.getcwd()).replace("\\", "/")
                    files_by_ext[ext].append(rel_path)

        # Pobieranie ścieżek
        image_paths = sorted(files_by_ext.get(".png", []))
        audio_paths = sorted(files_by_ext.get(".wav", []))

        # Ładowanie grafik w dwóch skalach (tak jak miałeś w main)
        gfx_40 = {path: self.get_image(path, 40) for path in image_paths}
        gfx_100 = {path: self.get_image(path, 100) for path in image_paths}

        return gfx_40, gfx_100, audio_paths