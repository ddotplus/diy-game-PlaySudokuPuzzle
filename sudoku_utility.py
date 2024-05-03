"""
Sudoku utility functions:
    solve_sudoku(): a solver for Sudoku puzzles to find all solutions
    convert_index(): index converting between numpy array and display on screen
    display(): generate and display a list of line strings to present Sudoku
               puzzle with colors on screen

MIT license
Copyright (c) 2024 ddotplus@github
"""

from sudoku_generator import *
import numpy as np

def solve_sudoku(sudoku_array):
    """ Find Solution(s) to A Given Sodoku Puzzle
    Input:
        sudoku_array: 2D squared numpy array, incomplete Sudoku array,
                      and empty positions defined by 0
    Output:
        sudoku_solutions: list of 2D numpy array, a list of complete Sudoku
                          solutions
        solving_record: nested list, record num of positions filled in
                        the process of finding solution(s)
    """
    sudoku_arr = sudoku_array.copy()
    n0_zeros = len(sudoku_arr[sudoku_arr == 0])
    n_zeros = n0_zeros
    sudoku_solutions = []
    solving_record = []
    while n_zeros > 0:
        avail_lst, pos_x, pos_y = available_digits(sudoku_arr)
        n_avail = [len(a) for a in avail_lst]
        if min(n_avail) == 0:                 ## see deadend, give up
            solving_record.append(
                            n_zeros - len(sudoku_arr[sudoku_arr == 0]))
            return None, solving_record
        elif min(n_avail) == 1:               ## normal cases, do iterations
            indices = [i for i, n in enumerate(n_avail) if n == 1]
            for idx in indices:
                sudoku_arr[pos_x[idx], pos_y[idx]] = avail_lst[idx][0]
            n_zeros = len(sudoku_arr[sudoku_arr == 0])
        else:         ## sub-branch searching, potentially multiple solutions
            indices = [i for i, n in enumerate(n_avail) if n == min(n_avail)]
            record_indices = [n0_zeros-n_zeros]
            for idx in indices:
                record_idx = []
                for val in avail_lst[idx]:
                    tmp = sudoku_arr.copy()
                    tmp[pos_x[idx], pos_y[idx]] = val
                    tmp_solved, tmp_record = solve_sudoku(tmp)
                    record_idx.append(tmp_record)
                    if not (tmp_solved is None):
                        sudoku_solutions = sudoku_solutions + tmp_solved
                        print('')
                        print(tmp_solved)
                record_indices.append(record_idx)
            solving_record.append(record_indices)
            break
    if len(solving_record) == 0:                  ## no sub-branch searching
        sudoku_solutions = [sudoku_arr]
        solving_record.append([n0_zeros-n_zeros, sudoku_arr])
    return sudoku_solutions, solving_record


def convert_index(array_size, pos_x, pos_y):
    """ Converting Between Array Index and Display Index
    Note:
        array index: x,y: [0,1,2,3,...]
        display index: x: ['A','B','C',...] (vertical)
                       y: ['1','2','3',...,'9','a','b',...] (horizontal)
    Input:
        array_size: int, size of Sudoku puzzle array in one dimension
        pos_x: int, string or list, vertical direction of
               array index (int/list, e.g. 10 or [0,7,15]),  or
               display index (str/list, e.g. 'K' or ['A','H','P'])
        pos_y: int, str or list, horizontal direction of
               array index (int/list, e.g. 10 or [0,7,15]),  or
               display index (str/list, e.g. 'b' or ['1','8','g'])
    Output:
        pos_x_converted: int, string, or list, new pox_x after conversion
        pos_y_converted: int, string, or list, new pox_y after conversion
    """
    if (isinstance(pos_x, int) and isinstance(pos_y, int)) or \
       (isinstance(pos_x, str) and isinstance(pos_y, str)):
        pos_x = [pos_x]
        pos_y = [pos_y]
    elif isinstance(pos_x, list) and isinstance(pos_y, list):
        if len(pos_x) != len(pos_y):
            raise ValueError('convert_index(): <pos_x/y> unpaired')

    import string
    array_xy = list(range(array_size))
    display_x = list(string.ascii_uppercase[:array_size])
    display_y = list(string.printable[1:1+array_size])

    pos_x_converted = []
    pos_y_converted = []
    for x, y in zip(pos_x, pos_y):
        if isinstance(x, str) and isinstance(y, str):
            x = x.upper()                   ## for case insensitive
            y = y.lower()
            if not (x in display_x) or not (y in display_y):
                raise ValueError('convert_index(): x or y overflow:', x, y)
            pos_x_converted.append(array_xy[display_x.index(x)])
            pos_y_converted.append(array_xy[display_y.index(y)])
        elif x == int(x) and y == int(y):
            if x < 0 or x > array_size or y < 0 or y > array_size:
                raise ValueError('convert_index(): x or y overflow:', x, y)
            pos_x_converted.append(display_x[array_xy.index(x)])
            pos_y_converted.append(display_y[array_xy.index(y)])
    return pos_x_converted, pos_y_converted


