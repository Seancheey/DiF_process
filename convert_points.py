import pandas as pd
from pandas import DataFrame
import numpy as np
from functools import reduce
import os.path
from math import cos, sin, pi
from argparse import ArgumentParser

parser = ArgumentParser(description="python script to convert DiF points to separated csv points file")
parser.add_argument('-s', '--start', help="start line number", default=1, required=True)
parser.add_argument('-n', '--num', help='number of points to convert', default=100, required=True)
parser.add_argument('-o', '--output', help='destination folder to store points', default='DiF/points',
                    required=True)
parser.add_argument('-i', '--input', help='input csv file or pkl file to read', default='DiF/DiF_v1.csv',
                    required=False)
parser.add_argument('--rotation', help='do rotation augmentation', action='store_true')
parser.add_argument('--translation', help='do translation augmentation', action='store_true')
parser.add_argument('--gaussian', help='do gaussian shading augmentation', action='store_true')

args = parser.parse_args()

START_LINE = int(args.start)
CONVERT_NUM = int(args.num)
csv_file_path = args.input
points_dir_path = args.output

pkl_file_path = 'DiF_v1_dataframe.pkl'

table_cols = ['id', 'url', 'width', 'height', 'box_x1', 'box_y1', 'box_x2', 'box_y2'] + \
             reduce(lambda x, y: x + y, [['p_x%d' % i, 'p_y%d' % i] for i in range(1, 69)]) + \
             ['col%d' % i for i in range(1, 48)]


def col_name(prefix, point_id, rot_id):
    return "%s%d-%02d" % (prefix, point_id, rot_id)


def rotate(points, angle):
    if angle != 0:
        theta = -angle * pi / 180
        rotation_mat = np.matrix(((cos(theta), -sin(theta)),
                                  (sin(theta), cos(theta))))
        return (points - 64) * rotation_mat + 64
    else:
        return points


def translate_x(points, offset):
    return points - (offset, 0)


def translate_y(points, offset):
    return points - (0, offset)


augmentations = ((lambda x, y: x, 0),
                 (rotate, 10),
                 (rotate, 20),
                 (rotate, -10),
                 (rotate, -20),
                 (translate_x, 10),
                 (translate_x, -10),
                 (translate_y, 10),
                 (translate_y, -10),
                 (lambda x, y: x, 0)
                 )


def main():
    if os.path.isfile(pkl_file_path):
        print('reading DataFrame directly')
        table: DataFrame = pd.read_pickle(pkl_file_path).loc[START_LINE - 1:START_LINE + CONVERT_NUM - 2]
    else:
        print('reading csv file...')
        table: DataFrame = pd.read_csv(csv_file_path, sep=',', header=None, names=table_cols)
        table.to_pickle(pkl_file_path)
        table = table.loc[START_LINE - 1:START_LINE + CONVERT_NUM - 2]

    offset_matrix = table[['box_x1', 'box_y1']].to_numpy()
    size_matrix = table[['box_x2', 'box_y2']].to_numpy() - offset_matrix

    out_df = pd.DataFrame(table['id'])
    for id in range(1, 69):
        print('converting point set', id)
        xy_matrix = table[['p_x%d' % id, 'p_y%d' % id]].to_numpy()

        # non-augmented point set
        points = np.divide((xy_matrix - offset_matrix), size_matrix) * 128.0

        # for each augmentation, calculate their transformed points
        for aug_id, (aug_func, param) in enumerate(augmentations):
            augmented_pts = aug_func(points, param)
            out_df[col_name('x', id, aug_id)] = augmented_pts[:, 0]
            out_df[col_name('y', id, aug_id)] = augmented_pts[:, 1]

    if not os.path.isdir(points_dir_path):
        print('points path {} not detected, create the directory'.format(points_dir_path))
        os.mkdir(points_dir_path)

    for index, row in out_df.iterrows():
        face_id = row['id']

        for aug_id, _ in enumerate(augmentations):
            with open("%s/%07d-%02d.pts" % (points_dir_path, face_id, aug_id), 'w') as f:
                for pid in range(1, 69):
                    f.write(
                        '%.3f,%.3f\n' % (row[col_name('x', pid, aug_id)], row[col_name('y', pid, aug_id)]))


if __name__ == '__main__':
    main()
