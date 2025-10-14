import pygame
from pygame.draw import *
from random import randint, choice
from math import sqrt
import sys
import time

pygame.init()
pygame.mixer.init()  # Явная инициализация микшера звука

FPS = 30
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Поймай шарик")

# Цвета
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

balls = []
squares = []
score = 0
miss_count = 0
max_miss_count = 5

# Фон
try:
    background_img = pygame.image.load('Troll.png').convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except Exception:
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((255, 255, 255))

leaderboard = []

# Загрузка квадратов
square_images = []
square_filenames = ["квадрат1.jpg", "квадрат2.jpg", "квадрат3.jpg", "квадрат4.png", "квадрат5.jpg"]
for filename in square_filenames:
    try:
        img = pygame.image.load(filename).convert_alpha()
        square_images.append(img)
    except Exception as e:
        print(f"Ошибка загрузки {filename}: {e}")
        img = pygame.Surface((50, 50)).convert_alpha()
        img.fill(GREEN)
        square_images.append(img)

# Загрузка кругов
circle_images = []
circle_filenames = ["круг1.jpg", "круг2.png", "круг3.jpg", "круг4.jpg", "круг5.jpg"]
for filename in circle_filenames:
    try:
        img = pygame.image.load(filename).convert_alpha()
        circle_images.append(img)
    except Exception as e:
        print(f"Ошибка загрузки {filename}: {e}")
        img = pygame.Surface((40, 40)).convert_alpha()
        img.fill(RED)
        circle_images.append(img)

# Загрузка звуков
def load_sound(filename):
    try:
        sound = pygame.mixer.Sound(filename)
        return sound
    except pygame.error as e:
        print(f"Ошибка загрузки звука {filename}: {e}")
        return None

sound_hit_circle = load_sound("ПОПАЛКРУГ.wav")  # звук попадания по кругу
sound_hit_square = load_sound("ПОПАЛКВАДРАТ.wav")  # звук попадания по квадрату
sound_miss = load_sound("промах.wav")  # звук промаха
sound_game_over=load_sound("арматура.wav") ##ЕТО КРУТОЙ ЗВУК ПРОИГРЫША

# Загрузка картинки проигрыша
try:
    game_over_img = pygame.image.load('поражение.jpg').convert_alpha()
    game_over_img = pygame.transform.scale(game_over_img, (300, 200))
except Exception as e:
    print(f"Ошибка загрузки картинки проигрыша: {e}")
    game_over_img = None


def create_ball():
    r = randint(20, 40)
    x = randint(r, WIDTH - r)
    y = randint(r, HEIGHT - r)
    dx = choice([-5, -4, -3, 3, 4, 5])
    dy = choice([-5, -4, -3, 3, 4, 5])
    img = choice(circle_images)
    balls.append({'x': x, 'y': y, 'r': r, 'dx': dx, 'dy': dy, 'img': img})


def create_square():
    size = randint(30, 50)
    x = randint(size, WIDTH - size)
    y = randint(size, HEIGHT - size)
    dx = choice([-6, -5, 5, 6])
    img = choice(square_images)
    squares.append({'x': x, 'y': y, 'size': size, 'dx': dx, 'img': img})


def move_balls():
    for ball in balls:
        ball['x'] += ball['dx']
        ball['y'] += ball['dy']
        if ball['x'] - ball['r'] <= 0 or ball['x'] + ball['r'] >= WIDTH:
            ball['dx'] = -ball['dx']
        if ball['y'] - ball['r'] <= 0 or ball['y'] + ball['r'] >= HEIGHT:
            ball['dy'] = -ball['dy']


def move_squares():
    for sq in squares:
        sq['x'] += sq['dx']
        if sq['x'] - sq['size'] <= 0 or sq['x'] + sq['size'] >= WIDTH:
            sq['dx'] = -sq['dx']


def draw_objects():
    for ball in balls:
        scaled_img = pygame.transform.smoothscale(ball['img'], (ball['r'] * 2, ball['r'] * 2))
        rect = scaled_img.get_rect(center=(int(ball['x']), int(ball['y'])))
        screen.blit(scaled_img, rect)
    for sq in squares:
        scaled_img = pygame.transform.smoothscale(sq['img'], (sq['size'] * 2, sq['size'] * 2))
        rect = scaled_img.get_rect(center=(int(sq['x']), int(sq['y'])))
        screen.blit(scaled_img, rect)
        
