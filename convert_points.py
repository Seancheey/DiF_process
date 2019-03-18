import pandas as pd
from pandas import DataFrame
import numpy as np
from functools import reduce
import os.path
from math import cos, sin, pi

STOP_LIMIT = 10000
csv_file_path = 'DiF/DiF_v1.csv'
pkl_file_path = 'DiF_v1_dataframe.pkl'
points_dir_path = 'DiF/points'
rotations = [(0, 0), (1, 10), (2, 20), (3, -10), (4, -20)]

table_cols = ['id', 'url', 'width', 'height', 'box_x1', 'box_y1', 'box_x2', 'box_y2'] + \
             reduce(lambda x, y: x + y, [['p_x%d' % i, 'p_y%d' % i] for i in range(1, 69)]) + \
             ['col%d' % i for i in range(1, 48)]


def col_name(prefix, point_id, rot_id):
    return "%s%d-%02d" % (prefix, point_id, rot_id)


if os.path.isfile(pkl_file_path):
    print('reading DataFrame directly')
    table: DataFrame = pd.read_pickle(pkl_file_path).head(STOP_LIMIT)
else:
    print('reading csv file...')
    table: DataFrame = pd.read_csv(csv_file_path, sep=',', header=None, names=table_cols)
    table.to_pickle(pkl_file_path)
    table = table.head(STOP_LIMIT)

offset_matrix = table[['box_x1', 'box_y1']].to_numpy()
size_matrix = table[['box_x2', 'box_y2']].to_numpy() - offset_matrix

out_df = pd.DataFrame(table['id'])
for id in range(1, 69):
    print('converting point set', id)
    xy_matrix = table[['p_x%d' % id, 'p_y%d' % id]].to_numpy()

    # non-augmented point set
    points = np.divide((xy_matrix - offset_matrix), size_matrix) * 128.0

    # for each angle, calculate their transformed points
    for rotation_id, angle in rotations:
        if angle != 0:
            theta = -angle * pi / 180
            rotation = np.matrix(((cos(theta), -sin(theta)),
                                  (sin(theta), cos(theta))))
            augmented_pts = (points - 64) * rotation + 64
        else:
            augmented_pts = points
        out_df[col_name('x', id, rotation_id)] = augmented_pts[:, 0]
        out_df[col_name('y', id, rotation_id)] = augmented_pts[:, 1]

if not os.path.isdir(points_dir_path):
    print('points path {} not detected, create the directory'.format(points_dir_path))
    os.mkdir(points_dir_path)

for index, row in out_df.iterrows():
    face_id = row['id']

    for rotation_id, angle in rotations:
        with open("%s/%07d-%02d.pts" % (points_dir_path, face_id, rotation_id), 'w') as f:
            for pid in range(1, 69):
                f.write('%.3f,%.3f\n' % (row[col_name('x', pid, rotation_id)], row[col_name('y', pid, rotation_id)]))
