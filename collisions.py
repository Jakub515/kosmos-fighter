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
        # --- 1. KOLIZJE POCISKÓW ---
        for shot in shoot_obj.shots[:]:
            # Jeśli pocisk już jest w fazie wybuchu, nie sprawdzamy kolizji ponownie
            if shot.get("is_exploding"):
                continue

            shot_hit = False
            
            # A. Pocisk gracza (leci w stronę wrogów)
            if not shot.get("is_enemy_shot", False):
                for enemy in enemy_manager.enemies[:]:
                    dist_sq = (shot["pos"] - enemy.pos).length_squared()
                    
                    # Zakładamy promień kolizji wroga ok. 60 pikseli
                    if dist_sq < 60**2:
                        enemy.hp -= shot["damage"]
                        shot_hit = True
                        
                        if enemy.hp <= 0:
                            if enemy in enemy_manager.enemies:
                                enemy_manager.enemies.remove(enemy)
                                # Opcjonalnie: dźwięk wybuchu wroga
                                self.music_obj.play("images/audio/sfx_exp_medium1.wav", 0.2)
                        break 

            # B. Pocisk wroga (leci w stronę gracza)
            else:
                dist_sq = (shot["pos"] - player.player_pos).length_squared()
                if dist_sq < 35**2: # Promień kolizji gracza
                    shot_hit = True
                    if not player.shield_active:
                        player.hp -= shot["damage"]
                    else:
                        # Dźwięk uderzenia w tarczę
                        self.music_obj.play("images/audio/kenney_sci-fi-sounds/forceField_001.wav", 0.25)
                    
                    if player.hp <= 0:
                        return True # Game Over

            # --- LOGIKA WYBUCHU RAKIETY PO TRAFIENIU ---
            if shot_hit:
                if shot.get("rocket"):
                    # Jeśli to rakieta, aktywujemy animację dymu z shoot.py
                    shot["is_exploding"] = True
                    # Zatrzymujemy lub drastycznie spowalniamy pocisk w miejscu wybuchu
                    shot["vel"] *= 0.05 
                else:
                    # Jeśli to zwykły laser, usuwamy go natychmiast
                    if shot in shoot_obj.shots:
                        shoot_obj.shots.remove(shot)

        # --- 2. KOLIZJA: STATEK -> STATEK (ZDERZENIA) ---
        for enemy in enemy_manager.enemies[:]:
            dist_sq = (player.player_pos - enemy.pos).length_squared()
            
            # Wstępny test dystansu przed ciężką kolizją maskową
            if dist_sq < 90**2:
                hit = self.check_mask_collision(
                    player.actual_frame, player.player_pos, player.angle,
                    enemy.image, enemy.pos, enemy.angle
                )
                
                if hit:
                    # Fizyka odrzutu przy zderzeniu
                    push_dir = (player.player_pos - enemy.pos)
                    if push_dir.length() > 0:
                        push_dir = push_dir.normalize()
                    else:
                        push_dir = pygame.math.Vector2(1, 0)
                        
                    player.player_pos += push_dir * 20
                    player.velocity *= -0.5
                    
                    player.hp -= 20
                    enemy.hp -= 100 # Zazwyczaj niszczy małe statki
                    
                    if enemy.hp <= 0:
                        if enemy in enemy_manager.enemies:
                            enemy_manager.enemies.remove(enemy)
        
        return False