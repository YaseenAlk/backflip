
ROW_SIZE = 5
COL_SIZE = 5
TOTAL_SQ = ROW_SIZE*COL_SIZE


# Example of a completed valid board:
completed_example = {
    'board': [
        0, 1, 1, 1, 1, 
        1, 3, 1, 1, 1,
        1, 1, 0, 1, 0,
        1, 2, 0, 2, 1,
        3, 0, 1, 1, 0,
    ],
    'num_empty': 0,
    'row_counts': [(4,1),(7,0),(3,2),(6,1),(5,2)],
    'col_counts': [(6,1),(7,1),(3,2),(6,0),(3,2)],
    'level': 1,
}

# Example of an incomplete valid board with 2 possibilities:
incomplete_example = {
    'board': [
        -1, 1, 1, 1, -1, 
        1, 3, 1, 1, 1,
        -1, 1, 0, 1, -1,
        1, 2, 0, 2, 1,
        3, 0, 1, 1, 0,
    ],
    'num_empty': 4,
    'row_counts': [(4,1),(7,0),(3,2),(6,1),(5,2)],
    'col_counts': [(6,1),(7,1),(3,2),(6,0),(3,2)],
    'level': 1,
}

empty_example = {
    'board': [-1]*25,
    'num_empty': 25,
    'row_counts': [(4,1),(7,0),(3,2),(6,1),(5,2)],
    'col_counts': [(6,1),(7,1),(3,2),(6,0),(3,2)],
    'level': 1,
}


STARTING_BOARD = {
    'board': [-1]*25,
    'num_empty': 25,
    'row_counts': [],
    'col_counts': [],
    'level': 1,
}

def check_row_counts(board):
    row_indices = [(i, i+ROW_SIZE-1) for i in range(0, TOTAL_SQ, ROW_SIZE)]
    for i, (start,end) in enumerate(row_indices):
        row = board['board'][start:end+1]
        n_s, n_v = board['row_counts'][i]
        if row.count(0) > n_v or sum(row) > n_s:
            return False

    return True

def check_col_counts(board):
    for i in range(ROW_SIZE):
        col = [board['board'][i+r*ROW_SIZE] for r in range(COL_SIZE)]
        n_s, n_v = board['col_counts'][i]
        if col.count(0) > n_v or sum(col) > n_s:
            return False
    
    return True

LEVEL_TEMPLATES = {
    # indices are (# Voltorbs, # 1s, # 2s, #3s)
    1: [
        (6,15,3,1),
        (6,16,0,3),
        (6,14,5,0),
        (6,15,2,2),
        (6,14,4,1),
    ],

    2: [
        (7,14,1,3),
        (7,12,6,0),
        (7,13,3,2),
        (7,14,0,4),
        (7,12,5,1),
    ],

    3: [
        (8,12,2,3),
        (8,10,7,0),
        (8,11,4,2),
        (8,12,1,4),
        (8,10,6,1),
    ],

    4: [
        (8,11,3,3),
        (8,12,0,5),
        (10,7,8,0),
        (10,8,5,2),
        (10,9,2,4),
    ],

    5: [
        (10,7,7,1),
        (10,8,4,3),
        (10,9,1,5),
        (10,6,9,0),
        (10,7,6,2),
    ],

    6: [
        (10,8,3,4),
        (10,9,0,6),
        (10,6,8,1),
        (10,7,5,3),
        (10,8,2,5),
    ],

    7: [
        (10,6,7,2),
        (10,7,4,4),
        (13,5,1,6),
        (13,2,9,1),
        (10,6,6,3),
    ],

    8: [
        (10,8,0,7),
        (10,5,8,2),
        (10,6,5,4),
        (10,7,2,6),
        (10,5,7,3),
    ],

}

def check_level_info(board):
    # Heuristic 2: Each level selects from a set of template parameters, so we can't deviate from that and still be correct
    # In particular, we know we deviate if our parameters can't work for any template
    layouts = LEVEL_TEMPLATES[board['level']]
    grid = board['board']
    rvol, r1, r2, r3 = grid.count(0), grid.count(1), grid.count(2), grid.count(3)
    for nvol, n1, n2, n3 in layouts:
        if rvol > nvol or \
            r1 > n1 or \
                r2 > n2 or \
                    r3 > n3:
                    continue
        return True
    return False

def check_rules(board):
    rule_funcs = [check_row_counts, check_col_counts, check_level_info]
    return all(rule(board) for rule in rule_funcs)

def copy_board(inp):
    copied_board = inp.copy()
    copied_board['board'] = inp['board'].copy()
    return copied_board


