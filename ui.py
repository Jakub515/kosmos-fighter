import pygame

class GameController:
    def __init__(self, event_obj, player, cxx, cyy, loaded_images):
        # Inicjalizujemy UI
        self.ui = UI(event_obj, cxx, cyy, loaded_images)
        
        # Inicjalizujemy InputHandler i przekazujemy mu obiekt UI
        self.input_handler = InputHandler(event_obj, player, self.ui)

    def update(self, dt):
        self.input_handler.update()
        self.ui.update()

    def draw(self, window):
        self.ui.draw(window)

class InputHandler():
    def __init__(self, event_obj, player_obj, ui_obj):
        self.event_obj = event_obj
        self.player_obj = player_obj
        self.ctrl_pressed_last_frame = False
        self.ui_obj = ui_obj
    
    def update(self):
        # --- RUCH ---
        # Thrust i Boost
        is_boosting = self.event_obj.backquote
        self.player_obj.thrust(self.event_obj.key_up, boost=is_boosting)

        # Rotacja
        if self.event_obj.key_left:
            self.player_obj.rotate(1)
        elif self.event_obj.key_right:
            self.player_obj.rotate(-1)
        else:
            self.player_obj.rotate(0)

        # Hamowanie
        self.player_obj.brake(self.event_obj.key_down)

        # --- WALKA ---
        # Strzelanie
        self.player_obj.fire(self.event_obj.key_space)

        # Tarcza
        if self.event_obj.key_s:
            self.player_obj.activate_shield()

        # Przełączanie zestawów broni (Toggle CTRL)
        if self.event_obj.key_ctrl_left and not self.ctrl_pressed_last_frame:
            self.player_obj.switch_weapon_set()
            self.ui_obj.change_weapon_type_ctr()
        self.ctrl_pressed_last_frame = self.event_obj.key_ctrl_left

        # Wybór konkretnej broni (Klawisze 1-9)
        keys_numbers = [
            self.event_obj.key_1, self.event_obj.key_2, self.event_obj.key_3,
            self.event_obj.key_4, self.event_obj.key_5, self.event_obj.key_6,
            self.event_obj.key_7, self.event_obj.key_8, self.event_obj.key_9
        ]
        
        for i, pressed in enumerate(keys_numbers):
            if pressed:
                self.ui_obj.change_weapon_type_num(i)
                self.player_obj.select_weapon(i)
                break
import pygame

