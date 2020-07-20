import pygame
import numpy as np
import random
import sys

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
"""

pygame.init()

# GLOBALS VARS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # meaning 300 // 10 = 30 width per block
PLAY_HEIGHT = int(PLAY_WIDTH * 2)  # meaning 600 // 20 = 20 height per block
BRICK_SIZE = int(PLAY_WIDTH/10)  # or PLAY_HEIGHT/20
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

# SHAPES
z_shape = [(0, 0), (0, -1), (1, -1), (-1, 0)]

s_shape = [(0, 0), (-1, 0), (0, 1), (1, 1)]

i_shape = [(0, 1), (1, 1), (-1, 1), (-2, 1)]

#fixme Probar como gira el cuadrado
o_shape = [(0, 0), (-1, 0), (-1, 1), (0, 1)]

j_shape = [(0, 0), (-1, 0), (0, 1), (0, 2)]

l_shape = [(0, 0), (1, 0), (0, 1), (0, 2)]

t_shape = [(0, 0), (1, 0), (-1, 0), (0, 1)]

shapes_map = [z_shape, s_shape, i_shape, o_shape, j_shape, l_shape, t_shape]


class Brick(pygame.sprite.Sprite):
    def __init__(self, shape, color, pos=(0, 0)):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/brick_lb.png'), (BRICK_SIZE, BRICK_SIZE))
        self.surface = pygame.Surface((BRICK_SIZE, BRICK_SIZE))
        self.rot_pos = (shape[0], shape[1])
        self.rect = self.surface.get_rect(topleft=(shape[0] * BRICK_SIZE + START_POINT[0] + pos[0], shape[1] * BRICK_SIZE + START_POINT[1] + pos[1]))
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


def get_new_piece(pos=(0, 0)):
    return [Brick(brick, WHITE, pos) for brick in random.choice(shapes_map)]


def collision(active_piece, static_bricks, check_side):
    return pygame.sprite.groupcollide(active_piece, static_bricks, False, False, collided=check_side)


def collided_brick_y(b1, b2):
    return b1.rect.bottomleft == b2.rect.topleft or b1.rect.bottom >= (TOP_LEFT_Y + PLAY_HEIGHT)


def collided_brick_x_left(b1, b2):
    return b1.rect.topleft == b2.rect.topright or b1.rect.left <= TOP_LEFT_X


def collided_brick_x_right(b1, b2):
    return b1.rect.topright == b2.rect.topleft or b1.rect.right >= TOP_LEFT_X + PLAY_WIDTH


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('Calibri', size, italic=True)
    label = font.render(text, 1, color)

    surface.blit(label,
                 (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))



def draw_window(surface, score=0):
    surface.fill(WHITE)
    pygame.font.init()
    font = pygame.font.SysFont('Calibri', 50)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))

    font = pygame.font.SysFont('Calibri', 25)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))

    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100

    surface.blit(label, (sx + 10, sy + 200))

    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)


def change_piece(active_sprites, static_sprites, all_sprites, next_sprites):
    static_sprites.add(active_sprites.sprites())
    active_sprites.empty()

    next_piece = next_sprites.sprites()
    for b in next_piece:
        b.rect.move_ip(-250, -150)
    static_sprites.remove(next_piece)
    active_sprites.add(next_piece)
    next_sprites.empty()

    new_piece = get_new_piece(pos=(250, 150))
    next_sprites.add(new_piece)
    all_sprites.add(new_piece)


def rotate_piece(active_bricks, static_bricks, i=1):
    if i > 4:
        return

    for brick in active_bricks:
        brick.rotate()

    if pygame.sprite.groupcollide(active_bricks, static_bricks, False, False) or check_invalid_terrain(active_bricks):
        rotate_piece(active_bricks, static_bricks, i + 1)
    else:
        return


def check_invalid_terrain(active_bricks):
    for brick in active_bricks:
        if brick.rect.left < TOP_LEFT_X or brick.rect.right > TOP_LEFT_X + PLAY_WIDTH:
            return True

    return False


def check_lines(static_bricks):
    lines = False
    last_line = False
    sorted_bricks = sorted(static_bricks, key=lambda b: b.rect.top)
    for i in range(sorted_bricks[0].rect.top, TOP_LEFT_Y + PLAY_HEIGHT, BRICK_SIZE):
        bricks_in_same_y = list(filter(lambda b: b.rect.top == i, sorted_bricks))
        if len(bricks_in_same_y) >= PLAY_WIDTH / BRICK_SIZE:
            lines += 1
            last_line = i
            for b in bricks_in_same_y:
                b.kill()

    if lines:
        bricks_floating = list(filter(lambda b: b.rect.top < last_line, static_bricks))
        for b_float in bricks_floating:
            b_float.rect.move_ip(0, BRICK_SIZE*lines)

    return lines


def main(win, high_score):
    locked_positions = {}
    run = True
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    active_sprites = pygame.sprite.Group()
    static_sprites = pygame.sprite.Group()
    next_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    current_piece = get_new_piece()
    active_sprites.add(current_piece)

    next_piece = get_new_piece(pos=(+250, +150))
    next_sprites.add(next_piece)
    static_sprites.add(next_piece)

    all_sprites.add(current_piece, next_piece)

    while run:
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
                change_piece(active_sprites, static_sprites, all_sprites, next_sprites)
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
                    rotate_piece(active_sprites, static_sprites)

        draw_window(win, score)

        check_lines(static_sprites)
        all_sprites.draw(win)
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
