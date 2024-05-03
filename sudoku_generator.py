"""
Sudoku puzzle generation functions:
    available_digits(): find possible digits under Sudoku conditions
                        for given position(s)
    gen_sudoku_full(): generate a fully-filled Sudoku array, i.e. solution
    gen_sudoku_puzzle(): generate a Sudoku puzzle from given solution array
                         by kicking out array elements, but keeping unique
                         solution in mind

MIT license
Copyright (c) 2024 ddotplus@github
"""

import numpy as np
import random

def available_digits(sudoku_array, pos_x=None, pos_y=None):
    """ List All Possible Digit Values in Empty Sudoku Position(s)
    Input:
        sudoku_array: 2D squared numpy array, incomplete Sudoku array,
                      and empty positions defined by 0
        pos_x: int, x index of given empty position in the array
               if None, use those of all possible empty positions
        pos_y: int, y index of given empty position in the array
               if None, use those of all possible empty positions
    Output:
        avail_digits: list of list, list of possible Digits for
                      following (pos_x, pos_y)
        pos_x: list of x indices of empty positions
        pos_y: list of y indices of empty positions
    """
    if not isinstance(sudoku_array, np.ndarray):
        raise ValueError('available_digits(): <sudoku_array> not numpy array')
    n0 = sudoku_array.shape[0]              ## size of whole grid
    n1 = int(n0 ** (1/2))                   ## size of inner boxes
    if (n0 != sudoku_array.shape[1]) or (n0 != n1 ** 2):
        raise ValueError('available_digits(): <sudoku_array> not a squared size')
    if np.max(sudoku_array) > n0:
        raise ValueError('available_digits(): <sudoku_array> max value overflow')
    if pos_x is None and pos_y is None:     ## use all empty positions
        pos_x, pos_y = np.nonzero(sudoku_array == 0)    ## x: vertical axis
    else:
        if pos_x < 0 or pos_x >= n0 or pos_y < 0 or pos_y >= n0:
            raise ValueError('available_digits(): input <pos_x/y> out of range')
        pos_x = [pos_x]
        pos_y = [pos_y]

    avail_digits = []
    for ix, iy in zip(pos_x, pos_y):
        ix1 = int(ix // n1)
        iy1 = int(iy // n1)
        exist_lst = list(sudoku_array[ix, :]) + list(sudoku_array[:, iy]) \
           + list(sudoku_array[ix1*n1:(ix1+1)*n1, iy1*n1:(iy1+1)*n1].flatten())
        avail_lst = list(set(range(1, 1+n0)) - set(exist_lst))
        avail_digits.append(avail_lst)
    return avail_digits, pos_x, pos_y


def gen_sudoku_full(array_size=9, random_seed=None):
    """ Generate All Digits in A Squared Array That Follow Sudoku Conditions
    Input:
        array_size: int, size of Sudoku puzzle array in one dimension
        random_seed: int or string, seed for random.shuffle(),
                     to reproduce case for purpose
    Output:
        sudoku_full: 2D squared numpy array, complete Sudoku array
    """
    if (not isinstance(array_size, int)) or \
            (array_size != int(array_size**(1/2)) ** 2):
        raise ValueError('gen_sudoku_full(): <array_size> not int or squared')
    random.seed(random_seed)
    n0 = array_size

    ## generate full-array elements, one by one
    sudoku_full = np.zeros((n0, n0), dtype=int)
    my, mx = np.meshgrid(np.arange(0, n0), np.arange(0, n0))
    mx = mx.flatten()                        ## mx: vertical axis
    my = my.flatten()
    i = 0
    avail_lst = []
    n_steps = 0
    while i < len(mx):
        n_steps = n_steps + 1                ## for overhead-ratio calc
        a_lst, _, _ = available_digits(sudoku_full, mx[i], my[i])
        a_lst = a_lst[0]
        if len(a_lst) == 0:                  ## if not working, one-step back
            while len(avail_lst[i-1]) == 1:  ## will be empty , more steps back
                avail_lst.pop()
                sudoku_full[mx[i-1], my[i-1]] = 0
                i = i - 1
            avail_lst[i-1].pop(0)
            sudoku_full[mx[i-1], my[i-1]] = avail_lst[i-1][0]
        else:
            random.shuffle(a_lst)
            sudoku_full[mx[i], my[i]] = a_lst[0]
            avail_lst.append(a_lst)
            i = i + 1
    # print('overhead ratio: ', round(n_steps/n0**2-1, 2))
    return sudoku_full


def gen_sudoku_puzzle(sudoku_full, max_removed_ratio=None, random_seed=None):
    """ Create a Sudoku Puzzle from Its Solution (Full Sudoku Array)
    Input:
        sudoku_full: 2D squared numpy array, complete Sudoku array
        max_removed_ratio: float, max ratio of removed array elements
        random_seed: int or string, seed for random.shuffle(),
                     to reproduce case for purpose
    Output:
        sudo_array: 2D squared numpy array, incomplete Sudoku array,
                    as a Sudoku game
    """
    if not isinstance(sudoku_full, np.ndarray):
        raise ValueError('gen_sudoku_puzzle(): <sudoku_array> not numpy array')
    n0 = sudoku_full.shape[0]
    if np.max(sudoku_full) > n0 or np.min(sudoku_full) < 1:
        raise ValueError('gen_sudoku_puzzle(): <sudoku_full> value overflow')
    for i in range(len(sudoku_full)):
        if len(set(sudoku_full[i])) != n0:
            raise ValueError('gen_sudoku_puzzle(): <sudoku_full> inconsistent')
    if max_removed_ratio is None:
        nmax_idx = -1                                         ## no max limit
    else:
        nmax_idx = max([1, int(max_removed_ratio * n0**2)])   ## min = 1
    random.seed(random_seed)

    my, mx = np.meshgrid(np.arange(0, n0), np.arange(0, n0))
    mx = mx.flatten()
    my = my.flatten()
    idx = list(range(n0**2))
    random.shuffle(idx)
    sudoku_array = sudoku_full.copy()
    for i in idx:
        tmp = sudoku_array.copy()
        tmp[mx[i], my[i]] = 0
        a_lst, _, _ = available_digits(tmp, mx[i], my[i])
        if len(a_lst[0]) == 1:            ## for puzzle with unique solution
            sudoku_array[mx[i], my[i]] = 0
            nmax_idx = nmax_idx - 1
            if nmax_idx == 0:
                break

    # removed_ratio = round(np.count_nonzero(sudoku_array == 0)/n0**2, 2)
    # print('element removed ratio: ', removed_ratio)
    return sudoku_array
