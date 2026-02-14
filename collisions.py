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

    def check_collisions(self, player, enemy_manager, shoot_obj):
        """
        Główna funkcja sprawdzająca kolizje przy założeniu, że shoot_obj 
        zarządza wszystkimi pociskami.
        """
        
        # --- 1. KOLIZJE POCISKÓW ---
        # Iterujemy po wszystkich pociskach z shoot_obj
        for shot in shoot_obj.shots[:]:
            shot_hit = False
            
            # A. Pocisk gracza (leci w stronę wrogów)
            if not shot.get("is_enemy_shot", False):
                for enemy in enemy_manager.enemies[:]:
                    dist_sq = (shot["pos"] - enemy.pos).length_squared()
                    
                    if dist_sq < 60**2: # Promień trafienia wroga
                        enemy.hp -= shot["damage"]
                        shot_hit = True
                        
                        if enemy.hp <= 0:
                            if enemy in enemy_manager.enemies:
                                enemy_manager.enemies.remove(enemy)
                        break # Ten pocisk już trafił, kończymy pętlę wrogów

            # B. Pocisk wroga (leci w stronę gracza)
            else:
                dist_sq = (shot["pos"] - player.player_pos).length_squared()
                
                if dist_sq < 35**2: # Promień trafienia gracza
                    shot_hit = True
                    if not player.shield_active:
                        player.hp -= shot["damage"]
                    else:
                        self.music_obj.play("images/audio/kenney_sci-fi-sounds/forceField_001.wav", 0.25)
                    
                    if player.hp <= 0:
                        return True # Game Over

            # Jeśli pocisk w coś trafił (wroga lub gracza), usuwamy go z globalnej listy
            if shot_hit:
                if shot in shoot_obj.shots:
                    shoot_obj.shots.remove(shot)

        # --- 2. KOLIZJA: STATEK -> STATEK (KAMIKAZE) ---
        # (Logika pozostaje bez zmian, bo dotyczy fizycznego kontaktu jednostek)
        for enemy in enemy_manager.enemies[:]:
            dist_sq = (player.player_pos - enemy.pos).length_squared()
            
            if dist_sq < 80**2:
                hit = self.check_mask_collision(
                    player.actual_frame, player.player_pos, player.angle,
                    enemy.image, enemy.pos, enemy.angle
                )
                
                if hit:
                    # Fizyka odbicia
                    push_dir = (player.player_pos - enemy.pos)
                    push_dir = push_dir.normalize() if push_dir.length() > 0 else pygame.math.Vector2(1, 0)
                        
                    player.player_pos += push_dir * 25
                    player.velocity *= -0.5
                    
                    player.hp -= 15
                    enemy.hp -= 100 
                    
                    if enemy.hp <= 0:
                        if enemy in enemy_manager.enemies:
                            enemy_manager.enemies.remove(enemy)

        return False