import pygame # type: ignore
import random
import math
import os
import log
import menu
import sys
pygame.init()
pygame.mixer.init()

# Menampilkan menu utama sebelum game dimulai
if menu.main_menu() == "play":
    # Game dimulai seperti biasa
    pass
else:
    pygame.quit()
    sys.exit()

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_sound(file):
    """because pygame can be compiled without mixer."""
    if not pygame.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print(f"Warning, unable to load, {file}")
    return None

boom_sound = load_sound("boom.wav")
shoot_sound = load_sound("car_door.wav")
brak_sound = load_sound("whiff.wav")
defeat_sound = load_sound("Defeat2.ogg")
if pygame.mixer:
    music = os.path.join(main_dir, "data", "house_lo.mp3")
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)

# Dapatkan ukuran layar
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w - 100
HEIGHT = screen_info.current_h - 60
RES = (WIDTH, HEIGHT)

# Buat tampilan
SCREEN = pygame.display.set_mode(RES, pygame.RESIZABLE)
pygame.display._set_autoresize(False)
pygame.display.set_caption("Pixel Shooter - Arcade")

# Warna
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SILVER = (192, 192, 192)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Kecepatan
SPEED = 5
BASE_ENEMY_SPEED = 2
ENEMY_SPEED = BASE_ENEMY_SPEED
BULLET_SPEED = 10
SHOOT_DELAY = 10
SHIELD_RADIUS = 50

# Load karakter
player_size = 40
player_img = pygame.image.load("char.png")
player_img = pygame.transform.scale(player_img, (player_size, player_size))

enemy_img = pygame.image.load(os.path.join(main_dir, "data", "alien1.gif"))
exp_size = 50
explosion_img = pygame.image.load(os.path.join(main_dir, "data", "ledakan1.gif"))
explosion_img = pygame.transform.scale(explosion_img, (exp_size, exp_size))

bullet_img = pygame.image.load(os.path.join(main_dir, "data", "shot.gif"))
bullet_img = pygame.transform.scale(bullet_img, (10, 10))

# Tambahkan sebelum game loop
PAUSE_BUTTON_SIZE = 50
pause_img = pygame.image.load(os.path.join(main_dir, "data", "pause.png"))
pause_img = pygame.transform.scale(pause_img, (PAUSE_BUTTON_SIZE, PAUSE_BUTTON_SIZE))

# Fungsi menggambar tombol
def draw_button(text, x, y, width, height, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(SCREEN, hover_color if rect.collidepoint(mouse_pos) else color, rect)
    text_surface = pygame.font.Font(None, 36).render(text, True, BLACK)
    SCREEN.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))
    return rect

