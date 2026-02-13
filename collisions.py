import pygame
import math

def get_masked_data(image, pos, angle):
    """
    Pomocnicza funkcja, która tworzy obrócony obrazek, jego rect i maskę w locie.
    Wymagana, ponieważ Twoje statki obracają się w czasie rzeczywistym.
    """
    rotated_image = pygame.transform.rotate(image, angle)
    # Tworzymy rect wyśrodkowany na pozycji w świecie gry (World Coordinates)
    rect = rotated_image.get_rect(center=(pos.x, pos.y))
    mask = pygame.mask.from_surface(rotated_image)
    return rect, mask

def check_mask_collision(obj1_img, obj1_pos, obj1_angle, obj2_img, obj2_pos, obj2_angle):
    """
    Sprawdza kolizję pixel-perfect między dwoma obiektami.
    """
    # Tworzymy dane dla obiektu 1
    rect1, mask1 = get_masked_data(obj1_img, obj1_pos, obj1_angle)
    
    # Tworzymy dane dla obiektu 2
    rect2, mask2 = get_masked_data(obj2_img, obj2_pos, obj2_angle)

    # Obliczamy przesunięcie (offset) maski 2 względem maski 1
    offset_x = rect2.left - rect1.left
    offset_y = rect2.top - rect1.top
import pygame
import math

def get_masked_data(image, pos, angle):
    """
    Pomocnicza funkcja dla kolizji pixel-perfect (używana tylko dla statków).
    """
    rotated_image = pygame.transform.rotate(image, angle)
    rect = rotated_image.get_rect(center=(pos.x, pos.y))
    mask = pygame.mask.from_surface(rotated_image)
    return rect, mask

def check_mask_collision(obj1_img, obj1_pos, obj1_angle, obj2_img, obj2_pos, obj2_angle):
    """
    Sprawdza kolizję pixel-perfect między dwoma dużymi obiektami (statkami).
    """
    rect1, mask1 = get_masked_data(obj1_img, obj1_pos, obj1_angle)
    rect2, mask2 = get_masked_data(obj2_img, obj2_pos, obj2_angle)

    offset_x = rect2.left - rect1.left
    offset_y = rect2.top - rect1.top

    return mask1.overlap(mask2, (offset_x, offset_y))

def check_collisions(player, enemy_manager):
    """
    Główna funkcja sprawdzająca wszystkie typy kolizji.
    """
    
    # 1. KOLIZJA: POCISKI GRACZA -> PRZECIWNICY
    # Pociski są szybkie, więc używamy kolizji kołowej (dystansowej) dla 100% pewności trafienia.
    for shot in player.shots[:]:
        for enemy in enemy_manager.enemies[:]:
            dist_sq = (shot["pos"] - enemy.pos).length_squared()
            
            # hit_radius: Promień wroga (np. 40-50px) + promień pocisku (np. 5px)
            # Zwiększamy ten promień, jeśli pociski nadal "przelatują"
            hit_threshold = 50**2 
            
            if dist_sq < hit_threshold:
                # TRAFIENIE!
                enemy.hp -= shot["damage"]
                
                if shot in player.shots:
                    player.shots.remove(shot)
                
                if enemy.hp <= 0:
                    if enemy in enemy_manager.enemies:
                        enemy_manager.enemies.remove(enemy)
                
                # Ten pocisk już został zużyty, wychodzimy z pętli wrogów
                break

    # 2. KOLIZJA: POCISKI PRZECIWNIKA -> GRACZ
    for enemy in enemy_manager.enemies:
        for shot in enemy.shots[:]:
            dist_sq = (shot["pos"] - player.player_pos).length_squared()
            
            # Promień gracza jest nieco mniejszy dla sprawiedliwości
            if dist_sq < 35**2:
                player.hp -= shot["damage"]
                
                if shot in enemy.shots:
                    enemy.shots.remove(shot)
                
                if player.hp <= 0:
                    return True # Sygnał Game Over

    # 3. KOLIZJA: STATEK -> STATEK (KAMIKAZE)
    # Tutaj zostawiamy maski, bo statki są duże i chcemy, żeby otarcia skrzydeł wyglądały realistycznie.
    for enemy in enemy_manager.enemies[:]:
        dist_sq = (player.player_pos - enemy.pos).length_squared()
        
        # Szeroki test (broad phase) - sprawdzamy maski tylko gdy statki są blisko
        if dist_sq < 80**2:
            hit = check_mask_collision(
                player.actual_frame, player.player_pos, player.angle,
                enemy.image, enemy.pos, enemy.angle
            )
            
            if hit:
                # Efekt fizyczny: odepchnięcie
                push_dir = (player.player_pos - enemy.pos)
                if push_dir.length() > 0:
                    push_dir = push_dir.normalize()
                    player.player_pos += push_dir * 25
                    player.velocity *= -0.5 # Nagłe zatrzymanie/odbicie
                
                player.hp -= 15
                enemy.hp -= 100 # Kolizja statków niszczy wroga natychmiast
                
                if enemy.hp <= 0:
                    if enemy in enemy_manager.enemies:
                        enemy_manager.enemies.remove(enemy)

    return False
    # Sprawdzamy, czy piksele się pokrywają (zwraca punkt kolizji lub None)
    return mask1.overlap(mask2, (offset_x, offset_y))# W collisions.py

