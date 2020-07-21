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
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 50
START_POINT = (TOP_LEFT_X + PLAY_WIDTH/2, TOP_LEFT_Y - 2 * BRICK_SIZE)
DISPLAY_INFO_START = (TOP_LEFT_X + PLAY_WIDTH + 50, TOP_LEFT_Y + 50)

# FPS Value
fps = 60
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

# POINTS
points = [40, 100, 300, 1200]


class Brick(pygame.sprite.Sprite):
    def __init__(self, shape, color, pos=(0, 0)):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/bl_red.jpg'), (BRICK_SIZE, BRICK_SIZE))
        self.surface = pygame.Surface((BRICK_SIZE, BRICK_SIZE))
        self.rot_pos = (shape[0], shape[1])
        self.rect = self.surface.get_rect(topleft=(shape[0] * BRICK_SIZE + START_POINT[0] + pos[0], shape[1] * BRICK_SIZE + START_POINT[1] + pos[1]))
        self.surface.fill(WHITE)

    def rotate(self):
        final_rot = np.dot(mat_rot, self.rot_pos)
        move = (final_rot - self.rot_pos)
        self.rot_pos = final_rot
        self.rect.move_ip(move[0] * BRICK_SIZE, move[1] * BRICK_SIZE)

    def move(self, movx, movy):
        self.rect.move_ip(movx, movy)


class Piece(pygame.sprite.Group):
    def __init__(self, pos=(0, 0)):
        super().__init__()
        self.add([Brick(brick, WHITE, pos) for brick in random.choice(shapes_map)])

    def collision(self, static_bricks, check_side):
        return pygame.sprite.groupcollide(self, static_bricks, False, False, collided=check_side)

    @staticmethod
    def collided_brick_y(b1, b2):
        return b1.rect.bottomleft == b2.rect.topleft or b1.rect.bottom >= (TOP_LEFT_Y + PLAY_HEIGHT)

    @staticmethod
    def collided_brick_x_left(b1, b2):
        return b1.rect.topleft == b2.rect.topright or b1.rect.left <= TOP_LEFT_X

    @staticmethod
    def collided_brick_x_right(b1, b2):
        return b1.rect.topright == b2.rect.topleft or b1.rect.right >= TOP_LEFT_X + PLAY_WIDTH

    def rotate_piece(self, static_bricks, i=1):
        if i > 4:
            return

        for brick in self.sprites():
            brick.rotate()

        if pygame.sprite.groupcollide(self, static_bricks, False, False) or self.check_invalid_terrain():
            self.rotate_piece(static_bricks, i + 1)
        else:
            return

    def soft_drop(self):
        for b in self.sprites():
            b.move(0, BRICK_SIZE)

    def hard_drop(self, static_bricks):
        left_pos_active = dict()
        for b in self.sprites():
            if not (b.rect.left in left_pos_active):
                left_pos_active[b.rect.left] = b.rect.bottom
            elif left_pos_active[b.rect.left] < b.rect.bottom:
                left_pos_active[b.rect.left] = b.rect.bottom

        left_pos_static = dict()
        for b in static_bricks:
            if not (b.rect.left in left_pos_static):
                left_pos_static[b.rect.left] = b.rect.top
            elif left_pos_static[b.rect.left] > b.rect.top:
                left_pos_static[b.rect.left] = b.rect.top

        diff_vector = []
        for active in left_pos_active:
            if active in left_pos_static:
                diff_vector.append(left_pos_static[active] - left_pos_active[active])
            else:
                diff_vector.append(TOP_LEFT_Y + PLAY_HEIGHT - left_pos_active[active])

        drop = min(diff_vector)
        for b in self.sprites():
            b.move(0, drop)

        return int(drop / BRICK_SIZE)

    def check_invalid_terrain(self):
        for brick in self.sprites():
            if brick.rect.left < TOP_LEFT_X or brick.rect.right > TOP_LEFT_X + PLAY_WIDTH:
                return True

        return False


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/bg.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.surface.get_rect(topleft=(0, 0))
        self.surface.fill(WHITE)


