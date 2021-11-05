"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : prune_by_density.py
# @Software: PyCharm
-------------------------------------
"""

import os

from utils import ProgressBar
from .prune_by_direction import get_node


def prune_density(sd_desensitization_after_prune_direction_path: str, sd_final_path: str,
                  min_latitude: float, min_longitude: float, len_latitude: float,
                  len_longitude: float, density_grid_side: int, trajs_file_name_list: list):
    """

    orientation based post processing

    Args:
        sd_desensitization_after_prune_direction_path: trajectory file path after direction-based post-processing
        sd_final_path                                : the path of the final processed trajectory file
        min_latitude                                 : minimum latitude(GPS)
        min_longitude                                : minimum longitude(GPS)
        len_latitude                                 : latitude range(GPS)
        len_longitude                                : longitude range(GPS)
        density_grid_side                            : initialize the uniform grid side length of the map
        trajs_file_name_list                         : trajectory file name

    Returns:

    """
    D = []
    D_grid = []
    ite_len = density_grid_side ** 2

    with open(sd_desensitization_after_prune_direction_path, 'r') as f:
        for line in f.readlines():
            T_new = []
            T_grid = []
            pre_count = 0

            for item in line.strip()[1:-1].split('(')[1:]:
                pre_count += 1
                x = float(item.split(',')[0].strip())
                y = float(item.split(',')[1][:-1].strip())

                T_new.append((x, y))
                xg = int((x - min_latitude) / len_latitude * density_grid_side)
                yg = int((y - min_longitude) / len_longitude * density_grid_side)

                if xg >= density_grid_side:
                    xg = density_grid_side - 1
                if yg >= density_grid_side:
                    yg = density_grid_side - 1
                t = xg * density_grid_side + yg
                T_grid.append(t)

            D.append(T_new)
            D_grid.append(T_grid)

    D_final = []
    last_count = 0
    total_count = 0

    p = ProgressBar(ite_len, 'Pruning according to the trajectory density distribution')
    for i in range(ite_len):
        p.update(i)
        for j in range(ite_len):
            check = False
            step_count = 0

            D_count = []
            d_count = 0

            Area = [0 for _ in range(ite_len)]
            for T in D_grid:
                if T[0] == i and T[-1] == j:
                    if len(T) != 2:
                        check = True
                    for item in T:
                        Area[item] += 1
                        step_count += 1

                    D_count.append(d_count)
                d_count += 1
            if check is not True:
                for T_index in D_count:
                    T_final = list()
                    T_final.append(D[T_index][0])
                    T_final.append(D[T_index][-1])
                    D_final.append(T_final)
            else:
                floor = len(D_count)
                for T_index in D_count:
                    T_final = []
                    T_temp = D_grid[T_index]
                    T_final.append(D[T_index][0])
                    total_check = False
                    last_check = False

                    for it_index in range(1, len(D_grid[T_index]) - 1):
                        item = T_temp[it_index]
                        # cells with less than a certain number of passes, delete the middle point
                        if Area[item] < floor:
                            total_check = True
                            if i >= len(T) - 5:
                                last_check = True
                                continue
                            T_final.append(
                                get_node(D[T_index][it_index][0], D[T_index][it_index][1],
                                         D[T_index][it_index - 1][0], D[T_index][it_index - 1][1],
                                         D[T_index][it_index + 1][0], D[T_index][it_index + 1][1]))

                        else:
                            T_final.append(D[T_index][it_index])
                    T_final.append(D[T_index][-1])
                    D_final.append(T_final)

                    if last_check:
                        last_count += 1
                    elif total_check:
                        total_count += 1

    # write file
    if not os.path.exists(sd_final_path):
        os.mkdir(sd_final_path)

    for i, sd in enumerate(D_final):
        with open(sd_final_path + trajs_file_name_list[i], 'w') as sd_final_file:
            for point in sd:
                sd_final_file.writelines(str(point)[1:-1] + '\n')
