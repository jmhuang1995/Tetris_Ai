from copy import deepcopy
from random import randrange
from threading import Lock

import pygame
import sys

# Config
CELL_SIZE = 20
COLS = 10
ROWS = 22
MAX_FPS = 20
DROP_TIME = 15
DRAW = True

COLORS = [
    (0, 0, 0),
    ( 184, 15, 238),
    (100, 200, 115),
    (255, 85, 85),
    ( 226, 249, 98),
    (255, 87, 51),
    ( 37, 250, 4),
    (14, 160, 238),
    ( 4, 60, 250)
]

BLOCKS = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(COLS)]] + board


def join_matrices(mat1, mat2, mat2_off):
    mat3 = deepcopy(mat1)
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat3[cy + off_y - 1][cx + off_x] += val
    return mat3


def new_board():
    board = [[0 for x in range(COLS)] for y in range(ROWS)]
    board += [[1 for x in range(COLS)]]
    return board


class TetrisApp(object):
    def __init__(self, runner=None):
        self.DROPEVENT = pygame.USEREVENT + 1

        pygame.init()
        pygame.display.set_caption("Tetris_AI")
        pygame.key.set_repeat(250, 25)
        self.width = CELL_SIZE * (COLS + 10)
        self.height = CELL_SIZE * ROWS
        self.rlim = CELL_SIZE * COLS
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(COLS)] for y in range(ROWS)]
        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 11)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.next_block = BLOCKS[randrange(len(BLOCKS))]
        self.gameover = False
        self.runner = runner
        self.player_ai = None
        self.lock = Lock()
        self.init_game()

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def ai_toggle(self):
        if self.player_ai:
            self.player_ai.instant_play = not self.player_ai.instant_play

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    try:
                        pygame.draw.rect(self.screen, COLORS[val],
                                         pygame.Rect((off_x + x) * CELL_SIZE, (off_y + y) * CELL_SIZE, CELL_SIZE,
                                                     CELL_SIZE), 0)
                    except IndexError:
                        print("Corrupted board")
                        print(self.board)

    def run(self):
        key_actions = {
            'ESCAPE': sys.exit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': self.drop,
            'UP': self.rotate_block,
            'SPACE': self.start_game,
            'RETURN': self.insta_drop,
            'p': self.ai_toggle,
        }

        clock = pygame.time.Clock()
        while True:
            if DRAW:
                self.screen.fill((0, 0, 0))
                if self.gameover:
                    self.center_msg("Game Over!\nYour score: %d\nPress space to continue" % self.score)
                else:
                    pygame.draw.line(self.screen, (255, 255, 255),
                                     (self.rlim + 1, 0), (self.rlim + 1, self.height - 1))
                    self.disp_msg("Next:", (self.rlim + CELL_SIZE, 2))
                    self.disp_msg("Score: %d" % self.score, (self.rlim + CELL_SIZE, CELL_SIZE * 5))
                    if self.player_ai and self.runner:
                        from halgo import holes_amount, blocks_above_hole_amount, gaps_amount, max_board_height, block_avgerage_height, \
                            blocks_amount
                        chrom = self.runner.population[self.runner.current_chromosome]
                        self.disp_msg("Discontentment: %d" % -self.player_ai.util(self.board),
                                      (self.rlim + CELL_SIZE, CELL_SIZE * 10))
                        self.disp_msg("Generation: %s" % self.runner.current_generation,
                                      (self.rlim + CELL_SIZE, CELL_SIZE * 11))
                        self.disp_msg("Chromosome: %d" % chrom.name, (self.rlim + CELL_SIZE, CELL_SIZE * 12))
                        self.disp_msg("\n  %s: %s\n  %s: %s\n  %s: %s\n  %s: %s\n  %s: %s\n  %s: %s" % (
                            "num_holes", chrom.halgo[holes_amount],
                            "num_blocks_above_holes", chrom.halgo[blocks_above_hole_amount],
                            "num_gaps", chrom.halgo[gaps_amount],
                            "max_height", chrom.halgo[max_board_height],
                            "avg_height", chrom.heuristics[block_avgerage_height],
                            "num_blocks", chrom.heuristics[blocks_amount],
                        ), (self.rlim + CELL_SIZE, CELL_SIZE * 12.1))
                    self.draw_matrix(self.bground_grid, (0, 0))
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.block, (self.block_x, self.block_y))
                    self.draw_matrix(self.next_block, (COLS + 1, 2))
                pygame.display.update()

            for event in pygame.event.get():
                if event.type == self.DROPEVENT:
                    self.drop()
                elif event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()

            clock.tick(MAX_FPS)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(self.default_font.render(line, False, (255, 255, 255), (0, 0, 0)), (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    def new_block(self):
        self.block = self.next_block
        self.next_block = BLOCKS[randrange(len(BLOCKS))]
        self.block_x = COLS // 2 - len(self.block[0]) // 2
        self.block_y = 0
        self.score += 1

        if check_collision(self.board, self.block, (self.block_x, self.block_y)):
            self.gameover = True
            if self.runner:
                self.runner.on_game_over(self.score)

    def init_game(self):
        self.board = new_board()
        self.score = 0
        self.new_block()
        pygame.time.set_timer(self.DROPEVENT, DROP_TIME)


    def add_cl_lines(self, n):
        linescores = [0, 50, 100, 200, 1000]
        self.score += linescores[n]

    def rotate_block(self):
        if not self.gameover:
            new_block = rotate_clockwise(self.block)
            if not check_collision(self.board, new_block, (self.block_x, self.block_y)):
                self.block = new_block

    def move_to(self, x):
        self.move(x - self.block_x)

    def move(self, delta_x):
        if not self.gameover:
            new_x = self.block_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > COLS - len(self.block[0]):
                new_x = COLS - len(self.block[0])
            if not check_collision(self.board, self.block, (new_x, self.block_y)):
                self.block_x = new_x

    def drop(self):
        self.lock.acquire()
        if not self.gameover:
            self.block_y += 1
            if check_collision(self.board, self.block, (self.block_x, self.block_y)):
                self.board = join_matrices(self.board, self.block, (self.block_x, self.block_y))
                self.new_block()
                cleared_rows = 0
                for i, row in enumerate(self.board[:-1]):
                    if 0 not in row:
                        self.board = remove_row(self.board, i)
                        cleared_rows += 1
                self.add_cl_lines(cleared_rows)

                self.lock.release()
                if self.player_ai:
                    self.player_ai.do_action()

                return True
        self.lock.release()
        return False

    def insta_drop(self):
        if not self.gameover:
            while not self.drop():
                pass

if __name__ == "__main__":
    from player_ai import Player_AI

    app = TetrisApp()
    app.player_ai = Player_AI(app)
    app.player_ai.instant_play = False
    app.run()
