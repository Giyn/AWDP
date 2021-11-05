"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : prune_by_direction.py
# @Software: PyCharm
-------------------------------------
"""

import math

import numpy as np

from utils import ProgressBar


def get_node(a, b, x1, y1, x2, y2):
    """

    Args:
        a :
        b :
        x1:
        y1:
        x2:
        y2:

    Returns:
        x:
        y:

    """
    if x1 == x2:
        return x1, b
    elif y1 == y2:
        return a, y1
    else:
        k = (y1 - y2) / (x1 - x2)
        x = (k * k * x1 + a + k * b - k * y1) / (k * k + 1)
        y = (k * k * b + a * k + y1 - k * x1) / (k * k + 1)

        return x, y


def prune_direction(sd_desensitization_path, sd_desensitization_after_prune_direction_path):
    """

    orientation based post processing

    Args:
        sd_desensitization_path                      : file path of desensitization trajectory
        sd_desensitization_after_prune_direction_path: trajectory file path after direction-based post-processing

    Returns:

    """
    with open(sd_desensitization_path, 'r') as sd_desensitization_file:
        D = []
        for each_traj_list in sd_desensitization_file.readlines():
            D.append(eval(each_traj_list))

    D_new = []
    last_count = 0
    total_count = 0
    trajs_len = len(D)

    p = ProgressBar(trajs_len, 'Pruning according to the direction')
    for i in range(trajs_len):
        p.update(i)
        T = D[i]

        T_new = [T.copy()[0], T.copy()[1]]
        if T_new[0][0] == T_new[1][0]:
            last_dir = np.inf
        else:
            last_dir = abs((T_new[1][1] - T_new[0][1]) / (T_new[1][0] - T_new[0][0]))
        total_check = False
        last_check = False

        for i in range(2, len(T) - 1):
            if T[i][0] == T[i - 1][0]:
                now_dir = np.inf
            else:
                now_dir = abs((T[i][1] - T[i - 1][1]) / T[i][0] - T[i - 1][0])
            if T[i][0] == T[i + 1][0]:
                next_dir = np.inf
            else:
                next_dir = abs((T[i - 1][1] - T[i + 1][1]) / (T[i - 1][0] - T[i + 1][0]))

            thred = abs(math.atan(last_dir) - math.atan(next_dir))
            if abs(math.atan(next_dir) - math.atan(now_dir)) < (math.pi / 2):
                total_check = True
                if i >= len(T) - 5:
                    last_check = True

                if abs(math.atan(next_dir) - math.atan(now_dir)) > thred:
                    new_node = get_node(T[i][0], T[i][1], T[i - 1][0], T[i - 1][1], T[i + 1][0],
                                        T[i + 1][1])
                    if abs(T[i - 1][0] - new_node[0]) < abs(T[i - 1][0] - T[i + 1][0]) and \
                            abs(T[i + 1][0] - new_node[0]) < abs(T[i - 1][0] - T[i + 1][0]):
                        T_new.append(
                            get_node(T[i][0], T[i][1], T[i - 1][0], T[i - 1][1], T[i + 1][0],
                                     T[i + 1][1]))
                        last_dir = abs((T[i][1] - T_new[-1][1]) / T[i][0] - T_new[-1][0])
                else:
                    T_new.append((T[i][0], T[i][1]))
                    last_dir = now_dir

        if last_check:
            last_count += 1
        elif total_check:
            total_count += 1
        if len(T) > 2:
            T_new.append(T[-1])
        D_new.append(T_new)

    with open(sd_desensitization_after_prune_direction_path, 'w') as sd_final_file:
        for sd in D_new:
            sd_final_file.writelines(str(sd) + '\n')