class Playfield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.transform.rotate(pygame.image.load('img/play3.png'), 90), (PLAY_WIDTH + 55, PLAY_HEIGHT + 52))
        self.surface = pygame.Surface((PLAY_WIDTH + 55, PLAY_HEIGHT + 52))
        self.rect = self.surface.get_rect(topleft=(TOP_LEFT_X - 27, TOP_LEFT_Y - 20))


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
    surface.fill(BLACK)
    pygame.font.init()

    font = pygame.font.Font('font/Tetris.ttf', 25)
    label_score = font.render(f'Score: {score}', 1, (255, 255, 255))
    label_next = font.render('Next Piece', 1, (255, 255, 255))

    surface.blit(label_score, (DISPLAY_INFO_START[0], DISPLAY_INFO_START[1] + ((TOP_LEFT_Y+PLAY_HEIGHT)*0.50)))
    surface.blit(label_next, DISPLAY_INFO_START)


def change_piece(active_sprites, static_sprites, all_sprites, next_sprites):
    static_sprites.add(active_sprites.sprites())
    active_sprites.empty()

    next_piece = next_sprites.sprites()
    for b in next_piece:
        b.move(-DISPLAY_INFO_START[0] + START_POINT[0] - 60, -DISPLAY_INFO_START[1] + START_POINT[1] - 25)
    static_sprites.remove(next_piece)
    active_sprites.add(next_piece)
    next_sprites.empty()

    new_piece = Piece(pos=(DISPLAY_INFO_START[0] - START_POINT[0] + 60, DISPLAY_INFO_START[1] - START_POINT[1] + 25))
    next_sprites.add(new_piece)
    all_sprites.add(new_piece)


def check_lines(static_bricks):
    lines = False
    last_line = False
    total_points = 0
    sorted_bricks = sorted(static_bricks, key=lambda b: b.rect.top)
    for i in range(sorted_bricks[0].rect.top, TOP_LEFT_Y + PLAY_HEIGHT, BRICK_SIZE):
        bricks_in_same_y = list(filter(lambda b: b.rect.top == i, sorted_bricks))
        if len(bricks_in_same_y) >= PLAY_WIDTH / BRICK_SIZE:
            lines += 1
            last_line = i
            for b in bricks_in_same_y:
                b.kill()

    if lines:
        total_points = points[lines-1]
        bricks_floating = list(filter(lambda b: b.rect.top < last_line, static_bricks))
        for b_float in bricks_floating:
            b_float.move(0, BRICK_SIZE*lines)

    return total_points


def main(win, high_score):
    run = True
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    playfield = Playfield()

    static_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    current_piece = Piece()

    next_piece = Piece(pos=(DISPLAY_INFO_START[0] - START_POINT[0] + 60, DISPLAY_INFO_START[1] - START_POINT[1] + 25))
    static_sprites.add(next_piece)

    all_sprites.add(current_piece.sprites(), next_piece.sprites())

    soft_drop_active = False

    while run:

        fall_time += frames.get_rawtime()
        level_time += frames.get_rawtime()
        frames.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not (current_piece.collision(static_sprites, Piece.collided_brick_x_left)):
                        for brick in current_piece:
                            brick.move(-BRICK_SIZE, 0)
                if event.key == pygame.K_RIGHT:
                    if not (current_piece.collision(static_sprites, Piece.collided_brick_x_right)):
                        for brick in current_piece:
                            brick.move(BRICK_SIZE, 0)
                if event.key == pygame.K_DOWN:
                    soft_drop_active = True
                if event.key == pygame.K_UP:
                    current_piece.rotate_piece(static_sprites)
                if event.key == pygame.K_SPACE:
                    dropped_lines = current_piece.hard_drop(static_sprites)
                    score += dropped_lines * 2
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop_active = False

        if soft_drop_active:
            if not (current_piece.collision(static_sprites, Piece.collided_brick_y)):
                current_piece.soft_drop()
                score += 1

        need_piece = current_piece.collision(static_sprites, Piece.collided_brick_y)
        if need_piece:
            change_piece(current_piece, static_sprites, all_sprites, next_piece)
            score += check_lines(static_sprites)
        else:
            current_piece.soft_drop()

        draw_window(win, score)
        win.blit(playfield.image, playfield.rect)

        all_sprites.draw(win)
        pygame.display.update()


def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        bg = Background()
        win.blit(bg.image, bg.rect)
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
