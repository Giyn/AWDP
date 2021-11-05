"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : config.py
# @Software: PyCharm
-------------------------------------
"""

epsilon_list = [0.1, 0.5, 1.0, 2.0]

# budget allocation
epsilon_alloc = {
    'mag': (1 / 9),  # multilevel adaptive grid construction
    'tde': (3 / 9),  # trip distribution extraction
    'mmc': (4 / 9),  # mobility model construction
    'rle': (1 / 9)  # route length estimation(a median length estimation method)
}

DATASET_LIST = ['Geolife Trajectories 1.3',
                'Brinkhoff',
                'Guangzhou Taxi_30_six_hours',
                'Guangzhou Taxi_60_six_hours'
                ]

MIN_LAT_LON = {'Geolife Trajectories 1.3': [39.4, 115.7],
               'Brinkhoff': [6.558, 0.468],
               'Guangzhou Taxi_30_six_hours': [21.2554, 110.0],
               'Guangzhou Taxi_60_six_hours': [21.2554, 110.0]
               }

MDL_SCALING_RATE = {'Geolife Trajectories 1.3': 1100,
                    'Brinkhoff': 300,
                    'Guangzhou Taxi_30_six_hours': 500,
                    'Guangzhou Taxi_60_six_hours': 500
                    }

TRAJS_NUM = {'Geolife Trajectories 1.3': 14650,
             'Brinkhoff': 50000,
             'Guangzhou Taxi_30_six_hours': 30000,
             'Guangzhou Taxi_60_six_hours': 30000,
             }

USE_DATA = DATASET_LIST[0]
