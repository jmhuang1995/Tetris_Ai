from tetris import check_collision, COLS, join_matrices, rotate_clockwise
import halgo
from collections import namedtuple

Action = namedtuple('Move', ['x_position', 'rotation', 'result'])

class Player_AI(object):
    def __init__(self, tetris):
        self.tetris = tetris
        self.halgo = {
            halgo.blocks_amount: 175,
            halgo.block_avgerage_height: -750,
            halgo.gaps_amount: -20,
            halgo.holes_amount: -500,
            halgo.blocks_above_hole_amount: 900,
            halgo.max_board_height: -750,
        }
        self.instant_play = True

    @staticmethod
    def max_xposition(block):
        return COLS - len(block[0])

    @staticmethod
    def rotation_amount(block):
        blocks = [block]
        while True:
            block = rotate_clockwise(block)
            if block in blocks:
                return len(blocks)
            blocks.append(block)

    def util(self, board):
        return sum([f(board)*weight for (f, weight) in self.halgo.items()])

    def new_board_with_blocks(self,x ,y, block):
        return join_matrices(self.tetris.board, block, (x,y))

    def insert_point(self, x, block):
        y = 0
        while not check_collision(self.tetris.board, block, (x,y)):
            y += 1
        return y -1

    def all_possible_actions(self):
        actions = []
        block = self.tetris.block
        for i in range(Player_AI.rotation_amount(block)):
            for x in range(self.max_xposition(block)+1):
                y = self.insert_point(x, block)
                board = self.new_board_with_blocks(x , y , block)
                actions.append(Action(x, i, board))
            block = rotate_clockwise(block)
        return actions

    def most_efficient_action(self):
        return max(self.all_possible_actions(), key=lambda a: self.util(a.result))

    def do_action(self):
        tetris = self.tetris
        action = self.most_efficient_action()
        tetris.lock.acquire()

        for i in range(action.rotation):
            tetris.block = rotate_clockwise(tetris.block)
        tetris.move_to(action.x_position)
        if self.instant_play:
            tetris.block_y = self.insert_point(action.x_position, tetris.block)
        tetris.lock.release()




