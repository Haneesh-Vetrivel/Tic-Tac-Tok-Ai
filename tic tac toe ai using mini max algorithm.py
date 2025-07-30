import sys
import pygame
import numpy as np

pygame.init()

# Colors and sizes
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

WIDTH = 600
HEIGHT = 700
LINE_WIDTH = 10
WIN_LINE_WIDTH = 10
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe AI')
screen.fill(WHITE)

symbol_font = pygame.font.Font(None, 200)
title_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 40)

# Load win sound
try:
    win_sound = pygame.mixer.Sound("win_sound.wav")
except pygame.error:
    win_sound = None
    print("Warning: win_sound.wav not found or cannot be loaded.")

# Game state
board = np.zeros((BOARD_ROWS, BOARD_COLS))
player_choice = None
ai_choice = None
start_screen = True
show_symbol_selection = False
choose_first = False
player = 1
game_over = False
win_line = None
win_color = None
just_restarted = False

start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 35, 200, 70)


def draw_button(rect, text, color=WHITE):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    text_surface = small_font.render(text, True, BLACK)
    screen.blit(text_surface, (rect.x + rect.width // 2 - text_surface.get_width() // 2,
                                rect.y + rect.height // 2 - text_surface.get_height() // 2))


def draw_start_screen():
    screen.fill(WHITE)
    title_text = title_font.render("Welcome to Tic Tac Toe!", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    draw_button(start_button, "Start Game", LIGHT_BLUE)
    pygame.display.update()


def draw_symbol_selection_screen():
    screen.fill(WHITE)
    text = title_font.render('Choose your symbol:', True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

    global x_button, o_button
    x_button = pygame.Rect(WIDTH // 4 - 75, 200, 150, 70)
    o_button = pygame.Rect(WIDTH * 3 // 4 - 75, 200, 150, 70)

    draw_button(x_button, 'X', LIGHT_BLUE)
    draw_button(o_button, 'O', LIGHT_BLUE)
    pygame.display.update()


def draw_first_second_screen():
    screen.fill(WHITE)
    text = title_font.render('Choose turn order:', True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

    global first_button, second_button
    first_button = pygame.Rect(WIDTH // 4 - 75, 200, 150, 70)
    second_button = pygame.Rect(WIDTH * 3 // 4 - 75, 200, 150, 70)

    draw_button(first_button, 'First', LIGHT_BLUE)
    draw_button(second_button, 'Second', LIGHT_BLUE)
    pygame.display.update()


def draw_lines(color=BLACK):
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, color, (0, SQUARE_SIZE * i), (WIDTH, SQUARE_SIZE * i), LINE_WIDTH)
        pygame.draw.line(screen, color, (SQUARE_SIZE * i, 0), (SQUARE_SIZE * i, WIDTH), LINE_WIDTH)


def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            val = board[row][col]
            if val == player_choice:
                symbol = 'O' if player_choice == 1 else 'X'
            elif val == ai_choice:
                symbol = 'O' if ai_choice == 1 else 'X'
            else:
                continue
            text_surface = symbol_font.render(symbol, True, BLACK)
            text_rect = text_surface.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                      row * SQUARE_SIZE + SQUARE_SIZE // 2))
            screen.blit(text_surface, text_rect)


def draw_game_over_message():
    if is_board_full() and not check_win(player_choice) and not check_win(ai_choice):
        message = "It's a Draw!"
    elif check_win(player_choice):
        message = "You Win!"
    elif check_win(ai_choice):
        message = "AI Wins!"
    else:
        return  # no message

    text = title_font.render(message, True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, WIDTH + 20))


def mark_square(row, col, player):
    board[row][col] = player


def available_square(row, col):
    return board[row][col] == 0


def is_board_full(check_board=board):
    return np.all(check_board != 0)


def check_win(player, check_board=board, update_line=True):
    global win_line
    line = None

    for col in range(BOARD_COLS):
        if all(check_board[row][col] == player for row in range(3)):
            line = ('vertical', col * SQUARE_SIZE + SQUARE_SIZE // 2)
            break
    for row in range(BOARD_ROWS):
        if all(check_board[row][col] == player for col in range(3)):
            line = ('horizontal', row * SQUARE_SIZE + SQUARE_SIZE // 2)
            break
    if all(check_board[i][i] == player for i in range(3)):
        line = ('desc_diag', None)
    if all(check_board[i][2 - i] == player for i in range(3)):
        line = ('asc_diag', None)

    if line and update_line:
        win_line = line

    return line is not None


def draw_win_line(color):
    if win_line and color:
        if win_line[0] == 'vertical':
            x = win_line[1]
            pygame.draw.line(screen, color, (x, 0), (x, WIDTH), WIN_LINE_WIDTH)
        elif win_line[0] == 'horizontal':
            y = win_line[1]
            pygame.draw.line(screen, color, (0, y), (WIDTH, y), WIN_LINE_WIDTH)
        elif win_line[0] == 'desc_diag':
            pygame.draw.line(screen, color, (0, 0), (WIDTH, WIDTH), WIN_LINE_WIDTH)
        elif win_line[0] == 'asc_diag':
            pygame.draw.line(screen, color, (0, WIDTH), (WIDTH, 0), WIN_LINE_WIDTH)


def minimax(minimax_board, depth, is_maximizing):
    if check_win(ai_choice, minimax_board, update_line=False):
        return 1
    elif check_win(player_choice, minimax_board, update_line=False):
        return -1
    elif is_board_full(minimax_board):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for row in range(3):
            for col in range(3):
                if minimax_board[row][col] == 0:
                    minimax_board[row][col] = ai_choice
                    score = minimax(minimax_board, depth + 1, False)
                    minimax_board[row][col] = 0
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for row in range(3):
            for col in range(3):
                if minimax_board[row][col] == 0:
                    minimax_board[row][col] = player_choice
                    score = minimax(minimax_board, depth + 1, True)
                    minimax_board[row][col] = 0
                    best_score = min(score, best_score)
        return best_score


def best_move():
    best_score = -float('inf')
    move = (-1, -1)
    for row in range(3):
        for col in range(3):
            if board[row][col] == 0:
                board[row][col] = ai_choice
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    move = (row, col)

    if move != (-1, -1):
        mark_square(move[0], move[1], ai_choice)
        return True
    return False


def restart_game_full():
    global board, win_line, game_over, player, player_choice, ai_choice
    global start_screen, choose_first, show_symbol_selection, win_color, just_restarted
    board = np.zeros((3, 3))
    win_line = None
    win_color = None
    game_over = False
    player = 1
    player_choice = None
    ai_choice = None
    start_screen = True
    choose_first = False
    show_symbol_selection = False
    just_restarted = True
    screen.fill(WHITE)
    draw_lines()
    pygame.display.update()


# Game loop
draw_lines()

while True:
    if start_screen:
        draw_start_screen()
    elif show_symbol_selection:
        draw_symbol_selection_screen()
    elif choose_first:
        draw_first_second_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if start_screen and event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                start_screen = False
                show_symbol_selection = True

        elif show_symbol_selection and event.type == pygame.MOUSEBUTTONDOWN:
            if x_button.collidepoint(event.pos):
                player_choice = 2
                ai_choice = 1
                show_symbol_selection = False
                choose_first = True
            elif o_button.collidepoint(event.pos):
                player_choice = 1
                ai_choice = 2
                show_symbol_selection = False
                choose_first = True

        elif choose_first and event.type == pygame.MOUSEBUTTONDOWN:
            if first_button.collidepoint(event.pos):
                player = player_choice
                choose_first = False
                screen.fill(WHITE)
                draw_lines()
            elif second_button.collidepoint(event.pos):
                player = ai_choice
                choose_first = False
                screen.fill(WHITE)
                draw_lines()
                best_move()
                player = player % 2 + 1

        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouseX = event.pos[0] // SQUARE_SIZE
            mouseY = event.pos[1] // SQUARE_SIZE
            if available_square(mouseY, mouseX):
                mark_square(mouseY, mouseX, player)
                if check_win(player):
                    game_over = True
                    win_color = GREEN if player == player_choice else RED
                    if win_sound:
                        win_sound.play()
                player = player % 2 + 1

                if not game_over and player == ai_choice:
                    if best_move() and check_win(ai_choice):
                        game_over = True
                        win_color = RED
                        if win_sound:
                            win_sound.play()
                    player = player % 2 + 1

                if not game_over and is_board_full():
                    game_over = True
                    win_color = GRAY

    if not (start_screen or show_symbol_selection or choose_first):
        if just_restarted:
            just_restarted = False
        else:
            screen.fill(WHITE)
            draw_lines()
            draw_figures()
            if game_over:
                draw_win_line(win_color)
                draw_game_over_message()

    pygame.display.update()
