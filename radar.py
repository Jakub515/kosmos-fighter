import pygame

class Radar:
    def __init__(self, screen_width, screen_height, radar_size=200, world_radius=10000, zoom_radius=4000):
        self.size = radar_size
        self.world_radius = world_radius
        
        # Kolory
        self.border_color = (70, 70, 70)      # Szary kolor obramowania
        self.bg_color = (0, 0, 0, 150)        # Półprzezroczyste czarne tło
        self.player_color = (50, 255, 50)     # Zielony punkt gracza
        self.enemy_color = (255, 50, 50)      # Czerwone punkty wrogów
        
        # Marginesy i pozycja (Prawy dolny róg)
        self.margin = 20
        self.pos_x = screen_width - self.size - self.margin
        self.pos_y = screen_height - self.size - self.margin
        
        # Powierzchnia maski do przycinania wystających elementów (np. linii świata)
        self.mask_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.mask_surface, (255, 255, 255, 255), (self.size // 2, self.size // 2), self.size // 2)

        # Skalowanie jednostek świata na piksele radaru
        self.zoom_radius = zoom_radius 
        self.scale = self.size / (self.zoom_radius * 2)

        # --- PARAMETRY ANIMACJI (Rzadsze pulsowanie) ---
        self.pulse_timer = 0.0      # Wspólny licznik czasu dla wszystkich fal
        self.pulse_speed = 0.35     # Prędkość rozchodzenia się (mniejsza = wolniej)
        self.num_circles = 2        # Liczba fal widocznych jednocześnie (rzadziej niż 3)

    def draw(self, window, player, enemy_manager, dt):
        # 1. Tworzymy czystą powierzchnię z kanałem Alpha (przezroczystość)
        temp_radar = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        temp_radar.fill((0, 0, 0, 0))
        
        center = pygame.math.Vector2(self.size // 2, self.size // 2)
        
        # 2. Rysujemy tło radaru (koło)
        pygame.draw.circle(temp_radar, self.bg_color, (int(center.x), int(center.y)), self.size // 2)
        
        # --- LOGIKA PULSOWANIA ---
        self.pulse_timer += self.pulse_speed * dt
        if self.pulse_timer > 1.0:
            self.pulse_timer -= 1.0  # Płynny reset cyklu
            
        for i in range(self.num_circles):
            # Obliczamy przesunięcie dla każdego kółka, aby były w równych odstępach
            offset = i / self.num_circles
            progress = (self.pulse_timer + offset) % 1.0
            
            # Promień rośnie od 0 do połowy rozmiaru radaru
            current_radius = progress * (self.size // 2)
            
            # Zanikanie: Im dalej od środka, tym bardziej przezroczyste (Alpha od 160 do 0)
            alpha = int(160 * (1.0 - progress))
            
            # Rysujemy okrąg fali
            pygame.draw.circle(temp_radar, (60, 220, 60, alpha), 
                               (int(center.x), int(center.y)), 
                               int(current_radius), 1)

        # --- GRANICA ŚWIATA (Czerwony okrąg pokazujący limit mapy) ---
        rel_world_center = pygame.math.Vector2(0, 0) - player.player_pos
        world_center_radar = center + rel_world_center * self.scale
        world_radar_radius = self.world_radius * self.scale
        
        # Rysujemy tylko jeśli granica jest w zasięgu widoczności radaru (z małym marginesem)
        pygame.draw.circle(temp_radar, (255, 50, 50, 180), 
                           (int(world_center_radar.x), int(world_center_radar.y)), 
                           int(world_radar_radius), 2)

        # --- WROGOWIE ---
        for enemy in enemy_manager.enemies:
            rel_pos = enemy.pos - player.player_pos
            # Rysujemy wrogów tylko w zasięgu zoom_radius
            if rel_pos.length() < self.zoom_radius:
                radar_pos = center + rel_pos * self.scale
                pygame.draw.circle(temp_radar, self.enemy_color, (int(radar_pos.x), int(radar_pos.y)), 3)

        # --- GRACZ I JEGO KIERUNEK ---
        # Linia kierunku (np. przód statku/postaci)
        direction_vec = pygame.math.Vector2(8, 0).rotate(-player.angle)
        pygame.draw.line(temp_radar, (255, 255, 255), 
                         (int(center.x), int(center.y)), 
                         (int(center.x + direction_vec.x), int(center.y + direction_vec.y)), 2)

        # Kropka gracza w samym centrum radaru
        pygame.draw.circle(temp_radar, self.player_color, (int(center.x), int(center.y)), 4)

        # --- MASKOWANIE I FINALIZACJA ---
        # Przycinamy wszystko, co wyszło poza obrys koła (np. fragmenty granicy świata)
        temp_radar.blit(self.mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Nakładamy gotowy radar na główne okno gry
        window.blit(temp_radar, (self.pos_x, self.pos_y))
        
        # Rysujemy stałą obwódkę zewnętrzną
        pygame.draw.circle(window, self.border_color, 
                           (int(self.pos_x + center.x), int(self.pos_y + center.y)), 
                           self.size // 2, 2)