"""
Game board elements
- board: int[25]
    - -1: empty
    - 0: voltorb
    - 1/2/3: 1/2/3
- num_empty: # of unfilled elements, range 0 to 25
- row_counts: tuple(2)[5] ; list of (row_sum, voltorb_sum)
- col_counts: tuple(2)[5] ; list of (col_sum, voltorb_sum)
- level: int, range 1 to 8
"""

def solve(board):
    iters = 0
    freq_dict_list = [{0:0, 1:0, 2:0, 3:0} for _ in range(TOTAL_SQ)]
    def helper(cur_board):
        if cur_board['num_empty'] == 0:
            nonlocal iters
            iters += 1
            for sq_i, sq_v in enumerate(cur_board['board']):
                freq_dict_list[sq_i][sq_v] += 1
            return

        # find the first empty square
        grid = cur_board['board']
        first_empty = grid.index(-1)
        for possibility in [0,1,2,3]:
            grid[first_empty] = possibility
            cur_board['num_empty'] -= 1
            if not check_rules(cur_board):
                # undo
                grid[first_empty] = -1 # technically unnecessary
                cur_board['num_empty'] += 1
                continue

            helper(cur_board)
            #if helper(cur_board):
            #    return True
            
            # undo
            grid[first_empty] = -1 # technically unnecessary
            cur_board['num_empty'] += 1
    
    copied_board = copy_board(board)
    helper(copied_board)
    return iters, freq_dict_list

def update_board(inp, idx, val):
    initial = inp['board'][idx]
    inp['board'][idx] = val
    if initial == -1 and val != -1:
        inp['num_empty'] -= 1
    elif initial != -1 and val == -1:
        inp['num_empty'] += 1

def best_guess(initial, soln):
    iters, freq_dict_list = soln
    empties = [i for i in range(25) if initial['board'][i] == -1]
    probabilities = [freq_dict_list[i][0]/iters for i in empties]
    paired = [(i,j) for i,j in zip(empties, probabilities)]
    return min(paired, key=lambda x: x[1])

if __name__ == "__main__":
    print('Welcome to Backflip')
    working_board = copy_board(STARTING_BOARD)
    
    lvl = int(input("Enter current level: "))
    assert 1 <= lvl <= 8
    working_board['level'] = lvl

    for i in range(COL_SIZE):
        nsum = int(input(f"row {i+1} nsum: "))
        nvol = int(input(f"row {i+1} nvol: "))
        assert 0 <= nsum <= 3*(ROW_SIZE-nvol)
        assert 0 <= nvol <= ROW_SIZE
        working_board['row_counts'].append((nsum, nvol))
    for i in range(ROW_SIZE):
        nsum = int(input(f"col {i+1} nsum: "))
        nvol = int(input(f"col {i+1} nvol: "))
        assert 0 <= nsum <= 3*(COL_SIZE-nvol)
        assert 0 <= nvol <= COL_SIZE
        working_board['col_counts'].append((nsum, nvol))
    
    # Heuristic #1: any row/col with a voltorb count of 0 can be safely cleared
    for i in range(COL_SIZE):
        if working_board['row_counts'][i][1] == 0:
            for j in range(ROW_SIZE):
                idx = i*ROW_SIZE + j
                v = int(input(f"What value do you see at index {idx+1}? (1-indexing): "))
                assert v in [1,2,3]
                update_board(working_board, idx, v)
    for i in range(ROW_SIZE):
        if working_board['col_counts'][i][1] == 0:
            for j in range(COL_SIZE):
                idx = j*ROW_SIZE + i
                v = int(input(f"What value do you see at index {idx+1}? (1-indexing): "))
                assert v in [1,2,3]
                update_board(working_board, idx, v)

    print("Now for other squares you've already tapped.")
    others = input("Enter index,value (row-major 1-indexing) or n if done: ")
    while not others.lower().startswith('n'):
        idx,val = others.split(',')
        idx = int(idx)
        val = int(val)
        assert 1 <= idx <= 25
        assert val in [1,2,3]
        update_board(working_board, idx, val)
        others = input("Enter index,value (row-major 1-indexing) or n if done: ")

    initial_board = copy_board(working_board)
    while working_board['num_empty'] > 0:
        next_guess = best_guess(initial_board, solve(working_board))
        idx, prob = next_guess 
        next_val = input(f"What value do you see at index {idx+1}? (row-major 1-indexing) ({prob*100}% chance of being a voltorb): ")
        val = int(next_val)
        assert(val in [0,1,2,3])
        if val == 0:
            break
        update_board(working_board, idx, val)
        update_board(initial_board, idx, val)
    if working_board['num_empty'] == 0:
        print('Congratulations! You win!')
    else:
        print('Oh no :( Remember this is still a game of luck')