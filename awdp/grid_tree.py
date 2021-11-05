"""
-------------------------------------
# -*- coding: utf-8 -*-
# @File    : grid_tree.py
# @Software: PyCharm
-------------------------------------
"""


class Node:
    def __init__(self, start_lat=0, start_lon=0, end_lat=0, end_lon=0, is_end=False, number=-1,
                 level=0):
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.end_lat = end_lat
        self.end_lon = end_lon
        self.is_end = is_end
        self.number = number
        self.children = []
        self.level = level


class GridTree:
    def __init__(self, start_lat, start_lon, end_lat, end_lon):
        self.root = Node(start_lat, start_lon, end_lat, end_lon, is_end=False)

    def add_nodes(self, root: Node, grid_tree_list: list, n_grid: int, lat_init: float,
                  lon_init: float, level: int, start_base: tuple):
        C = n_grid * n_grid

        for i in range(C):
            lat = lat_init
            lon = lon_init
            row = int(i / n_grid)
            col = i - row * n_grid

            # first level child nodes
            start_position = (row * lat + start_base[0], col * lon + start_base[1])
            end_position = ((row + 1) * lat + start_base[0], (col + 1) * lon + start_base[1])

            now_node = Node(start_position[0], start_position[1],
                            end_position[0], end_position[1], True, -1, level)
            root.children.append(now_node)

            # whether to generate a subtree down
            if type(grid_tree_list[i]) == list:
                now_node.is_end = False
                self.add_nodes(now_node, grid_tree_list[i], n_grid, lat_init / 2, lon_init / 2,
                               level + 1, start_position)

    @staticmethod
    def print_node(node):
        print(
            'start_range:', (node.start_lat, node.start_lon),
            'end_range:', (node.end_lat, node.end_lon),
            'is_end:', node.is_end,
            'number:', node.number,
            'level:', node.level
        )

    def set_num(self, root, count):
        children_list = root.children

        for i in range(len(children_list)):
            child = children_list[i]

            if child.is_end:
                child.number = count
                count += 1
            else:
                count = self.set_num(child, count)

        return count

    def find_node_by_level(self, level):
        root = self.root
        back_arr = [root]
        ret_arr = []
        while len(back_arr) != 0:
            now_node = back_arr[0]
            back_arr = back_arr[1:]
            if now_node.level < level:
                back_arr.extend(now_node.children)

            if now_node.level == level:
                ret_arr.append(now_node)

        for node in ret_arr:
            self.print_node(node)

    def position_to_num(self, pos, node=None):
        pos_lat = pos[0]
        pos_lon = pos[1]
        if node is None:
            root = self.root.children
        else:
            root = Node

        while True:
            for item in root:
                if (item.start_lat <= pos_lat <= item.end_lat) and \
                        (item.start_lon <= pos_lon <= item.end_lon):
                    if item.is_end:
                        return item.number
                    else:
                        root = item.children
                        break

    def num_to_position(self, num):
        root = self.root.children
        back_arr = root.copy()

        while len(back_arr):
            now_node = back_arr[0]
            back_arr = back_arr[1:]
            if now_node.number == num:
                return now_node
            else:
                if now_node.is_end is not True:
                    back_arr.extend(now_node.children)


if __name__ == '__main__':
    grid_tree_test = GridTree(0, 0, 1, 1)
    grid_tree_test.add_nodes(grid_tree_test.root,
                             [[1, 1, 1, 1], 1, 1, 1],
                             2, (1920 + 120) // 2, (2397 + 240) // 2, 1, (0, 0))

    grid_tree_test.set_num(grid_tree_test.root, 1)

    grid_tree_test.find_node_by_level(0)
    grid_tree_test.find_node_by_level(1)
    grid_tree_test.find_node_by_level(2)

    print(grid_tree_test.position_to_num((512, 1021)))
    grid_tree_test.print_node(grid_tree_test.num_to_position(4))