def check_click(pos):
    try:
        x, y = pos
    except Exception as e:
        print(f"Ошибка распаковки pos в check_click: {e}. Значение pos: {pos}")
        return False  # Не обработан клик, т.к. неверные координаты

    # ... остальной код проверки попадания ...
    global score, miss_count
    hit = False
    for i in reversed(range(len(balls))):
        ball = balls[i]
        dx = x - ball['x']
        dy = y - ball['y']
        if dx * dx + dy * dy <= ball['r'] * ball['r']:
            score += 1
            del balls[i]
            hit = True
            if sound_hit_circle:
                sound_hit_circle.play()
            break

    if not hit:
        for i in reversed(range(len(squares))):
            sq = squares[i]
            if (sq['x'] - sq['size'] <= x <= sq['x'] + sq['size'] and
                    sq['y'] - sq['size'] <= y <= sq['y'] + sq['size']):
                score += 3
                del squares[i]
                hit = True
                if sound_hit_square:
                    sound_hit_square.play()
                break

    if not hit:
        miss_count += 1
        if sound_miss:
            sound_miss.play()

    return hit


def draw_score():
    font = pygame.font.Font(None, 30)
    text = font.render(f"Очки: {score}", True, BLACK)
    screen.blit(text, (10, 10))


def draw_miss_count():
    font = pygame.font.Font(None, 30)
    text = font.render(f"Промахи: {miss_count}/{max_miss_count}", True, BLACK)
    screen.blit(text, (10, 50))


def draw_time_left(time_left):
    font = pygame.font.Font(None, 30)
    minutes = int(time_left) // 60
    seconds = int(time_left) % 60
    text = font.render(f"Время: {minutes:02}:{seconds:02}", True, BLACK)
    screen.blit(text, (WIDTH - text.get_width() - 10, 10))


def draw_signature():
    font = pygame.font.Font(None, 20)
    text = font.render("Memoclick2017-byVovochkaM", True, BLACK)
    screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT - text.get_height() - 5))


def save_score_to_leaderboard(user_score):
    global leaderboard
    leaderboard.append(user_score)
    leaderboard.sort(reverse=True)
    if len(leaderboard) > 5:
        leaderboard.pop()


def show_leaderboard():
    global leaderboard 
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 40)
    title = font.render("Таблица лидеров", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    font_score = pygame.font.Font(None, 30)
    for i, val in enumerate(leaderboard):
        text = font_score.render(f"{i + 1}. {val} очков", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 40))

    draw_signature()
    pygame.display.update()


def draw_game_over_screen():
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 50)
    text = font.render("Вы проиграли, удалите ПК", True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))
    if game_over_img:
        img_rect = game_over_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(game_over_img, img_rect)
        # Подпись под картинкой
        font_sub = pygame.font.Font(None, 30)
        sub_text = font_sub.render("дядюшка Нагиев зол...", True, BLACK)
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        screen.blit(sub_text, sub_rect)
    screen.blit(text, text_rect)
    pygame.display.update()

    if sound_game_over:
        sound_game_over.play()


def game_over():
    draw_game_over_screen()
    pygame.time.delay(3000)
    save_score_to_leaderboard(score)
    show_leaderboard()
    pygame.time.delay(5000)
    pygame.quit()
    sys.exit()


def main():
    global miss_count, score
    clock = pygame.time.Clock()
    running = True
    start_time = time.time()
    game_duration = 300

    add_ball_event = pygame.USEREVENT + 1
    pygame.time.set_timer(add_ball_event, 1000)

    add_square_event = pygame.USEREVENT + 2
    pygame.time.set_timer(add_square_event, 2500)

    for _ in range(3):
        create_ball()
    for _ in range(2):
        create_square()

    while running:
        elapsed_time = time.time() - start_time
        time_left = max(0, game_duration - elapsed_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                check_click(event.pos)
            elif event.type == add_ball_event:
                if len(balls) < 6:
                    create_ball()
            elif event.type == add_square_event:
                if len(squares) < 3:
                    create_square()

        move_balls()
        move_squares()

        screen.blit(background_img, (0, 0))
        draw_objects()
        draw_score()
        draw_miss_count()
        draw_time_left(time_left)
        draw_signature()

        if miss_count >= max_miss_count or elapsed_time >= game_duration:
            running = False

        pygame.display.update()
        clock.tick(FPS)

    game_over()


if __name__ == "__main__":
    main()