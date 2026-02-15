import pygame

class Radar:
    def __init__(self, screen_width, screen_height, radar_size=200, world_radius=10000, zoom_radius=4000):
        self.size = radar_size
        self.world_radius = world_radius
        
        # Marginesy
        self.margin = 20
        self.pos_x = screen_width - self.size - self.margin
        self.pos_y = screen_height - self.size - self.margin
        
        # Główna powierzchnia radaru
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Powierzchnia maski (białe kółko, które wycina kształt)
        self.mask_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.mask_surface, (255, 255, 255, 255), (self.size // 2, self.size // 2), self.size // 2)

        # Skalowanie: zoom_radius to obszar świata widoczny na radarze
        self.zoom_radius = zoom_radius 
        self.scale = self.size / (self.zoom_radius * 2)

    def draw(self, window, player, enemy_manager):
        # 1. Przygotowujemy czystą, przezroczystą warstwę roboczą
        temp_radar = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Środek radaru na jego własnej powierzchni
        center = pygame.math.Vector2(self.size // 2, self.size // 2)
        
        # Tło radaru (półprzezroczyste czarne koło)
        pygame.draw.circle(temp_radar, (0, 0, 0, 150), (int(center.x), int(center.y)), self.size // 2)
        
        # --- RYSOWANIE GRANICY ŚWIATA ---
        # Wektor od gracza do środka świata (0,0)
        rel_world_center = pygame.math.Vector2(0, 0) - player.player_pos
        # Pozycja środka świata na powierzchni radaru
        world_center_radar = center + rel_world_center * self.scale
        world_radar_radius = self.world_radius * self.scale
        
        # Rysujemy czerwoną linię granicy świata (naprawione zmienne .x i .y)
        pygame.draw.circle(temp_radar, (255, 50, 50, 200), 
                           (int(world_center_radar.x), int(world_center_radar.y)), 
                           int(world_radar_radius), 3)

        # --- RYSOWANIE WROGÓW ---
        for enemy in enemy_manager.enemies:
            rel_pos = enemy.pos - player.player_pos
            if rel_pos.length() < self.zoom_radius:
                radar_pos = center + rel_pos * self.scale
                pygame.draw.circle(temp_radar, (255, 50, 50), (int(radar_pos.x), int(radar_pos.y)), 3)

        # --- RYSOWANIE GRACZA (zawsze na środku) ---
        pygame.draw.circle(temp_radar, (50, 255, 50), (int(center.x), int(center.y)), 4)
        
        # Kierunek patrzenia gracza
        direction_vec = pygame.math.Vector2(7, 0).rotate(-player.angle)
        pygame.draw.line(temp_radar, (255, 255, 255), 
                         (int(center.x), int(center.y)), 
                         (int(center.x + direction_vec.x), int(center.y + direction_vec.y)), 1)

        # --- MASKOWANIE (WYCINANIE KOŁA) ---
        # Usuwa wszystko, co wystaje poza okrągły kształt radaru
        temp_radar.blit(self.mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # --- RYSOWANIE OBWÓDKI ---
        # Rysujemy ją na głównym oknie (window), żeby nie została przycięta
        pygame.draw.circle(window, (200, 200, 200), 
                           (int(self.pos_x + center.x), int(self.pos_y + center.y)), 
                           self.size // 2, 2)

        # Nakładamy gotowy, przycięty radar na ekran
        window.blit(temp_radar, (self.pos_x, self.pos_y))