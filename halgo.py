def empty_(cell):
    return cell == 0


def blocked_(cell):
    return cell != 0


def blocks_amount(board):
    i = 0
    for row in board:
        for cell in row:
            if blocked_(cell):
                i += 1
    return i


def max_board_height(board):
    for idx, row in enumerate(board):
        for cell in row:
            if blocked_(cell):
                return len(board) - idx - 1


def block_avgerage_height(board):
    block_total_height = 0
    for height, row in enumerate(reversed(board[1:])):
        for cell in row:
            if blocked_(cell):
                block_total_height += height
    return block_total_height / blocks_amount(board)


def find_holes(board):
    holes = []
    blocks_in_colunm = False
    for x in range(len(board[0])):
        for y in range(len(board)):
            if blocks_in_colunm and empty_(board[y][x]):
                holes.append((x,y))
            elif blocked_(board[y][x]):
                blocks_in_colunm = True
        blocks_in_colunm = False
    return holes


def holes_amount(board):
    return len(find_holes(board))


def blocks_above_hole_amount(board):
    i = 0
    for hole_x, hole_y in find_holes(board):
        for y in range(hole_y-1, 0, -1):
            if blocked_(board[y][hole_x]):
                i += 1
            else:
                break
    return i


def gaps_amount(board):

    gaps = []
    sequence = 0
    board_copy = []

    for y in range(len(board)):
        board_copy.append([1] + board[y] + [1])

        #find gaps
        for y in range(len(board_copy)):
            for x in range(len(board_copy[0])):
                if sequence == 0 and blocked_(board_copy[y][x]):
                    sequence = 1
                elif sequence == 1 and empty_(board_copy[y][x]):
                    sequence = 2
                elif sequence == 2:
                    if blocked_(board_copy[y][x]):
                         gaps.append(board_copy[y][x - 1])
                         sequence = 1
                    else:
                         sequence = 0

    return len(gaps)