class UI:
    def __init__(self, event_obj, screen_width, screen_height, images):
        self.event_obj = event_obj
        self.cxx = screen_width
        self.cyy = screen_height
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

        # Inicjalizacja list broni z obrazkami i parametrami
        # Zakładamy, że images to słownik z załadowanymi Surface'ami
        self.weapons = self.setup_weapons_1(images)
        self.weapons_2 = self.setup_weapons_2(images)

        self.active_set = 1
        self.current_weapon = 0
        
        # --- PARAMETRY GRAFICZNE ---
        self.slot_size = 55       # Rozmiar kwadratowego slotu
        self.spacing = 8          # Odstęp między slotami
        self.y_pos = 25           # Pozycja paska od góry ekranu
        
        # --- LOGIKA ANIMACJI ---
        self.frame_x = 0          # Bieżąca pozycja ramki (wyliczana w update)
        self.target_x = 0         # Docelowa pozycja ramki
        self.lerp_speed = 0.15    # Prędkość podążania ramki (0.1 - 1.0)

    def setup_weapons_1(self, images):
        """Zestaw Laserów"""
        return [
            [images["images/Lasers/laserBlue12.png"], 60, 5, 0.1],
            [images["images/Lasers/laserBlue13.png"], 65, 4, 0.4],
            [images["images/Lasers/laserBlue14.png"], 70, 3, 0.3],
            [images["images/Lasers/laserBlue15.png"], 75, 2, 0.2],
            [images["images/Lasers/laserBlue16.png"], 80, 1, 0.1]
        ]

    def setup_weapons_2(self, images):
        """Zestaw Rakiet"""
        paths = ["001", "004", "007", "010", "013", "016", "019", "022", "025"]
        return [[images[f"images/Missiles/spaceMissiles_{p}.png"], 40, 5, 3] for p in paths]

    def change_weapon_type_ctr(self):
        """Przełączanie między laserami a rakietami (CTRL)"""
        self.active_set = 2 if self.active_set == 1 else 1
        self.current_weapon = 0

    def change_weapon_type_num(self, index):
        """Wybór konkretnej broni z zestawu (1-9)"""
        current_list = self.weapons if self.active_set == 1 else self.weapons_2
        if index < len(current_list):
            self.current_weapon = index

    def draw_proportional_icon(self, window, icon, rect):
        """
        Rysuje ikonę wewnątrz rect, powiększając ją maksymalnie 
        przy zachowaniu oryginalnych proporcji.
        """
        img_w = icon.get_width()
        img_h = icon.get_height()
        
        # Margines wewnątrz slotu (np. 10 pikseli luzu)
        padding = 10
        max_dim = self.slot_size - padding
        
        # Obliczanie skali (wybieramy mniejszą, aby nic nie wystawało)
        scale = min(max_dim / img_w, max_dim / img_h)
        
        new_size = (int(img_w * scale), int(img_h * scale))
        # smoothscale daje ładniejsze krawędzie dla ikon UI
        scaled_icon = pygame.transform.smoothscale(icon, new_size)
        
        # Centrowanie ikony wewnątrz przekazanego prostokąta slotu
        icon_rect = scaled_icon.get_rect(center=rect.center)
        window.blit(scaled_icon, icon_rect)

    def update(self):
        """Przeliczanie pozycji animowanej ramki"""
        current_list = self.weapons if self.active_set == 1 else self.weapons_2
        
        # Obliczanie całkowitej szerokości paska dla centrowania
        total_w = len(current_list) * (self.slot_size + self.spacing) - self.spacing
        start_x = (self.cxx - total_w) // 2
        
        # Gdzie ramka POWINNA być
        self.target_x = start_x + self.current_weapon * (self.slot_size + self.spacing)
        
        # Płynne przesuwanie ramki do celu (Lerp)
        # Jeśli ramka jest daleko od startu (np. przy zmianie zestawu), teleportujemy ją bliżej
        if abs(self.target_x - self.frame_x) > 400:
            self.frame_x = self.target_x
            
        self.frame_x += (self.target_x - self.frame_x) * self.lerp_speed

    def draw(self, window):
        """Rysowanie całego interfejsu wyboru broni"""
        current_list = self.weapons if self.active_set == 1 else self.weapons_2
        total_w = len(current_list) * (self.slot_size + self.spacing) - self.spacing
        start_x = (self.cxx - total_w) // 2

        # 1. Rysowanie slotów i ikon
        for i, weapon_data in enumerate(current_list):
            icon = weapon_data[0]
            x = start_x + i * (self.slot_size + self.spacing)
            slot_rect = pygame.Rect(x, self.y_pos, self.slot_size, self.slot_size)
            
            # Tło slotu (półprzezroczysty ciemny prostokąt)
            s = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
            pygame.draw.rect(s, (20, 20, 30, 180), (0, 0, self.slot_size, self.slot_size), border_radius=5)
            window.blit(s, (x, self.y_pos))
            
            # Obramowanie slotu
            pygame.draw.rect(window, (80, 80, 100), slot_rect, 1, border_radius=5)

            # Rysowanie ikony z zachowaniem proporcji
            self.draw_proportional_icon(window, icon, slot_rect)

            # Numeracja klawiszy (1, 2, 3...)
            key_label = self.font.render(str(i + 1), True, (200, 200, 200))
            window.blit(key_label, (x + 5, self.y_pos + 2))

        # 2. Rysowanie animowanej ramki wyboru (na wierzchu)
        # Ramka jest nieco większa od slotu dla efektu "podświetlenia"
        glow_rect = pygame.Rect(self.frame_x - 2, self.y_pos - 2, self.slot_size + 4, self.slot_size + 4)
        pygame.draw.rect(window, (0, 200, 255), glow_rect, 3, border_radius=6)
        
        # Dodatkowy napis pod paskiem
        mode_name = "SYSTEM LASEROWY" if self.active_set == 1 else "WYRZUTNIA RAKIET"
        mode_txt = self.font.render(mode_name, True, (0, 255, 255))
        window.blit(mode_txt, (self.cxx // 2 - mode_txt.get_width() // 2, self.y_pos + self.slot_size + 5))