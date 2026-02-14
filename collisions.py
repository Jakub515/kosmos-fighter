import pygame
import math

class Collision():
    def __init__(self, mixer_obj):
        self.music_obj = mixer_obj
        
    def get_masked_data(self, image, pos, angle):
        """
        Pomocnicza funkcja dla kolizji pixel-perfect (używana tylko dla zderzeń statek-statek).
        """
        rotated_image = pygame.transform.rotate(image, angle)
        rect = rotated_image.get_rect(center=(pos.x, pos.y))
        mask = pygame.mask.from_surface(rotated_image)
        return rect, mask

    def check_mask_collision(self, obj1_img, obj1_pos, obj1_angle, obj2_img, obj2_pos, obj2_angle):
        """
        Sprawdza kolizję pixel-perfect między dwoma dużymi obiektami (statkami).
        """
        rect1, mask1 = self.get_masked_data(obj1_img, obj1_pos, obj1_angle)
        rect2, mask2 = self.get_masked_data(obj2_img, obj2_pos, obj2_angle)

        offset_x = rect2.left - rect1.left
        offset_y = rect2.top - rect1.top

        return mask1.overlap(mask2, (offset_x, offset_y))

    def check_collisions(self, player, enemy_manager):
        """
        Główna funkcja sprawdzająca wszystkie typy kolizji.
        """
        
        # 1. KOLIZJA: POCISKI GRACZA -> PRZECIWNICY
        # Używamy kopii list [:] aby bezpiecznie usuwać obiekty podczas pętli
        for shot in player.shots[:]:
            shot_hit = False
            for enemy in enemy_manager.enemies[:]:
                # Obliczamy dystans (kwadrat dystansu jest szybszy bo nie wymaga pierwiastkowania)
                dist_sq = (shot["pos"] - enemy.pos).length_squared()
                
                # --- POPRAWKA ---
                # Zamiast maski, używamy hojnego promienia kolizji.
                # Jeśli statek wroga ma ok. 80-100px szerokości, to promień ~50-60px jest idealny.
                # Dystans 60px ^ 2 = 3600.
                HIT_RADIUS_SQ = 60**2 

                if dist_sq < HIT_RADIUS_SQ:
                    # TRAFIENIE! (Bez sprawdzania masek dla laserów - są zbyt szybkie)
                    enemy.hp -= shot["damage"]
                    shot_hit = True
                    
                    if enemy.hp <= 0:
                        if enemy in enemy_manager.enemies:
                            enemy_manager.enemies.remove(enemy)
                    
                    # Przerywamy pętlę wrogów, bo pocisk trafił pierwszego napotkanego
                    break
            
            # Jeśli pocisk trafił w cokolwiek, usuwamy go z listy gracza
            if shot_hit:
                if shot in player.shots:
                    player.shots.remove(shot)

        for enemy in enemy_manager.enemies:
            for shot in enemy.shots[:]:
                dist_sq = (shot["pos"] - player.player_pos).length_squared()
                
                # Dla gracza też używamy samej odległości, żeby było sprawiedliwie
                # Promień 35-40px jest wystarczający
                if dist_sq < 35**2:
                    if not player.shield_active:
                        player.hp -= shot["damage"]
                        
                        if shot in enemy.shots:
                            enemy.shots.remove(shot)
                        
                        if player.hp <= 0:
                            return True # Sygnał Game Over
                    
                    else:
                        self.music_obj.play("images/audio/kenney_sci-fi-sounds/forceField_001.wav", 0.1)

        # 3. KOLIZJA: STATEK -> STATEK (KAMIKAZE)
        # Tutaj zostawiamy maski, bo statki są duże, powolne i chcemy precyzji przy mijaniu się.
        for enemy in enemy_manager.enemies[:]:
            dist_sq = (player.player_pos - enemy.pos).length_squared()
            
            # Broad phase: sprawdzamy maski tylko gdy statki są blisko (< 80px)
            if dist_sq < 80**2:
                hit = self.check_mask_collision(
                    player.actual_frame, player.player_pos, player.angle,
                    enemy.image, enemy.pos, enemy.angle
                )
                
                if hit:
                    # Efekt fizyczny: odepchnięcie
                    push_dir = (player.player_pos - enemy.pos)
                    if push_dir.length() > 0:
                        push_dir = push_dir.normalize()
                    else:
                        push_dir = pygame.math.Vector2(1, 0) # Zabezpieczenie przed wektorem zero
                        
                    player.player_pos += push_dir * 25
                    player.velocity *= -0.5 # Nagłe zatrzymanie/odbicie
                    
                    player.hp -= 15
                    enemy.hp -= 100 # Kolizja niszczy wroga natychmiast
                    
                    if enemy.hp <= 0:
                        if enemy in enemy_manager.enemies:
                            enemy_manager.enemies.remove(enemy)

        return False