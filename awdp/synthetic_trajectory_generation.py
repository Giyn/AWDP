"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : synthetic_trajectory_generation.py
# @Software: PyCharm
-------------------------------------
"""

import pickle
import random

import numpy as np

from utils import ProgressBar


def synthetic_generate_trajs(grid_tree_path: str, trip_distribution_path: str,
                             midpoint_movement_path: str, routes_length_path: str, sd_path: str,
                             sd_desensitization_path: str, n_grid_side: int, max_traj_len: int,
                             min_latitude: float, min_longitude: float, nSyn: int, rate: int):
    """

    multi level adaptive meshing (main function)

    Args:
        grid_tree_path         : grid tree file path
        trip_distribution_path : starting and ending point distribution probability matrix path
        midpoint_movement_path : markov transition probability matrix path
        routes_length_path     : trajectory length estimation matrix
        sd_path                : trajectory path
        sd_desensitization_path: desensitization trajectory path
        n_grid_side            : the number of sides of the grid (n×n)
        max_traj_len           : maximum track length
        min_latitude           : minimum latitude (gps)
        min_longitude          : minimum longitude (gps)
        nSyn                   : number of trajectory
        rate                   : grid scaling

    Returns:

    """
    with open(grid_tree_path, 'rb') as grid_tree_file:
        grid_tree = pickle.loads(grid_tree_file.read())

    # starting and ending point distribution probability matrix
    with open(trip_distribution_path, 'r') as trip_distribution_file:
        R = np.array([list(map(lambda x: float(x), line.split(' '))) for line in
                      trip_distribution_file.readlines()])

    # markov transition probability matrix
    with open(midpoint_movement_path, 'r') as midpoint_movement_file:
        X = np.array([list(map(lambda x: float(x), line.split(' '))) for line in
                      midpoint_movement_file.readlines()])

    X_copy = X.copy()
    X_array = [X_copy]
    # power the transition probability matrix first,
    # basically unchanged after a certain number of iterations
    for i in range(max_traj_len):
        X_array.append(X_array[i].dot(X_copy))

    X_array_len = len(X_array)

    # trajectory length estimation matrix
    with open(routes_length_path, 'r') as routes_length_file:
        L = [i for each in [list(map(lambda x: float(x), line.split(' '))) for line in
                            routes_length_file.readlines()] for i in each]

    # start to synthesize
    with open(sd_path, 'w') as sd_file:
        SD = []
        index_list = [int(j) for j in range(n_grid_side * n_grid_side)]
        R /= np.sum(R)

        p = ProgressBar(nSyn, 'Comprehensive data')

        for i in range(nSyn):
            p.update(i)
            # Pick a sample S = (C_start, C_end) from Rˆ
            index = np.random.choice(index_list, p=R.ravel())

            start_point = int(index / n_grid_side)  # starting point of grid trajectory
            end_point = index - start_point * n_grid_side  # end of grid trajectory

            l_hat = L[index]  # trajectory length parameter

            # Exponential distribution takes the trajectory length
            route_length = int(np.round(random.expovariate(np.log(2) / l_hat)))
            if route_length < 2:
                route_length = 2

            T = []
            prev_point = start_point
            T.append(prev_point)

            for j in range(1, route_length - 1):
                # Thesis formula, X is the route length-j times, look for the X array subscript,
                # and take the last one if it exceeds the X array length
                if route_length - 1 - j - 1 >= X_array_len:
                    X_now = X_array[-1]
                else:
                    X_now = X_array[route_length - 1 - j - 1]
                # sampling
                sample_prob = []
                for k in range(n_grid_side):
                    # add sampling probability
                    sample_prob.append(X_now[k][end_point] * X[prev_point][k])

                sample_prob = np.array(sample_prob)
                if np.sum(sample_prob) == 0:
                    continue

                sample_prob /= np.sum(sample_prob)  # normalized
                now_point = np.random.choice([int(m) for m in range(n_grid_side)],
                                             p=sample_prob.ravel())  # sampling
                prev_point = now_point
                T.append(now_point)

            T.append(end_point)
            SD.append(T)

        for sd in SD:
            sd_file.writelines(str(sd) + '\n')

    # converted into original data coordinates
    with open(sd_desensitization_path, 'w') as sd_desensitization_file:
        SD_desensitization = []

        p2 = ProgressBar(nSyn, 'Desensitization data coordinate restoration')
        for i in range(nSyn):
            p2.update(i)
            T = SD[i]
            T_desensitization = []

            for j in range(len(T)):
                grid_number = T[j]
                correspond_node = grid_tree.num_to_position(grid_number)
                try:
                    correspond_node_start = (correspond_node.start_lat, correspond_node.start_lon)
                    correspond_node_end = (correspond_node.end_lat, correspond_node.end_lon)
                    # random sampling
                    res_row = random.uniform(correspond_node_start[0], correspond_node_end[0])
                    res_col = random.uniform(correspond_node_start[1], correspond_node_end[1])
                    out_point = (res_row / rate + min_latitude, res_col / rate + min_longitude)
                    T_desensitization.append(out_point)
                except AttributeError:
                    print('AttributeError: \'NoneType\' object has no attribute \'start_lat\'')

            SD_desensitization.append(T_desensitization)

        for sd in SD_desensitization:
            sd_desensitization_file.writelines(str(sd) + '\n')
