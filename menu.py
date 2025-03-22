import pygame # type: ignore
import log
import sys

pygame.init()

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Ukuran layar
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w - 100
HEIGHT = screen_info.current_h - 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pixel Shooter - Menu")

# Font
font = pygame.font.Font(None, 50)
title_font = pygame.font.Font(None, 80)

# Fungsi menggambar tombol
def draw_button(text, x, y, width, height, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(SCREEN, hover_color if rect.collidepoint(mouse_pos) else color, rect)
    text_surface = font.render(text, True, BLACK)
    SCREEN.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))
    return rect

# Fungsi tampilan menu utama
def main_menu():
    while True:
        SCREEN.fill(WHITE)
        
        # Tampilkan judul game
        title_text = title_font.render("Pixel Shooter", True, BLACK)
        SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        # Buat tombol
        play_button = draw_button("Main", WIDTH // 2 - 100, 250, 200, 50, GRAY, RED)
        score_button = draw_button("Skor Tertinggi", WIDTH // 2 - 100, 320, 200, 50, GRAY, RED)
        quit_button = draw_button("Keluar", WIDTH // 2 - 100, 390, 200, 50, GRAY, RED)

        # Cek event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "play"
                elif score_button.collidepoint(event.pos):
                    show_high_scores()
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

# Fungsi menampilkan skor tertinggi
def show_high_scores():
    high_scores = log.get_high_scores()
    while True:
        SCREEN.fill(WHITE)
        title_text = title_font.render("Skor Tertinggi", True, BLACK)
        SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, score in enumerate(high_scores[:5], start=1):
            score_text = font.render(f"{i}. {score}", True, BLACK)
            SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 150 + i * 50))

        back_button = draw_button("Kembali", WIDTH // 2 - 100, 500, 200, 50, GRAY, RED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                return

        pygame.display.update()
