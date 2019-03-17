import pandas as pd
import numpy as np
from functools import reduce

table_cols = ['id', 'url', 'width', 'height', 'box_x1', 'box_y1', 'box_x2', 'box_y2'] + \
             reduce(lambda x, y: x + y, [['p_x%d' % i, 'p_y%d' % i] for i in range(1, 69)]) + \
             ['col%d' % i for i in range(1, 48)]
table = pd.read_csv('DiF/DiF_v1.csv', sep=',', header=None, names=table_cols)

offset_matrix = table[['box_x1', 'box_y1']].to_numpy()
size_matrix = table[['box_x2', 'box_y2']].to_numpy() - offset_matrix

for i in range(1, 69):
    print('converting point set', i)
    xy_matrix = table[['p_x%d' % i, 'p_y%d' % i]].to_numpy()
    new_points = np.multiply((xy_matrix - offset_matrix), size_matrix) / 128.0
