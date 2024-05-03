"""
Sudoku playing functions:
    gen_customized_puzzle(): a wrapper to generate customized Sudoku puzzles
    main_sudoku_play(): main function for player to start a Sudoku game

MIT license
Copyright (c) 2024 ddotplus@github
"""

from sudoku_utility import *
import numpy as np
import random

def gen_customized_puzzle(array_size=9, random_seed=None, difficulty=0.5):
    """ Generate a customized Sudoku puzzle
    Note:
        - defined by: array size, random seed, and difficulty level
        - reproducible, and easy to generate a series of puzzles, e.g.
            array_size = 9
            random_seed = 'my1', 'my2', ..., 'my999'
            difficulty = 0.5
    Input:
        array_size: int, size of Sudoku puzzle array in one dimension
        random_seed: int or string, random seed for puzzle generation
        difficulty: float, in range [0, 1], the larger difficulty,
                    the more empty positions to be filled
    Output:
        c_puzzle: 2D numpy array, a generated puzzle, 0 meaning empty positions
        c_solution: 2D numpy array, full Sudoku array that the puzzle built on
    """
    c_solution = gen_sudoku_full(array_size, random_seed)
    ## define difficulty=1:  remove all possible positions under <random_seed>
    puzzle_max = gen_sudoku_puzzle(c_solution, random_seed=random_seed)
    max_removed_ratio = np.count_nonzero(puzzle_max == 0) / array_size ** 2
    ## generate puzzle for customized difficulty
    removed_ratio = difficulty * max_removed_ratio
    c_puzzle = gen_sudoku_puzzle(c_solution, max_removed_ratio=removed_ratio,
                                 random_seed=random_seed)
    return c_puzzle, c_solution


