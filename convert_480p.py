import pandas as pd
from pandas import DataFrame
import numpy as np
import os.path
from matplotlib.image import imread as read_image
from matplotlib.image import imsave as save_image
from urllib.request import urlretrieve
from random import randint
from argparse import ArgumentParser

__doc__ = 'convert pictures in DiF to 480x640 images with data augmentation'

parser = ArgumentParser(description="python script to convert DiF points to separated csv points file")
parser.add_argument('-s', '--start', help="start line number", default=1, required=True)
parser.add_argument('-n', '--num', help='number of points to convert', default=100, required=True)
parser.add_argument('-o', '--output', help='destination folder to store points', default='DiF/points',
                    required=True)
parser.add_argument('-i', '--input', help='input csv file or pkl file to read', default='DiF/DiF_v1.csv',
                    required=False)

args = parser.parse_args()

START_LINE = int(args.start)
CONVERT_NUM = int(args.num)
INPUT_CSV_PATH = args.input
OUTPUT_FOLDER = args.output

CSV_BUFFER_PATH = 'DataFrameBuffer.pkl'

target_image_shape = (480, 640, 3)


def crop_face(image, img_width, img_height, box_x1, box_y1, box_x2, box_y2):
    # crop area is bigger
    if img_width < target_image_shape[0] or img_height < target_image_shape[1]:
        # apply zero padding, put image on the middle
        pad = np.zeros(target_image_shape)
        x_offset = (target_image_shape[0] - img_width) // 2
        y_offset = (target_image_shape[1] - img_height) // 2
        pad[x_offset:img_width + x_offset, y_offset:img_height + y_offset, :] = image
        return pad, x_offset, y_offset
    elif img_width < target_image_shape[0]:
        pad = np.zeros(target_image_shape)
        x_offset = (target_image_shape[0] - img_width) // 2
        possible_yoff_start = max([0, box_y2 - 640])
        possible_yoff_end = min([img_height, box_y1 + 640])
        y_offset = randint(possible_yoff_start, possible_yoff_end)
        pad[x_offset:x_offset + img_width, :, :] = image[:, y_offset:y_offset + 640, :]
        return pad, x_offset, -y_offset
    elif img_height < target_image_shape[1]:
        pad = np.zeros(target_image_shape)
        y_offset = (target_image_shape[1] - img_height) // 2
        possible_xoff_start = max([0, box_x2 - 480])
        possible_xoff_end = min([img_width, box_x1 + 480])
        x_offset = randint(possible_xoff_start, possible_xoff_end)
        pad[:, y_offset + img_height, :] = image[x_offset:x_offset + 480, :, :]
    else:
        # usual case when image > 480x640, select a random place to get a 480x640 image containing the face
        possible_xoff_start = max([0, box_x2 - 480])
        possible_xoff_end = min([img_width, box_x1 + 480])
        possible_yoff_start = max([0, box_y2 - 640])
        possible_yoff_end = min([img_height, box_y1 + 640])
        x_offset = randint(possible_xoff_start, possible_xoff_end)
        y_offset = randint(possible_yoff_start, possible_yoff_end)
        return image[x_offset:x_offset + 480, y_offset:y_offset + 640, :], -x_offset, -y_offset


def produce_positive_data(row, image):
    # extract information
    face_id, url, img_width, img_height, box_x1, box_x2, box_y1, box_y2 = \
        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
    # find a random place to crop face
    image, x_off, y_off = crop_face(image, img_width, img_height, box_x1, box_y1, box_x2, box_y2)
    # output image
    save_image(image, '%07d-01.png' % face_id)
    # create point data with offset
    points = np.asarray(row[4:144]).reshape((70, 2)) + (x_off, y_off)
    # line content: id, classification, bounding box, landmarks
    content = [1] + points
    # output content
    with open("%07d-01.pts" % face_id) as file:
        file.write('1\n')
        for point in points:
            file.write('{},{}\n'.format(point[0], point[1]))


def try_download(url):
    image_name = str(url).split('/')[-1]
    if not os.path.isfile(image_name):
        urlretrieve(url, filename=image_name)
    return image_name


def read_dataset(start, num):
    if os.path.isfile(CSV_BUFFER_PATH):
        print('reading DataFrame directly')
        return pd.read_pickle(CSV_BUFFER_PATH).loc[start - 1:start + num - 2]
    else:
        print('reading csv file...')
        table: DataFrame = pd.read_csv(INPUT_CSV_PATH, sep=',', header=None)
        table.to_pickle(CSV_BUFFER_PATH)
        return table.loc[start - 1:start + num - 2]


def main():
    table = read_dataset(START_LINE, CONVERT_NUM)
    for row in table.itertuples():
        url = row[1]
        image_name = try_download(url)
        if os.path.isfile(image_name):
            image = read_image(image_name)
            produce_positive_data(row, image)
        else:
            raise AssertionError('file with name {} should exist but not found'.format(image_name))


if __name__ == '__main__':
    main()
