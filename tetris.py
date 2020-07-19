import pygame
import numpy as np
import random
import sys

# creating the data structure for pieces
# setting up global vars
# functions
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape in main
# - setting up the main

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.init()

# GLOBALS VARS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # meaning 300 // 10 = 30 width per block
PLAY_HEIGHT = 600  # meaning 600 // 20 = 20 height per block
BRICK_SIZE = 30
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT
START_POINT = (TOP_LEFT_X + PLAY_WIDTH/2, TOP_LEFT_Y - 2 * BRICK_SIZE)

# FPS Value
fps = 30
frames = pygame.time.Clock()



# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ROTATION MATRIX
mat_rot = ([0, -1], [1, 0])

# SHAPE FORMATS

z_shape = [(0, 0), (0, -1), (1, -1), (-1, 0)]

s_shape = [(0, 0), (-1, 0), (0, 1), (1, 1)]

i_shape = [(0, 1), (1, 1), (-1, 1), (-2, 1)]

#fixme Probar como gira el cuadrado
o_shape = [(0, 0), (-1, 0), (-1, 1), (0, 1)]

j_shape = [(0, 0), (-1, 0), (0, 1), (0, 2)]

l_shape = [(0, 0), (1, 0), (0, 1), (0, 2)]

t_shape = [(0, 0), (1, 0), (-1, 0), (0, 1)]

shapes_map = [z_shape, s_shape, i_shape, o_shape, j_shape, l_shape, t_shape]

for dot in o_shape:
    tuple(np.dot(mat_rot, dot))


S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',

      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Brick(pygame.sprite.Sprite):
    def __init__(self, shape, color):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/brick_lb.png'), (BRICK_SIZE, BRICK_SIZE))
        self.surface = pygame.Surface((BRICK_SIZE, BRICK_SIZE))
        self.rot_pos = (shape[0], shape[1])
        self.rect = self.surface.get_rect(topleft=(shape[0] * BRICK_SIZE + START_POINT[0], shape[1] * BRICK_SIZE + START_POINT[1]))
        self.surface.fill(WHITE)

    def rotate(self):
        final_rot = np.dot(mat_rot, self.rot_pos)
        move = (final_rot - self.rot_pos)
        self.rot_pos = final_rot
        self.rect.move_ip(move[0] * BRICK_SIZE, move[1] * BRICK_SIZE)

    def move(self, mov):
        self.rect.move_ip(mov, 0)


    def fall(self):
        self.rect.move_ip(0, BRICK_SIZE)


def get_new_piece():
    return [Brick(brick, WHITE) for brick in random.choice(shapes_map)]


def collision(active_piece, static_bricks, check_side):
    for brick in active_piece:
        if pygame.sprite.spritecollideany(brick, static_bricks, collided=check_side):
            return True
    return False


def collided_brick_y(b1, b2):
    return b1.rect.bottomleft == b2.rect.topleft or b1.rect.bottom >= (TOP_LEFT_Y + PLAY_HEIGHT)


def collided_brick_x_left(b1, b2):
    return b1.rect.topleft == b2.rect.topright or b1.rect.left <= TOP_LEFT_X


def collided_brick_x_right(b1, b2):
    return b1.rect.topright == b2.rect.topleft or b1.rect.right >= TOP_LEFT_X + PLAY_WIDTH


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    format_shape = convert_shape_format(shape)
    for pos in format_shape:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('Calibri', size, italic=True)
    label = font.render(text, 1, color)

    surface.blit(label,
                 (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))


def draw_grid(surface, grid):
    start_x = TOP_LEFT_X
    start_y = TOP_LEFT_Y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128),
                         (start_x, start_y+i*BRICK_SIZE), (start_x + PLAY_WIDTH, start_y+i*BRICK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128),
                             (start_x + j * BRICK_SIZE, start_y), (start_x + j * BRICK_SIZE, start_y + PLAY_HEIGHT))


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if(0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + inc)
                locked[new_key] = locked.pop(key)

    return inc

def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.SysFont('Calibri', 50)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))

    font = pygame.font.SysFont('Calibri', 25)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))

    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100

    surface.blit(label, (sx + 10, sy + 200))

    #for i in range(len(grid)):
    #    for j in range(len(grid[i])):
    #        pygame.draw.rect(surface, grid[i][j],
    #                         (TOP_LEFT_X + j*BRICK_SIZE, TOP_LEFT_Y + i*BRICK_SIZE, BRICK_SIZE, BRICK_SIZE), 0)
    #
    #pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    draw_grid(surface, grid)


def main(win, high_score):
    locked_positions = {}
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0
    active_sprites = pygame.sprite.Group()
    static_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    new_piece = get_new_piece()
    next_piece = get_new_piece()
    active_sprites.add(new_piece)
    all_sprites.add(new_piece, next_piece)
    static_sprites.add(next_piece)

    while run:
        grid = create_grid(locked_positions)
        fall_time += frames.get_rawtime()
        level_time += frames.get_rawtime()
        frames.tick()

        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.01

        if fall_time/1000 > fall_speed:
            fall_time = 0
            need_piece = collision(active_sprites, static_sprites, collided_brick_y)
            if need_piece:
                static_sprites.add(new_piece)
                active_sprites.remove(new_piece)
                new_piece = next_piece
                static_sprites.remove(next_piece)
                next_piece = get_new_piece()
                active_sprites.add(new_piece)
                all_sprites.add(new_piece)
            else:
                for brick in active_sprites:
                    brick.fall()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not (collision(active_sprites, static_sprites, collided_brick_x_left)):
                        for brick in active_sprites:
                            brick.move(-BRICK_SIZE)
                if event.key == pygame.K_RIGHT:
                    if not (collision(active_sprites, static_sprites, collided_brick_x_right)):
                        for brick in active_sprites:
                            brick.move(BRICK_SIZE)
                # if event.key == pygame.K_DOWN:
                if event.key == pygame.K_UP:
                    for brick in active_sprites:
                        brick.rotate()

        draw_window(win, grid, score)

        for brick in all_sprites:
            win.blit(brick.image, brick.rect)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, f'You Lost! Score: {score}', 75, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            #update_scores(score, high_score)


def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        #with open('scores.txt', 'r') as fl:
        #    lines = fl.readlines()
        #    high_score = lines[0].strip()
        draw_text_middle(win, f'Press any key to play.', 50, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win, 0)
    pygame.quit()
    sys.exit()


def update_scores(actual_score, score):
    with open('scores.txt', 'w') as fl:
        if actual_score > int(score):
            fl.write(str(actual_score))


win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
main_menu(win)
