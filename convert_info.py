import pandas as pd
from pandas import DataFrame
import numpy as np
from functools import reduce
import os.path

STOP_LIMIT = 100
csv_file_path = 'DiF/DiF_v1.csv'
pkl_file_path = 'DiF_v1_dataframe.pkl'
points_dir_path = 'DiF/points'

table_cols = ['id', 'url', 'width', 'height', 'box_x1', 'box_y1', 'box_x2', 'box_y2'] + \
             reduce(lambda x, y: x + y, [['p_x%d' % i, 'p_y%d' % i] for i in range(1, 69)]) + \
             ['col%d' % i for i in range(1, 48)]

if os.path.isfile(pkl_file_path):
    print('reading DataFrame directly')
    table: DataFrame = pd.read_pickle(pkl_file_path)
else:
    print('reading csv file...')
    table: DataFrame = pd.read_csv(csv_file_path, sep=',', header=None, names=table_cols)
    table.to_pickle(pkl_file_path)

offset_matrix = table[['box_x1', 'box_y1']].to_numpy()
size_matrix = table[['box_x2', 'box_y2']].to_numpy() - offset_matrix

out_df = pd.DataFrame(table['id'])
for i in range(1, 69):
    print('converting point set', i)
    xy_matrix = table[['p_x%d' % i, 'p_y%d' % i]].to_numpy()
    points = np.divide((xy_matrix - offset_matrix), size_matrix) * 128.0
    out_df['x%d' % i] = points[:, 0]
    out_df['y%d' % i] = points[:, 1]

if not os.path.isdir(points_dir_path):
    print('points path {} not detected, create the directory'.format(points_dir_path))
    os.mkdir(points_dir_path)

for n, row in enumerate(out_df.itertuples(), 1):
    if STOP_LIMIT != -1 and n > STOP_LIMIT:
        break
    with open('%s/%07d.pts' % (points_dir_path, row[1]), 'w') as f:
        for i in range(68):
            f.write('%.3f,%.3f\n' % (row[2 + i * 2], row[3 + i * 2]))