def display(sudoku_array, filling_list=None, hint_list=None, digit=None):
    """ Box-drawing of Sudoku puzzle with a color scheme
    Note:
        - limit of current version: array size <= 25
        - array index: x,y: [0,1,2,3,...]
        - display index: x: ['A','B','C',...] (vertical)
                         y: ['1','2','3',...,'9','a','b',...] (horizontal)
    Input:
        sudoku_array: 2D numpy array, digits in Sudoku array
        filling_list: list of filling strings, eg: ['A2=5', 'D7=8', 'Ka=12']
        hint_list: list of position strings as hint, eg: ['A2','D7']
        digit: int, single Sudoku number/digit to be highlighted
    Output:
        boxdraw: list of line strings, ready for printing in terminal
    """
    ## check sudoku_array
    if not isinstance(sudoku_array, np.ndarray):
        raise ValueError('display(): <sudoku_array> not numpy array')
    n0 = sudoku_array.shape[0]              ## size of whole grid
    n1 = int(n0 ** (1/2))                   ## size of inner boxes
    if n0 > 25:
        raise ValueError('display(): <sudoku_array> is too large ' +
                         'to display properly here (array_size > 25)')
    if (n0 != sudoku_array.shape[1]) or (n0 != n1 ** 2):
        raise ValueError('display(): <sudoku_array> size not squared ')
    ## generate display indices
    nd = len(str(n0))                       ## number of digits that <n0> has
    display_x, display_y = convert_index(n0, list(range(n0)), list(range(n0)))
    ## check and convert filling_list
    if isinstance(filling_list, str):
        filling_list = [filling_list]
    if not (filling_list is None or len(filling_list) == 0):
        if not all(['=' in s for s in filling_list]):
            raise ValueError('display(): <filling_list> missing "="')
        f_lst = [s.replace(' ', '').split('=') for s in filling_list]
        if not all([len(s[0]) == 2 and s[0][0].upper() in display_x
                    and s[0][1].lower() in display_y for s in f_lst]):
            raise ValueError('display(): <filling_list> display indices error')
        if not all([0 < int(s[1]) <= n0 for s in f_lst]):
            raise ValueError('display(): <filling_list> filled value overflow')
        for i in range(len(f_lst)):
            t = f_lst[i][0]
            ax, ay = convert_index(n0, t[0], t[1])  ## convert to array indices
            f_lst[i] = [ax[0], ay[0], f_lst[i][1]]  ## will be used in display
    ## check and convert hint_list
    if isinstance(hint_list, str):
        hint_list = [hint_list]
    if not (hint_list is None):
        if not all([len(s)==2 and s[0] in display_x
                    and s[1] in display_y for s in hint_list]):
            raise ValueError('display(): <hint_list> display indices error')
        h_lst = hint_list.copy()
        for i in range(len(h_lst)):                ## convert to array indices
            ax, ay = convert_index(n0, h_lst[i][0], h_lst[i][1])
            h_lst[i] = [ax[0], ay[0]]              ## will be used in display
    ## check <digit>
    if not (digit is None):
        if (isinstance(digit, str) and digit.isdigit()) or \
                (digit == int(digit)):
            digit = int(digit)
        else:
            raise ValueError('display(): <digit> not digit')
        if digit < 1 or digit > n0:
            raise ValueError('display(): <digit> not in [1,{}]'.format(n0))

    ## color scheme (ANSI escape sequences)
    font_type = '1;'          ## bold: for normal cell value
    font_color = '34;'        ## blue: for normal cell value
    bg_color_0 = '43m'        ## yellow: style-0 background of inner block
    bg_color_1 = '47m'        ## white: style-1 background of inner block
    hint_type = '5;'          ## flashing: for hint highlight
    fill_color = '31;'        ## red: for filling value
    digi_color = '37;'        ## white: for the digit to be highlighted
    digi_bg = '40m'           ## balck: for the digit to be highlighted
    normal = ['\033[' + font_type + font_color + bg_color_0,
              '\033[' + font_type + font_color + bg_color_1]
    hint = ['\033[' + hint_type + font_color + bg_color_0,
            '\033[' + hint_type + font_color + bg_color_1]
    fill = ['\033[' + font_type + fill_color + bg_color_0,
            '\033[' + font_type + fill_color + bg_color_1]
    digi = ['\033[' + font_type + fill_color + digi_bg,  ## for filled
            '\033[' + font_type + digi_color + digi_bg]  ## for not filled
    ending = '\033[0;0m'
    # print(hint[0] + 'hint' + ending, fill[0] + 'fill' + ending)  ## for test

    ## start box-draw
    top_bottom = ' '*(nd+2)+(' '*(nd+1)).join(display_y) ## horizontal indices
    boxdraw = [top_bottom]
    for ix in range(n0):
        line = []
        for iy in range(n0):
            t = ''
            t_show = 'normal'
            if sudoku_array[ix, iy] == 0:          ## replace empty position
                if not (hint_list is None):        ##   by hint symbol
                    if len([x for x, y in h_lst if x == ix and y == iy]) > 0:
                        t = u"\u2587" * nd
                        t_show = 'hint'
                                                   ##   by filled value
                if not (filling_list is None or len(filling_list) == 0):
                    t = [int(v) for x, y, v in f_lst if x == ix and y == iy]
                    if len(t) > 0:
                        if t[0] == digit:
                            t_show = 'fill_digi'
                        else:
                            t_show = 'fill'
                        t = ('{:' + str(nd) + 'd}').format(t[0])
                if len(t) == 0:
                    t = u"\u2587" * nd
            else:
                t = ('{:'+str(nd)+'d}').format(sudoku_array[ix, iy])
            ## apply font/background color
            bg_index = ((ix // n1) + (iy // n1)) % 2    ## 0 or 1
            t_space = normal[bg_index] + ' ' + ending
            if t_show == 'hint':
                t = hint[bg_index] + t + ending
            elif t_show == 'fill':
                t = fill[bg_index] + t + ending
            elif t_show == 'fill_digi':
                t = digi[0] + t + ending
            elif sudoku_array[ix, iy] == digit:
                t = digi[1] + t + ending
            else:
                t = normal[bg_index] + t + ending
            line.append(t_space + t + t_space)
        line = display_x[ix] + ' ' + ''.join(line) + ' ' + display_x[ix]
        boxdraw.append(line)
    boxdraw.append(top_bottom)
    ## display box-draw
    hspace = [20, 10, 5, 3]     ## for array size: 4/9/16/25
    print('')
    for s in boxdraw:
        print(' ' * hspace[min([n1-2, 3])] + s)
    print('')
    return boxdraw


def display_classic(sudoku_array, filling_list=None, hint_list=None, digit=None):
    """ Box-drawing of Sudoku puzzle with classical black-white borderlines
       (under construction)
    Note:
        - limit of current version: array size <= 25
        - array index: x,y: [0,1,2,3,...]
        - display index: x: ['A','B','C',...] (vertical)
                         y: ['1','2','3',...,'9','a','b',...] (horizontal)
    Input:
        sudoku_array: 2D numpy array, digits in Sudoku array
        filling_list: list of filling strings, eg: ['A2=5', 'D7=8', 'Ka=12']
        hint_list: list of position strings as hint, eg: ['A2','D7']
        digit: int, single Sudoku number to be highlighted
    Output:
        boxdraw: list of strings, ready for printing on terminal
    """
    pass




