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

# SHAPES with his Color (Sprite img)
z_shape = ([(0, 0), (0, -1), (1, -1), (-1, 0)], 'brick_r.png')

s_shape = ([(0, 0), (-1, 0), (0, 1), (1, 1)], 'brick_g.png')

i_shape = ([(0, 1), (1, 1), (-1, 1), (-2, 1)], 'brick_c.png')

#fixme Probar como gira el cuadrado
o_shape = ([(0, 0), (-1, 0), (-1, 1), (0, 1)], 'brick_y.png')

j_shape = ([(0, 0), (-1, 0), (-1, 1), (1, 0)], 'brick_b.png')

l_shape = ([(0, 0), (1, 0), (1, 1), (-1, 0)], 'brick_o.png')

t_shape = ([(0, 0), (1, 0), (-1, 0), (0, 1)], 'brick_v.png')

shapes_map = [z_shape, s_shape, i_shape, o_shape, j_shape, l_shape, t_shape]

# POINTS
points = [100, 400, 900, 2000]
point_multi = [1, 2, 2, 3, 3, 4, 4, 5]


class Brick(pygame.sprite.Sprite):
    def __init__(self, shape, color, pos=(0, 0)):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(f'img/bola.png'), (BRICK_SIZE, BRICK_SIZE))
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
        shape = random.choice(shapes_map)
        shape = [Brick(brick, shape[1], pos) for brick in shape[0]]
        self.add(shape)

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
        self.image = pygame.transform.scale(pygame.image.load('img/bgtry.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.surface.get_rect(topleft=(0, 0))
        self.surface.fill(WHITE)


class Playfield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/bgtry.png'), (PLAY_WIDTH, PLAY_HEIGHT + int(BRICK_SIZE/2)))
        self.surface = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT))
        self.rect = self.surface.get_rect(topleft=(TOP_LEFT_X, TOP_LEFT_Y))


class Level:
    def __init__(self, number=1, points_multi=1, lines_beat=10, gravity=48):
        self.gravity = gravity
        self.points_multi = points_multi
        self.lines_beat = lines_beat
        self.number = number

    def increment(self, line_beat=10):
        if self.gravity > 1:
            if self.number < 8:
                self.gravity = self.gravity - 5
            elif self.number == 8:
                self.gravity = self.gravity - 2
            else:
                self.gravity = self.gravity - 1
        self.lines_beat = line_beat
        self.number += self.number
        if self.number < 8:
            self.points_multi = point_multi[self.number-1]
        else:
            self.points_multi = point_multi[-1]

    def check_beat_level(self, total_lines):
        if total_lines >= (self.number-1) * 10 + self.lines_beat:
            self.increment()


def check_lost(static_bricks):
    for b in static_bricks:
        if b.rect.top <= TOP_LEFT_Y:
            return True
    return False


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('Calibri', size, italic=True)
    label = font.render(text, 1, color)

    surface.blit(label,
                 (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))


def draw_info(surface, total_lines, level, score=0):
    surface.fill(BLACK)
    pygame.font.init()

    font = pygame.font.Font('font/Tetris.ttf', 25)
    label_score = font.render(f'Score: {score}', 1, (255, 255, 255))
    label_next = font.render('Next Piece', 1, (255, 255, 255))
    label_lines = font.render(f'Lines: {total_lines}', 1, (255, 255, 255))
    label_level = font.render(f'Level: {level.number}', 1, (255, 255, 255))

    surface.blit(label_score, (DISPLAY_INFO_START[0], DISPLAY_INFO_START[1] + ((TOP_LEFT_Y+PLAY_HEIGHT)*0.5)))
    surface.blit(label_next, (DISPLAY_INFO_START[0], DISPLAY_INFO_START[1] - 30))
    surface.blit(label_lines, (TOP_LEFT_X - 175, DISPLAY_INFO_START[1] + (TOP_LEFT_Y+PLAY_HEIGHT)*0.5))
    surface.blit(label_level, (TOP_LEFT_X - 175, DISPLAY_INFO_START[1] + (TOP_LEFT_Y+PLAY_HEIGHT)*0.75))


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
    sorted_bricks = sorted(static_bricks, key=lambda b: b.rect.top)
    for i in range(sorted_bricks[0].rect.top, TOP_LEFT_Y + PLAY_HEIGHT, BRICK_SIZE):
        bricks_in_same_y = list(filter(lambda b: b.rect.top == i and b.rect.right <= TOP_LEFT_X + PLAY_WIDTH and b.rect.left >= TOP_LEFT_X, sorted_bricks))
        if len(bricks_in_same_y) >= PLAY_WIDTH / BRICK_SIZE:
            lines += 1
            last_line = i
            for b in bricks_in_same_y:
                b.kill()

    if lines:
        bricks_floating = list(filter(lambda b: b.rect.top < last_line, static_bricks))
        for b_float in bricks_floating:
            b_float.move(0, BRICK_SIZE*lines)

    return lines


def main(win, high_score):
    run = True
    score = 0
    elapsed_frames = 0
    total_lines = 0

    playfield = Playfield()
    level = Level()

    static_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    current_piece = Piece()

    next_piece = Piece(pos=(DISPLAY_INFO_START[0] - START_POINT[0] + 60, DISPLAY_INFO_START[1] - START_POINT[1] + 25))
    static_sprites.add(next_piece)

    all_sprites.add(current_piece.sprites(), next_piece.sprites())

    soft_drop_active = False

    while run:
        frames.tick(fps)
        elapsed_frames += 1
        lines_done = False

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
                    score += dropped_lines * 2 * level.points_multi
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop_active = False

        if soft_drop_active:
            if not (current_piece.collision(static_sprites, Piece.collided_brick_y)):
                current_piece.soft_drop()
                score += 1 * level.points_multi

        need_piece = current_piece.collision(static_sprites, Piece.collided_brick_y)
        if need_piece:
            change_piece(current_piece, static_sprites, all_sprites, next_piece)
            lines_done = check_lines(static_sprites)
            if lines_done:
                score += lines_done * level.points_multi
                total_lines += lines_done
                level.check_beat_level(total_lines)

        else:
            if elapsed_frames >= level.gravity:
                elapsed_frames = 0
                current_piece.soft_drop()

        if check_lost(static_sprites):
            run = False

        draw_info(win, total_lines, level, score)
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
