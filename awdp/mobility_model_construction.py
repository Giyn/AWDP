"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : mobility_model_construction.py
# @Software: PyCharm
-------------------------------------
"""

import numpy as np

from config import *
from utils import ProgressBar


def markov_model(trajs: list, n_grid: int, _epsilon: float, level_list: list,
                 h_max: int) -> np.ndarray:
    """

    markov model

    Args:
        trajs   : trajectory data
        n_grid  : number of secondary grids
        _epsilon: privacy budget
        level_list            : level list
        h_max                 : h_max

    Returns:
        O_: intermediate point transition probability matrix

    """
    O_ = np.zeros((n_grid, n_grid))  # establish n_grid * n_grid transition probability matrix
    for t in trajs:
        O_sub = np.zeros((n_grid, n_grid))
        for i in range(len(t) - 1):
            curr_point = t[i]
            next_point = t[i + 1]
            O_sub[curr_point][next_point] += 1
        O_sub /= (len(t) - 1)  # transition probability of the trajectory
        O_ += O_sub

    sum_of_level = sum(level_list)
    epsilon_step1 = _epsilon / epsilon_alloc['mmc'] * epsilon_alloc['mag']
    epsilon_step2 = _epsilon / epsilon_alloc['mmc'] * epsilon_alloc['tde']

    p = ProgressBar(n_grid, 'Generate midpoint transition probability matrix')
    for i in range(n_grid):
        i_epsilon = epsilon_step1 * (1 - level_list[i] / h_max) + \
                    epsilon_step2 * level_list[i] / sum_of_level + _epsilon
        p.update(i)
        for j in range(n_grid):
            j_epsilon = epsilon_step1 * (1 - level_list[j] / h_max) + \
                        epsilon_step2 * level_list[j] / sum_of_level + _epsilon
            noise = np.random.laplace(0, 1 / min(i_epsilon, j_epsilon))  # add laplacian noise
            O_[i][j] += noise

            if O_[i][j] < 0:
                O_[i][j] = 0

    # compute X
    row_sum = [sum(O_[i]) for i in range(n_grid)]
    for j in range(n_grid):
        O_[j] /= row_sum[j]

    return O_


def mobility_model_main(n_grid: int, _epsilon: float, grid_trajs_path: str,
                        midpoint_movement_path: str, level_list: list, h_max: int):
    """

    main function

    Args:
        n_grid                : number of grids
        _epsilon              : privacy budget
        grid_trajs_path       : grid track file path
        midpoint_movement_path: midpoint transition probability matrix file path
        level_list            : level list
        h_max                 : h_max

    Returns:

    """
    with open(grid_trajs_path, 'r') as grid_trajs_file:
        T = [eval(traj) for traj in grid_trajs_file.readlines()]
        with open(midpoint_movement_path, 'w') as midpoint_movement_file:
            midpoint_movement_matrix = markov_model(T, n_grid, _epsilon, level_list, h_max)
            for item in midpoint_movement_matrix:
                each_line = ' '.join([str(i) for i in item]) + '\n'
                midpoint_movement_file.writelines(each_line)