# Fungsi tampilan jeda
def pause_menu():
    global paused

    # Gambar permukaan transparan hanya sekali
    pause_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pause_bg.fill((0, 0, 0, 10))

    while paused:
        SCREEN.blit(pause_bg, (0, 0))
        title_text = pygame.font.Font(None, 50).render("Permainan Dijeda", True, WHITE)
        SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        # Tombol jeda
        resume_button = draw_button("Lanjut", WIDTH // 2 - 100, 200, 200, 50, GRAY, RED)
        menu_button = draw_button("Kembali ke Menu", WIDTH // 2 - 100, 270, 200, 50, GRAY, RED)
        quit_button = draw_button("Keluar", WIDTH // 2 - 100, 340, 200, 50, GRAY, RED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    paused = False
                elif menu_button.collidepoint(event.pos):
                    return "menu"
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

# Variabel game
def reset_game():
    global player_x, player_y, bullets, enemies, score, lives, running, game_over, shooting, paused, last_shot_time, current_weapon, enemy_size, enemy_scaled_img, ledak
    enemy_size = 30
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    bullets = []
    enemies = []
    ledak = []
    score = 0
    lives = 10
    current_weapon = "gun"
    game_over = False
    shooting = False
    paused = False
    last_shot_time = pygame.time.get_ticks()

    # Skala ulang gambar enemy agar sesuai dengan ukuran enemy
    global enemy_img
    enemy_scaled_img = pygame.transform.scale(enemy_img, (enemy_size, enemy_size))

reset_game()
SPAWN_TIME = 500
last_spawn_time = pygame.time.get_ticks()

# Fungsi spawn musuh
def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = pygame.display.get_surface().get_size()
    enemy_size
    if side == "top":
        enemy_x, enemy_y = random.randint(0, WIDTH - enemy_size), -enemy_size
    elif side == "bottom":
        enemy_x, enemy_y = random.randint(0, WIDTH - enemy_size), HEIGHT
    elif side == "left":
        enemy_x, enemy_y = -enemy_size, random.randint(0, HEIGHT - enemy_size)
    else:
        enemy_x, enemy_y = WIDTH, random.randint(0, HEIGHT - enemy_size)
    enemies.append([enemy_x, enemy_y, enemy_size])

# Game Loop
running = True
while running:
    pygame.time.delay(30)
    current_time = pygame.time.get_ticks()

    # Cek event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Tekan tombol "Esc" untuk keluar game atau Restart game saat Game Over jika tombol "Enter" ditekan
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN:
                if game_over:
                    reset_game()
                    pygame.mixer.music.play(-1)
                    music = True

        # Tombol "P" untuk pause/unpause
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            if not paused:
                paused = True
                result = pause_menu()
                if result == "menu":
                    import menu
                    if menu.main_menu() == "play":
                        reset_game()
                    else:
                        running = False
            else:
                paused = False
                
        # Tombol "Q" untuk mengganti senjata
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                current_weapon = "shield" if current_weapon == "gun" else "gun"

        # Tombol jeda
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 10 <= event.pos[0] <= 10 + PAUSE_BUTTON_SIZE and 10 <= event.pos[1] <= 10 + PAUSE_BUTTON_SIZE:
                paused = True
                result = pause_menu()
                if result == "menu":
                    import menu
                    if menu.main_menu() == "play":
                        reset_game()
                    else:
                        running = False

        if not paused and not game_over:  # Jika game tidak dalam keadaan pause
            # Jika mouse ditekan, mulai menembak
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_weapon == "gun":
                shooting = True

            # Jika mouse dilepas, berhenti menembak
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                shooting = False

    # Jika game tidak dijeda, update semua elemen
    if not paused and not game_over:
        # Jika menahan klik kiri, tembak secara otomatis dengan delay
        if shooting and current_weapon == "gun" and current_time - last_shot_time > SHOOT_DELAY:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            angle = math.atan2(mouse_y - (player_y + player_size // 2), mouse_x - (player_x + player_size // 2))
            dx = BULLET_SPEED * math.cos(angle)
            dy = BULLET_SPEED * math.sin(angle)
            bullets.append([player_x + player_size // 2, player_y + player_size // 2, dx, dy])
            last_shot_time = current_time
            shoot_sound.play()

        # Ambil input keyboard untuk gerakan
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: player_x -= SPEED
        if keys[pygame.K_d]: player_x += SPEED
        if keys[pygame.K_w]: player_y -= SPEED
        if keys[pygame.K_s]: player_y += SPEED

        # Batasi gerakan dalam layar
        player_x = max(0, min(WIDTH - player_size, player_x))
        player_y = max(0, min(HEIGHT - player_size, player_y))

        # Peningkatan kecepatan musuh setiap 10 skor
        ENEMY_SPEED = BASE_ENEMY_SPEED + ( score // 10 ) * 0.5

        # Update peluru
        for bullet in bullets:
            bullet[0] += bullet[2]  # dx
            bullet[1] += bullet[3]  # dy
        bullets = [bullet for bullet in bullets if 0 < bullet[0] < WIDTH and 0 < bullet[1] < HEIGHT]

        # Spawn musuh
        if current_time - last_spawn_time > SPAWN_TIME:
            spawn_enemy()
            last_spawn_time = current_time

        # Update musuh
        new_enemies = []
        for enemy in enemies:
            angle = math.atan2(player_y - enemy[1], player_x - enemy[0])
            enemy[0] += ENEMY_SPEED * math.cos(angle)
            enemy[1] += ENEMY_SPEED * math.sin(angle)

            # Jika musuh mengenai perisai, dorong menjauh
            if current_weapon == "shield":
                distance = math.hypot(player_x - enemy[0], player_y - enemy[1])
                if distance < SHIELD_RADIUS:
                    brak_sound.play()
                    push_angle = math.atan2(enemy[1] - player_y, enemy[0] - player_x)
                    # Dorongan menjauh ke arah horizontal (y)
                    enemy[0] += 300 * math.cos(push_angle)  
                    # Dorongan menjauh ke arah vertikal (x)
                    enemy[1] += 180 * math.sin(push_angle)

            # cek tabrakan dengan pemain
            if pygame.Rect(player_x, player_y, player_size, player_size).colliderect(pygame.Rect(enemy[0], enemy[1], enemy[2], enemy[2])):
                lives -= 1  
            else:
                new_enemies.append(enemy)
        enemies = new_enemies

        # Cek peluru kena musuh
        new_enemies = []
        for enemy in enemies:
            hit = any(pygame.Rect(enemy[0], enemy[1], enemy[2], enemy[2]).colliderect(pygame.Rect(bullet[0], bullet[1], 5, 5)) for bullet in bullets)     
            if not hit:
                new_enemies.append(enemy)
            else:
                boom_sound.play()
                ledak.append([enemy[0], enemy[1], current_time])
                score += 1  
        enemies = new_enemies

        ledak = [exp for exp in ledak if current_time - exp[2] < 100]

        # Jika nyawa habis, game over
        if lives <= 0:
            game_over = True
            defeat_sound.play()
            log.save_score(score)
            high_scores = log.get_high_scores()
            print("\n=== SKOR TERTINGGI ===")
            for i, hs in enumerate(high_scores, 1):
                print(f"{i}. {hs}")

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)


    # Gambar ulang layar
    SCREEN.fill(BROWN)
    SCREEN.blit(player_img, (player_x, player_y))

    # Gambar tombol jeda di pojok kiri atas
    SCREEN.blit(pause_img, (10, 10))

    # Gambar perisai jika aktif
    if current_weapon == "shield":
        pygame.draw.circle(SCREEN, BLACK, (player_x + player_size // 2, player_y + player_size // 2), SHIELD_RADIUS, 3)

    # Gambar skor dan nyawa
    font = pygame.font.Font(None, 36)
    text = font.render(f"Skor: {score} | Nyawa: {lives}", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, 20))
    SCREEN.blit(text, text_rect)

    # Gambar musuh
    for enemy in enemies:
        SCREEN.blit(enemy_scaled_img, (enemy[0], enemy[1]))
    for exp in ledak:
        SCREEN.blit(explosion_img, (exp[0], exp[1]))

    # Gambar peluru
    for bullet in bullets:
        angle = math.degrees(math.atan2(-bullet[3], bullet[2]))
        rotated_bullet = pygame.transform.rotate(bullet_img, angle)
        SCREEN.blit(rotated_bullet, (bullet[0], bullet[1]))

    # Jika game over, tampilkan teks "GAME OVER"
    if game_over:
        game_over_text = font.render("GAME OVER - Tekan ENTER untuk Restart atau Tekan ESC untuk Keluar", True, RED)
        SCREEN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        paused = False
        pygame.mixer.music.stop()
        music = True

    pygame.display.update()

pygame.quit()