def main_sudoku_play():
    """ Interface to solve Sudoku puzzle manually
        A complete version that one may play for a while.
    """
    hspace = 10
    print('')
    print(' ' * hspace + '*********************************')
    print(' ' * hspace + '*****  Play Sudoku Puzzle  ******')
    print(' ' * hspace + '*********************************')
    print(' ' * hspace + '  copyright(c)  ddotplus@github')
    print('')
    ## generate a Sudoku puzzle
    ## - choose size of puzzle array
    array_size = 9
    p = input('What puzzle size do you want to play? (4/9/16/25)  ' +
              '[{}]:  '.format(array_size))
    while len(p) > 0 and not (p.isdigit() and int(p) in [4, 9, 16, 25]):
        p = input('  > not one of 4,9,16,25. try again  ' +
                  '[{}]:  '.format(array_size))
    if len(p) > 0:
        array_size = int(p)
    ## - choose seed for puzzle generation
    random_seed = 'try_' + str(random.randint(0, 10000))
    p = input('Give a name or integer for puzzle creation:  ' +
              '["{}"]:  '.format(random_seed))
    if len(p) > 0:
        random_seed = p.strip()
    ## - choose puzzle difficulty
    difficulty = 0.5
    p = input('What level of puzzle difficulty? (range of [0,1])  ' +
              '[{}]:  '.format(difficulty))
    while len(p) > 0 and \
            not (p.replace('.', '').isdigit() and 0 <= float(p) <= 1):
        p = input('  > not in range of [0,1]. try again  ' +
                  '[{}]:  '.format(difficulty))
    if len(p) > 0:
        difficulty = float(p)

    n_dash = 66                      ## for print banner of each new run
    try_again = 1
    while try_again > 0:
        print('-' * n_dash)
        if try_again == 2:  ## update random_seed by automatic increment
            seed_name = random_seed
            seed_num = ''
            while len(seed_name) > 0 and seed_name[-1].isdigit():
                seed_num = seed_num + seed_name[-1]
                seed_name = seed_name[:-1]
            seed_num = int(seed_num[::-1]) if len(seed_num) > 0 else 0
        if try_again >= 2:
            seed_num = seed_num + 1
            random_seed = seed_name + str(seed_num)
        print('new puzzle ID (size/seed/difficulty): ',
              [array_size, random_seed, difficulty])

        if array_size == 25:
            print('creating the new Sudoku puzzle ... (might take a while)')
        else:
            print('creating the new Sudoku puzzle ...')
        c_puzzle, c_solution = gen_customized_puzzle(array_size, random_seed,
                                                     difficulty)

        ## solving the puzzle manually
        puzzle_updated = c_puzzle.copy()
        help_str = ['--------------------------------------------------',
                    ' List all short-cuts:',
                    '   h:  print this help',
                    '   hN:  show next N hints (random)',
                    '   ha:  show all hints',
                    '   D:  highlight Sudoku number D',
                    '   c:  show current status',
                    '   r:  restart current puzzle',
                    '   s:  show final solution',
                    '   n:  start a new puzzle',
                    '   q:  quit the game',
                    '--------------------------------------------------',
                    ' Format of position filling string(s):',
                    '   "VH=D"  (multiple strings separated by ",")',
                    '   "V"  --  vertical index of an empty position',
                    '   "H"  --  horizontal index of an empty position',
                    '   "D"  --  digits to be filled',
                    '   All blank spaces ignored; and case insensitive',
                    '--------------------------------------------------']
        display(c_puzzle)
        print('Please input:')
        print('  - "h" or "help" to print doc on short-cuts; or ')
        print('  - strings to fill empty positions with digits,')
        print('      e.g. "B7=8, H5=2"')
        p = input('  > type here:  ')
        filling_lst = []  ## list of filling strings, like ["B7=8"]
        new_puzzle_now = False  ## to start a new puzzle immediately
        while np.count_nonzero(puzzle_updated == 0) > 0 and not new_puzzle_now:
            if len(p) == 0 or len(p.replace(' ', '')) == 0:
                p = input('  >  ')
                continue
            elif p.lower() in ['h', 'help']:
                for s in help_str:
                    print(' ' * 4 + s)
            elif p.lower()[0] == 'h' and not ('=' in p):
                N = p.lower()[1:]
                if not (N.isdigit() or N == 'a'):
                    p = input('     not "hN" or "ha". try again:  ')
                    continue
                a_lst, pos_x, pos_y = available_digits(puzzle_updated)
                ## choose empty positions with no ambiguity
                idx_hint = [i for i in range(len(a_lst))
                            if len(a_lst[i]) == 1]
                if len(idx_hint) == 0:
                    print('  no hint found!')
                    p = input('  >  ')
                    continue
                pos_x_hint = [pos_x[i] for i in idx_hint]
                pos_y_hint = [pos_y[i] for i in idx_hint]
                disp_x_hint, disp_y_hint = convert_index(array_size,
                                                         pos_x_hint, pos_y_hint)
                hint_list = [disp_x_hint[i] + disp_y_hint[i] for i
                             in range(len(idx_hint))]
                random.shuffle(hint_list)
                if N != 'a':
                    hint_list = hint_list[:min([int(N), len(idx_hint)])]
                display(puzzle_updated, filling_lst, hint_list)
            elif p.upper() == 'D':
                print('  "{}" is not a Sudoku number, please input a number!'.format(p))
                p = input('  >  ')
                continue
            elif p.lower() == 'c':
                display(c_puzzle, filling_lst)
            elif p.lower() == 's':
                display(c_solution)
            elif p.lower() == 'r':  ## restart current puzzle
                print('-' * n_dash)
                print('Restart current puzzle with ID:',
                      [array_size, random_seed, difficulty])
                puzzle_updated = c_puzzle.copy()
                filling_lst = []
                p = 'c'
                continue
            elif p.lower() == 'n':  ## start a new puzzle now
                new_puzzle_now = True
                continue
            elif p.lower() == 'q':  ## quit the puzzle game
                print('')
                print('Quit the game now ...')
                print('  puzzle ID:', [array_size, random_seed, difficulty])
                n_remained = np.count_nonzero(puzzle_updated == 0)
                n_total = np.count_nonzero(c_puzzle == 0)
                print('  empty positions (remained/total): {}/{}={}'.format(
                    n_remained, n_total, round(n_remained / n_total), 3))
                print('')
                exit(0)
            elif '=' in p:  ## filling empty positions
                filling_new = []
                error_lst = []
                for s in p.split(','):
                    if not ('=' in s):
                        continue
                    s_clean = s.replace(' ', '')
                    t = s_clean.split('=')
                    if not (len(t[0]) == 2 and t[1].isdigit()):
                        error_lst.append(s_clean)
                        continue
                    try:
                        x, y = convert_index(array_size, t[0][0], t[0][1])
                        if c_solution[x[0], y[0]] == int(t[1]):
                            filling_new.append(s_clean)
                            puzzle_updated[x[0], y[0]] = int(t[1])
                        else:
                            error_lst.append(s_clean)
                    except Exception:
                        error_lst.append(s_clean)
                if len(error_lst) > 0:
                    print('  incorrect filling string(s):')
                    print('       ', ','.join(error_lst))
                print('  {} filling string(s) recognized'.format(
                    len(error_lst + filling_new)))
                if len(filling_new) > 0:
                    filling_lst = filling_lst + filling_new
                    print('  {} position(s) updated'.format(len(filling_new)))
                    display(c_puzzle, filling_lst)
                    if np.count_nonzero(puzzle_updated == 0) == 0:
                        print('🎉🎉🎉  Bingo! 🎉🎉🎉')
                        print('You completed the puzzle:',
                              [array_size, random_seed, difficulty])
                        print('')
                        continue
                else:
                    print('  0 position is updated')
            elif p.isdigit():
                p = int(p)
                if 0 < p <= array_size:
                    display(c_puzzle, filling_lst, digit=p)
                else:
                    print('  "{}" is not a Sudoku number. try again'.format(p))
                    p = input('  >  ')
                    continue
            else:
                print('  input not recognized, ignored')
            print('Type short-cuts or filling string(s) here: ')
            p = input('  >  ')
        if new_puzzle_now:
            p = 'y'
        else:
            p = input('Do you want another new puzzle? (y/n)  [y]:  ')
        if p.lower() in ['n', 'no']:
            try_again = 0
        else:
            try_again = try_again + 1
    print('')


if __name__ == '__main__':
    main_sudoku_play()
