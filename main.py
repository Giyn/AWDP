"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : main.py
# @Software: PyCharm
-------------------------------------
"""

import os
import pickle

from joblib import Parallel
from joblib import delayed

from awdp import adaptive_grid_construction_main
from awdp import mobility_model_main
from awdp import prune_density
from awdp import prune_direction
from awdp import route_length_estimate_main
from awdp import synthetic_generate_trajs
from awdp import trip_distribution_main
from config import *

mdl_trajs_path = 'data/{}/MDL/'
grid_trajs_path = 'data/{}/Middleware/grid_trajs_epsilon_{}.txt'
grid_tree_list_path = 'data/{}/Middleware/grid_tree_list_epsilon_{}.txt'
grid_tree_path = 'data/{}/Middleware/grid_tree_epsilon_{}.pkl'
trip_distribution_path = 'data/{}/Middleware/trip_distribution_epsilon_{}.txt'
midpoint_movement_path = 'data/{}/Middleware/midpoint_movement_epsilon_{}.txt'
length_traj_path = 'data/{}/Middleware/routes_length_epsilon_{}.txt'
sd_path = 'data/{}/SD/sd_epsilon_{}.txt'
sd_desensitization_path = 'data/{}/SD/sd_desensitization_epsilon_{}.txt'
sd_desensitization_after_prune_direction_path = \
    'data/{}/SD/sd_desensitization_after_prune_direction_epsilon_{}.txt'
sd_final_path = 'data/{}/SD/sd_final_epsilon_{}/'

if not os.path.exists(f'data/{USE_DATA}/Middleware'):
    os.mkdir(f'data/{USE_DATA}/Middleware')

if not os.path.exists(f'data/{USE_DATA}/SD'):
    os.mkdir(f'data/{USE_DATA}/SD')


def run(epsilon):
    with open(f'data/{USE_DATA}/MDL_trajs_range.pkl', 'rb') as MDL_trajs_range_file:
        MDL_trajs_range = pickle.loads(MDL_trajs_range_file.read())

    with open(f'data/{USE_DATA}/GPS_trajs_range.pkl', 'rb') as GPS_trajs_range_file:
        GPS_trajs_range = pickle.loads(GPS_trajs_range_file.read())

    with open(f'data/{USE_DATA}/trajs_file_name_list.pkl', 'rb') as trajs_file_name_list_file:
        trajs_file_name_list = pickle.loads(trajs_file_name_list_file.read())

    awdp = adaptive_grid_construction_main(
        mdl_trajs_path=mdl_trajs_path.format(USE_DATA),
        epsilon=epsilon_alloc['mag'] * epsilon,
        n_grid_side=2,
        grid_lat_len=MDL_trajs_range[0][1] / 2,
        grid_lon_len=MDL_trajs_range[1][1] / 2,
        grid_tree_list_path=grid_tree_list_path.format(USE_DATA, epsilon),
        grid_trajs_path=grid_trajs_path.format(USE_DATA, epsilon),
        grid_tree_path=grid_tree_path.format(USE_DATA, epsilon)
    )

    n_grid = awdp[0][0]
    level_list = awdp[0][1]
    h_max = awdp[1]

    trip_distribution_main(n_grid, _epsilon=epsilon_alloc['tde'] * epsilon,
                           grid_trajs_path=grid_trajs_path.format(USE_DATA, epsilon),
                           trip_distribution_path=trip_distribution_path.format(USE_DATA, epsilon),
                           level_list=level_list)

    mobility_model_main(n_grid, _epsilon=epsilon_alloc['mmc'] * epsilon,
                        grid_trajs_path=grid_trajs_path.format(USE_DATA, epsilon),
                        midpoint_movement_path=midpoint_movement_path.format(USE_DATA, epsilon),
                        level_list=level_list, h_max=h_max)

    maxT = route_length_estimate_main(n_grid, _epsilon=epsilon_alloc['rle'] * epsilon,
                                      grid_trajs_path=grid_trajs_path.format(USE_DATA, epsilon),
                                      routes_length_path=length_traj_path.format(USE_DATA,
                                                                                 epsilon))

    synthetic_generate_trajs(grid_tree_path=grid_tree_path.format(USE_DATA, epsilon),
                             trip_distribution_path=trip_distribution_path.format(USE_DATA,
                                                                                  epsilon),
                             midpoint_movement_path=midpoint_movement_path.format(USE_DATA,
                                                                                  epsilon),
                             routes_length_path=length_traj_path.format(USE_DATA, epsilon),
                             sd_path=sd_path.format(USE_DATA, epsilon),
                             sd_desensitization_path=sd_desensitization_path.format(USE_DATA,
                                                                                    epsilon),
                             n_grid_side=n_grid, max_traj_len=maxT,
                             min_latitude=MIN_LAT_LON[USE_DATA][0],
                             min_longitude=MIN_LAT_LON[USE_DATA][1], nSyn=TRAJS_NUM[USE_DATA],
                             rate=MDL_SCALING_RATE[USE_DATA])

    prune_direction(sd_desensitization_path=sd_desensitization_path.format(USE_DATA, epsilon),
                    sd_desensitization_after_prune_direction_path=
                    sd_desensitization_after_prune_direction_path.format(USE_DATA, epsilon))

    prune_density(sd_desensitization_after_prune_direction_path=
                  sd_desensitization_after_prune_direction_path.format(USE_DATA, epsilon),
                  sd_final_path=sd_final_path.format(USE_DATA, epsilon),
                  min_latitude=MIN_LAT_LON[USE_DATA][0], min_longitude=MIN_LAT_LON[USE_DATA][1],
                  len_latitude=GPS_trajs_range[0][1] - GPS_trajs_range[0][0],
                  len_longitude=GPS_trajs_range[1][1] - GPS_trajs_range[1][0],
                  density_grid_side=18, trajs_file_name_list=trajs_file_name_list)


if __name__ == '__main__':
    Parallel(n_jobs=4)(delayed(run)(i) for i in epsilon_list)
