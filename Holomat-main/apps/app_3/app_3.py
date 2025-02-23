#ARCADE WITH SPACE INVADERS AND BREAKOUT
#MAKE SURE TO DOWNLOAD IMAGES FOLDER AS WELL AND PUT IT INTO THE APPS FOLDER

import pygame
from pygame import mixer
import sys
import math
import time

from dotenv import load_dotenv
import os

load_dotenv()
pygame.init()
mixer.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1200 
SCREEN_SIZE = (1920, 500)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
NAVY_BLUE = (20, 20, 40)

def play_sound(file_path):
    try:
        mixer.music.load(file_path)
        mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound {file_path}: {e}")

def space_invaders(screen, camera_manager, SCREEN_SIZE):
    import pygame
    import sys
    import math
    from camera_manager import CameraManager

    pygame.init()

    pygame.display.set_caption("Space Invaders with Hand Control")

    player_scale = 8
    invader_scale = 3

    player_img = pygame.image.load("apps/app_3/player.png")
    invader1_img = pygame.image.load("apps/app_3/invader1.png")
    invader2_img = pygame.image.load("apps/app_3/invader2.png")

    player_img = pygame.transform.scale(player_img, (int(player_img.get_width() * player_scale), int(player_img.get_height() * player_scale)))
    invader1_img = pygame.transform.scale(invader1_img, (int(invader1_img.get_width() * invader_scale), int(invader1_img.get_height() * invader_scale)))
    invader2_img = pygame.transform.scale(invader2_img, (int(invader2_img.get_width() * invader_scale), int(invader2_img.get_height() * invader_scale)))

    player_width = player_img.get_width()
    player_height = player_img.get_height()

    

    home_button_center = (60, 60)
    home_button_radius = 50

    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def initialize_game():
        player = pygame.Rect(SCREEN_SIZE[0] // 2 - player_width // 2, SCREEN_SIZE[1] - player_height - 10, player_width, player_height)

        bullets = []
        invaders = []
        invader_rows = 5
        invader_columns = 11
        invader_gap = 15

        for row in range(invader_rows):
            for col in range(invader_columns):
                x = col * (invader1_img.get_width() + invader_gap) + 150
                y = row * (invader1_img.get_height() + invader_gap) + 50
                invader_rect = pygame.Rect(x, y, invader1_img.get_width(), invader1_img.get_height())
                if row < 3:
                    invaders.append((invader_rect, invader1_img))
                else:
                    invaders.append((invader_rect, invader2_img))

        return player, bullets, invaders

    global can_shoot

    player, bullets, invaders = initialize_game()

    running = True

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    LIGHT_BLUE = (173, 216, 230)
    NAVY_BLUE = (20, 20, 40)

    player_speed = 5
    bullet_speed = -10
    invader_speed_x = 3
    invader_speed_y = 10
    invader_drop_speed = 20
    invader_direction = 1
    invader_speed_increase_factor = 1.07
    can_shoot = True

    while running:
        if not camera_manager.update():
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                camera_manager.release()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if distance(mouse_pos, home_button_center) <= home_button_radius:
                    running = False

        screen.fill(BLACK)

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))
                player.centerx = index_pos[0]
                player.clamp_ip(screen.get_rect())

        if can_shoot:
            play_sound('./apps/app_3/laser.mp3')
            bullet = pygame.Rect(player.centerx - 2.5, player.top - 10, 5, 10)
            bullets.append(bullet)
            can_shoot = False

        for bullet in bullets[:]:
            bullet.y += bullet_speed
            if bullet.bottom < 0:
                bullets.remove(bullet)
                can_shoot = True

        move_down = False
        for invader, _ in invaders:
            invader.x += invader_speed_x * invader_direction
            if invader.left <= 0 or invader.right >= SCREEN_SIZE[0]:
                move_down = True

        if move_down:
            invader_direction *= -1
            for invader, _ in invaders:
                invader.y += invader_drop_speed
                invader.x += invader_speed_x * invader_direction

            invader_speed_x *= invader_speed_increase_factor

        for bullet in bullets[:]:
            for invader, img in invaders[:]:
                if bullet.colliderect(invader):
                    play_sound('./apps/app_3/explosion.mp3')
                    invaders.remove((invader, img))
                    bullets.remove(bullet)
                    can_shoot = True
                    break

        for invader, img in invaders:
            screen.blit(img, invader.topleft)

        screen.blit(player_img, player.topleft)
        for bullet in bullets:
            pygame.draw.rect(screen, RED, bullet)

        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, home_button_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, home_button_radius, 5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        if transformed_landmarks:
            index_pos = (int(transformed_landmarks[0][8][0]), int(transformed_landmarks[0][8][1]))
            if distance(index_pos, home_button_center) <= home_button_radius:
                running = False

        if not invaders:
            font = pygame.font.SysFont(None, 55)
            win_text = font.render("YOU WIN!", True, WHITE)
            screen.blit(win_text, (SCREEN_SIZE[0] // 2 - win_text.get_width() // 2, SCREEN_SIZE[1] // 2 - win_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(3000)
            running = False

        if any(invader.bottom >= SCREEN_SIZE[1] for invader, _ in invaders):
            font = pygame.font.SysFont(None, 55)
            lose_text = font.render("GAME OVER", True, WHITE)
            screen.blit(lose_text, (SCREEN_SIZE[0] // 2 - lose_text.get_width() // 2, SCREEN_SIZE[1] // 2 - lose_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(3000)
            running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def brick_breaker(screen, camera_manager, SCREEN_SIZE):
    import pygame
    from pygame import mixer
    import sys
    import time
    import math
    from camera_manager import CameraManager

    pygame.init()

    mixer.init()

    

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    NAVY_BLUE = (20, 20, 40)

    PADDLE_WIDTH = 150
    PADDLE_HEIGHT = 20
    BALL_RADIUS = 10
    BRICK_WIDTH = 125
    BRICK_HEIGHT = 30
    BRICKS_PER_ROW = SCREEN_SIZE[0] // BRICK_WIDTH
    BRICK_ROWS = 5
    global ball_dx, ball_dy
    ball_dx = 7  
    ball_dy = -7

    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    def create_bricks():
        bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICKS_PER_ROW):
                brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, BRICK_WIDTH - 5, BRICK_HEIGHT - 5)
                bricks.append(brick)
        return bricks

    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    running = True

    paddle = pygame.Rect(SCREEN_SIZE[0] // 2 - PADDLE_WIDTH // 2, SCREEN_SIZE[1] - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    bricks = create_bricks()

    home_button_center = (100, SCREEN_SIZE[1] - 100)
    home_button_radius = 50

    while running:
        if not camera_manager.update():
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                camera_manager.release()
                sys.exit()

        screen.fill(BLACK)

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))
                paddle.centerx = index_pos[0]
                paddle.clamp_ip(screen.get_rect())

        ball.x += ball_dx
        ball.y += ball_dy

        if ball.left <= 0 or ball.right >= SCREEN_SIZE[0]:
            play_sound('./apps/app_3/bounce.mp3')
            ball_dx *= -1
        if ball.top <= 0:
            play_sound('./apps/app_3/bounce.mp3')
            ball_dy *= -1
        if ball.bottom >= SCREEN_SIZE[1]:
            paddle = pygame.Rect(SCREEN_SIZE[0] // 2 - PADDLE_WIDTH // 2, SCREEN_SIZE[1] - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
            ball = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
            bricks = create_bricks()
            ball_dx, ball_dy = 7, -7

        if ball.colliderect(paddle):
            play_sound('./apps/app_3/bounce.mp3')
            ball_dy *= -1

        for brick in bricks[:]:
            if ball.colliderect(brick):
                bricks.remove(brick)
                play_sound('./apps/app_3/explosion.mp3')
                ball_dy *= -1
                break

        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.ellipse(screen, BLUE, ball)
        for brick in bricks:
            pygame.draw.rect(screen, RED, brick)

        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, home_button_radius)
        pygame.draw.circle(screen, WHITE, home_button_center, home_button_radius, 5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        if transformed_landmarks:
            index_pos = (int(transformed_landmarks[0][8][0]), int(transformed_landmarks[0][8][1]))
            if distance(index_pos, home_button_center) <= home_button_radius:
                running = False

        pygame.display.flip()
        pygame.time.delay(10)

PINCH_THRESHOLD = 40
HOVER_DELAY = 1.0  # Time in seconds to trigger action on hover

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def is_hover(pos, button_center, radius):
    return (pos[0] - button_center[0])**2 + (pos[1] - button_center[1])**2 <= radius**2

def run(screen, camera_manager):
    running = True
    circle_radius = 100
    space_invaders_button_center = (SCREEN_SIZE[0] // 3, SCREEN_SIZE[1] // 2)
    brick_breaker_button_center = (2 * SCREEN_SIZE[0] // 3, SCREEN_SIZE[1] // 2)
    home_button_center = (50 + circle_radius, SCREEN_SIZE[1] - 50 - circle_radius)

    # Load images for buttons
    space_invaders_img = pygame.image.load('./apps/app_3/space_invaders.jpg')
    space_invaders_img = pygame.transform.scale(space_invaders_img, (2 * circle_radius, 2 * circle_radius))

    brick_breaker_img = pygame.image.load('./apps/app_3/brick_breaker.jpg')
    brick_breaker_img = pygame.transform.scale(brick_breaker_img, (2 * circle_radius, 2 * circle_radius))

    # Hover tracking
    hover_start_time = { 'space_invaders': 0, 'brick_breaker': 0, 'home': 0 }

    while running:
        if not camera_manager.update():
            continue

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))  # Index finger tip position

                # Check if hovering over space invaders button
                if is_hover(index_pos, space_invaders_button_center, circle_radius):
                    if hover_start_time['space_invaders'] == 0:
                        hover_start_time['space_invaders'] = time.time()
                    elif time.time() - hover_start_time['space_invaders'] >= HOVER_DELAY:
                        play_sound('./apps/app_3/game_start.mp3')
                        space_invaders(screen, camera_manager, SCREEN_SIZE)  
                        return
                else:
                    hover_start_time['space_invaders'] = 0

                # Check if hovering over brick breaker button
                if is_hover(index_pos, brick_breaker_button_center, circle_radius):
                    if hover_start_time['brick_breaker'] == 0:
                        hover_start_time['brick_breaker'] = time.time()
                    elif time.time() - hover_start_time['brick_breaker'] >= HOVER_DELAY:
                        play_sound('./apps/app_3/game_start.mp3')
                        brick_breaker(screen, camera_manager, SCREEN_SIZE)
                        return
                else:
                    hover_start_time['brick_breaker'] = 0

                # Check if hovering over home button
                if is_hover(index_pos, home_button_center, circle_radius):
                    if hover_start_time['home'] == 0:
                        hover_start_time['home'] = time.time()
                    elif time.time() - hover_start_time['home'] >= HOVER_DELAY:
                        play_sound('audio/back.wav')
                        running = False
                else:
                    hover_start_time['home'] = 0

        screen.fill(BLACK)

        # Draw Space Invaders button with white circle overlay
        screen.blit(space_invaders_img, (space_invaders_button_center[0] - circle_radius, 
                                        space_invaders_button_center[1] - circle_radius))
        pygame.draw.circle(screen, WHITE, space_invaders_button_center, circle_radius, 5)  # White overlay circle

        # Draw Brick Breaker button with white circle overlay
        screen.blit(brick_breaker_img, (brick_breaker_button_center[0] - circle_radius, 
                                        brick_breaker_button_center[1] - circle_radius))
        pygame.draw.circle(screen, WHITE, brick_breaker_button_center, circle_radius, 5)  # White overlay circle

        # Draw Home button with text and white circle overlay
        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, circle_radius)
        pygame.draw.circle(screen, WHITE, home_button_center, circle_radius, 5)  # White overlay circle
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(50)
