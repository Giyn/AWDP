"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : multi_level_adaptive_grid_construction.py
# @Software: PyCharm
-------------------------------------
"""

import math
import os
import pickle

import numpy as np

from awdp.grid_tree import GridTree
from utils import ProgressBar

divide_times = 0


def grid_tree_list_length(grid_tree_list: list, count: int, level: int) -> int:
    """

    calculate the length of the grid tree

    Args:
        grid_tree_list: grid tree list(such as [[1, 1, 1, 1], 1, 1, 1])
        count         : number of grids (number of tree nodes)
        level         : number of grid tree layers

    Returns:
        count: total number of grids (number of tree nodes)

    """
    for i in range(len(grid_tree_list)):
        if type(grid_tree_list[i]) == int:
            count += grid_tree_list[i]
        else:
            count = grid_tree_list_length(grid_tree_list[i], count, level + 1)

    return count


def gps_to_grid_trajs(trajs: list, grid_tree: GridTree, grid_trajs_path: str):
    """

    GPS to grid

    Args:
        trajs          : trajectory
        grid_tree      : grid tree
        grid_trajs_path: grid trajectory file path

    Returns:

    """
    grid_trajs = []
    trajs_len = len(trajs)

    p = ProgressBar(trajs_len, 'convert grid coordinates')
    for i in range(trajs_len):
        p.update(i)
        traj = trajs[i]
        grid_traj = []
        for step in traj:
            grid_traj.append(grid_tree.position_to_num(step))
        grid_trajs.append(grid_traj)

    with open(grid_trajs_path, 'w') as grid_trajs_file:
        for grid_traj in grid_trajs:
            grid_trajs_file.writelines(str(grid_traj) + '\n')


def eta(trajs: list, n_grid_side: int, grid_number: int, epsilon: float,
        grid_lat_len: float, grid_lon_len: float, start_lat, start_lon) -> float:
    """

    calculate the sum of the ratio of the number of trajectory points in the grid to the total
    number of trajectory points for all trajectories in each grid

    Args:
        trajs       : trajectory
        n_grid_side : number of sides of the grid (n×n)
        grid_number : grid number
        epsilon     : privacy budget
        grid_lat_len: grid latitude length
        grid_lon_len: grid longitude length
        start_lat   : starting latitude
        start_lon   : starting longitude

    Returns:
        score: the sum of the ratio of the number of trajectory points in the grid to the total
        number of trajectory points in all trajectories in each grid

    """
    score = 0
    for traj in trajs:
        temp_score = 0.0
        # compare each point
        for step in traj:
            # latitude is the row, longitude is the column
            if int((step[0] - start_lat) / grid_lat_len) * n_grid_side + \
                    int((step[1] - start_lon) / grid_lon_len) == grid_number:
                temp_score += 1
        if len(traj) != 0:
            score += temp_score / len(traj)

    # add laplacian noise
    noise = np.random.laplace(0, 1 / epsilon)
    score += noise

    return score


def main_eta(trajs: list, epsilon: float, grid_lat_len: float, grid_lon_len: float,
             start_lat: float, start_lon: float, n_grid: int, n_grid_side: int, max_level: int,
             now_level: int) -> list:
    """

    calculate the sum of the ratio of the number of trajectory points in the grid to the total
    number of trajectory points for all trajectories in each grid (main function)

    Args:
        trajs       : trajectory
        epsilon     : privacy budget
        grid_lat_len: grid latitude length
        grid_lon_len: grid longitude length
        start_lat   : starting latitude
        start_lon   : starting longitude
        n_grid      : number of grids
        n_grid_side : number of sides of the grid (n×n)
        max_level   : the maximum number of iterations
        now_level   : number of iterations at this stage

    Returns:
        grid_tree_list: total number of grids (number of tree nodes)

    """
    global divide_times
    divide_times += 1

    grid_tree_list = []
    print('epoch: %d' % divide_times)

    for each_grid in range(n_grid):
        eta_score = eta(trajs, n_grid_side, each_grid, epsilon, grid_lat_len, grid_lon_len,
                        start_lat, start_lon)
        if eta_score <= 0:
            beta = 0
        else:
            # maximum number of meshing iterations
            beta = int(math.log(eta_score, 6) / 2)
        if beta <= 1:
            grid_tree_list.append(1)
        else:
            if now_level == max_level:
                grid_tree_list.append([1 for _ in range(n_grid_side * n_grid_side)])
            else:
                row = int(each_grid / n_grid_side)
                col = each_grid - row * n_grid_side
                start_lat_ = row * grid_lat_len + start_lat
                start_lon_ = col * grid_lon_len + start_lon
                grid_tree_list.append(main_eta(trajs, epsilon, grid_lat_len / n_grid_side,
                                               grid_lon_len / n_grid_side, start_lat_, start_lon_,
                                               n_grid, n_grid_side, max_level, now_level + 1))

    return grid_tree_list


def get_grid_level(tree, level, level_list):
    for tre in tree:
        if type(tre) is list:
            get_grid_level(tre, level + 1, level_list)
        else:
            level_list.append(level)

    return level_list


def adaptive_grid_construction(trajs: list, n_grid_side: int, epsilon: float, h_max: int,
                               grid_tree_list_path: str, grid_trajs_path: str, grid_lat_len: float,
                               grid_lon_len: float, grid_tree_path: str):
    """

    multi level adaptive grid construction

    Args:
        trajs              : trajectory
        n_grid_side        : number of sides of the grid (n×n)
        epsilon            : privacy budget
        h_max              : maximum number of meshing iterations
        grid_tree_list_path: grid tree structure path
        grid_trajs_path    : grid trajectory path
        grid_lat_len       : grid latitude length
        grid_lon_len       : grid longitude length
        grid_tree_path     : grid tree file path

    Returns:

    """
    # store the number of small grids on each side in each large grid
    with open(grid_tree_list_path, 'w') as grid_tree_list_file:
        n_grid = n_grid_side * n_grid_side  # total number of large grids

        print('generating grid...')
        grid_tree_list = main_eta(trajs, epsilon / h_max, grid_lat_len, grid_lon_len, 0, 0, n_grid,
                                  n_grid_side, h_max, 1)
        print('completed grid generation')
        print(grid_tree_list)
        grid_tree_list_file.writelines(str(grid_tree_list))

        lis = []
        level_list_res = get_grid_level(grid_tree_list, 1, lis)

    # 初始化一级网格size
    grid_tree = GridTree(0, 0, grid_lat_len * 5, grid_lon_len * 5)
    grid_tree.add_nodes(grid_tree.root, grid_tree_list, n_grid_side, grid_lat_len,
                        grid_lon_len, 1, (0, 0))

    print('number of grids: ', grid_tree.set_num(grid_tree.root, 0))

    with open(grid_tree_path, 'wb') as grid_tree_file:
        grid_tree_str = pickle.dumps(grid_tree)
        grid_tree_file.write(grid_tree_str)

    gps_to_grid_trajs(trajs, grid_tree, grid_trajs_path)  # build a grid tree

    return grid_tree.set_num(grid_tree.root, 0), level_list_res


def adaptive_grid_construction_main(mdl_trajs_path: str, epsilon: float, n_grid_side: int,
                                    grid_lat_len: float, grid_lon_len: float,
                                    grid_tree_list_path: str, grid_trajs_path: str,
                                    grid_tree_path: str):
    """

    multi-level adaptive grid (main function)

    Args:
        mdl_trajs_path     : MDL trajectory file path
        epsilon            : privacy budget
        n_grid_side        : number of sides of the grid (n×n)
        grid_lat_len       : grid latitude length
        grid_lon_len       : grid longitude length
        grid_tree_list_path: grid tree structure path
        grid_trajs_path    : grid trajectory path
        grid_tree_path     : grid tree file path

    Returns:

    """
    mdl_trajs_file_list = os.listdir(mdl_trajs_path)

    D = []

    p = ProgressBar(len(mdl_trajs_file_list), 'read file')
    for i in range(len(mdl_trajs_file_list)):
        p.update(i)
        file_name = mdl_trajs_file_list[i]
        with open(mdl_trajs_path + file_name, 'r') as file:
            T = []
            for line in file.readlines():
                T.append(eval(line))
            D.append(T)

    h_max = np.round(math.log(len(D), n_grid_side) / 2)

    return adaptive_grid_construction(D, n_grid_side, epsilon, h_max, grid_tree_list_path,
                                      grid_trajs_path, grid_lat_len, grid_lon_len,
                                      grid_tree_path), h_max