def check_collisions(player, enemy_manager):
    # 1. KOLIZJA: POCISKI GRACZA -> PRZECIWNICY
    # Używamy kopii list [:] aby bezpiecznie usuwać obiekty podczas pętli
    for shot in player.shots[:]:
        for enemy in enemy_manager.enemies[:]:
            # Najpierw szybki test dystansu (optymalizacja)
            dist_sq = (shot["pos"] - enemy.pos).length_squared()
            
            # Jeśli pocisk jest blisko statku (np. 45 px)
            if dist_sq < 45**2:
                # Opcjonalnie: Dokładna kolizja maskami
                hit = check_mask_collision(
                    shot["img"], shot["pos"], shot["dir"],
                    enemy.image, enemy.pos, enemy.angle
                )
                
                if hit:
                    enemy.hp -= shot["damage"]
                    if shot in player.shots:
                        player.shots.remove(shot)
                    
                    if enemy.hp <= 0:
                        if enemy in enemy_manager.enemies:
                            enemy_manager.enemies.remove(enemy)
                    break # Ten pocisk już trafił, sprawdzamy następny

    # 2. KOLIZJA: POCISKI PRZECIWNIKA -> GRACZ
    for enemy in enemy_manager.enemies:
        for shot in enemy.shots[:]:
            dist_sq = (shot["pos"] - player.player_pos).length_squared()
            if dist_sq < 40**2:
                hit = check_mask_collision(
                    shot["img"], shot["pos"], shot["dir"],
                    player.actual_frame, player.player_pos, player.angle
                )
                if hit:
                    player.hp -= shot["damage"]
                    if shot in enemy.shots:
                        enemy.shots.remove(shot)
                    if player.hp <= 0:
                        return True # Gracz zniszczony

    # 3. KOLIZJA: STATEK -> STATEK
    for enemy in enemy_manager.enemies[:]:
        dist_sq = (player.player_pos - enemy.pos).length_squared()
        if dist_sq < 60**2:
            hit = check_mask_collision(
                player.actual_frame, player.player_pos, player.angle,
                enemy.image, enemy.pos, enemy.angle
            )
            if hit:
                # Odepchnij gracza
                push_dir = (player.player_pos - enemy.pos).normalize()
                player.player_pos += push_dir * 20
                player.velocity *= -0.5
                
                player.hp -= 10
                enemy.hp -= 100 # Natychmiastowe zniszczenie wroga
                if enemy.hp <= 0:
                    enemy_manager.enemies.remove(enemy)

    return False