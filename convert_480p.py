import pandas as pd
from pandas import DataFrame, read_csv
import numpy as np
import os.path
from matplotlib.image import imread as read_image
from matplotlib.image import imsave as save_image
import matplotlib.pyplot as plot
from matplotlib.patches import Rectangle
from urllib.request import urlretrieve
from random import randint, choice
from argparse import ArgumentParser
from skimage.transform import resize

__doc__ = 'convert pictures in DiF to 480x640 images with data augmentation'

TEST_MODE = False

START_LINE = 1
CONVERT_NUM = 100
INPUT_CSV_PATH = 'DiF/DiF_v1.csv'
IMAGE_BUFFER_PATH = 'full_images/'
OUTPUT_FOLDER = './'

CSV_BUFFER_PATH = 'DataFrameBuffer.pkl'

target_image_width = 480
target_image_height = 640
target_image_shape = (target_image_height, target_image_width, 3)
crop_ratio_range = [0.5, 0.6, 0.8, 1]


def crop_face(image, img_width, img_height, box_x1, box_y1, box_x2, box_y2):
    crop_area_ratio = choice(crop_ratio_range)
    crop_width = int(target_image_width * crop_area_ratio)
    crop_height = int(target_image_height * crop_area_ratio)
    crop_shape = (crop_height, crop_width, 3)
    # crop area is bigger
    if img_width < crop_width and img_height < crop_height:
        # apply zero padding, put image on the middle
        pad = np.zeros(crop_shape, dtype=np.uint8)
        x_offset = (crop_width - img_width) // 2
        y_offset = (crop_height - img_height) // 2
        pad[y_offset:img_height + y_offset, x_offset:img_width + x_offset, :] = image
    elif img_width < crop_width:
        pad = np.zeros(crop_shape, dtype=np.uint8)
        x_offset = (crop_width - img_width) // 2
        possible_yoff_start = max([0, box_y2 - crop_height])
        possible_yoff_end = min([img_height - crop_height, box_y1])
        y_offset = randint(possible_yoff_start, possible_yoff_end)
        pad[:, x_offset:x_offset + img_width, :] = image[y_offset:y_offset + crop_height, :, :]
        y_offset = -y_offset
    elif img_height < crop_height:
        pad = np.zeros(crop_shape, dtype=np.uint8)
        y_offset = (crop_height - img_height) // 2
        possible_xoff_start = max([0, box_x2 - crop_width])
        possible_xoff_end = min([img_width - crop_width, box_x1])
        x_offset = randint(possible_xoff_start, possible_xoff_end)
        pad[y_offset:y_offset + img_height, :, :] = image[:, x_offset:x_offset + crop_width, :]
        x_offset = -x_offset
    else:
        # usual case when image > 480x640, select a random place to get a 480x640 image containing the face
        possible_xoff_start = max([0, box_x2 - crop_width])
        possible_xoff_end = min([img_width - crop_width, box_x1])
        possible_yoff_start = max([0, box_y2 - crop_height])
        possible_yoff_end = min([img_height - crop_height, box_y1])
        x_offset = randint(possible_xoff_start, possible_xoff_end)
        y_offset = randint(possible_yoff_start, possible_yoff_end)
        pad = image[y_offset:y_offset + crop_height, x_offset:x_offset + crop_width, :]
        x_offset, y_offset = -x_offset, -y_offset

    out_image = resize(pad, output_shape=target_image_shape)
    return out_image, x_offset, y_offset, crop_area_ratio


def produce_positive_data(row, image):
    # extract information
    face_id, url, img_width, img_height, box_x1, box_x2, box_y1, box_y2 = \
        row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
    # find a random place to crop face
    image, x_off, y_off, ratio = crop_face(image, img_width, img_height, box_x1, box_y1, box_x2, box_y2)
    # output image
    out_image_path = os.path.join(OUTPUT_FOLDER, '%07d-01.png' % face_id)
    save_image(out_image_path, image)
    # create point data with offset
    points = (np.asarray(row[5:145]).reshape((70, 2)) + (x_off, y_off)) / ratio
    # output content: id, classification, bounding box, landmarks
    out_points_path = os.path.join(OUTPUT_FOLDER, "%07d-01.pts" % face_id)
    with open(out_points_path, 'w') as file:
        file.write('1,0\n')
        for point in points:
            file.write('{},{}\n'.format(point[0], point[1]))


def try_download(url, folder):
    """
    :param url: url for the image
    :param folder: where to put the image
    :return: image path
    """
    image_path = os.path.join(folder, str(url).split('/')[-1])
    if not os.path.isfile(image_path):
        print('image with path {} not present. downloading from {}'.format(image_path, url))
        urlretrieve(url, filename=image_path)
    return image_path


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
    assert os.path.isfile(INPUT_CSV_PATH)
    # first construct folders if not present
    if not os.path.isdir(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)
    if not os.path.isdir(IMAGE_BUFFER_PATH):
        os.mkdir(IMAGE_BUFFER_PATH)

    # read data into memory
    table = read_dataset(START_LINE, CONVERT_NUM)

    # for each row, convert data
    for row in table.itertuples():
        url = row[2]
        image_name = try_download(url, IMAGE_BUFFER_PATH)
        if os.path.isfile(image_name):
            image = read_image(image_name)
            produce_positive_data(row, image)
        else:
            raise AssertionError('file with name {} should exist but not found'.format(image_name))


def test_convert():
    global START_LINE, CONVERT_NUM, OUTPUT_FOLDER, IMAGE_BUFFER_PATH, INPUT_CSV_PATH
    START_LINE = 1
    CONVERT_NUM = 10
    OUTPUT_FOLDER = './output'
    IMAGE_BUFFER_PATH = '/Volumes/SeanSSD/DiF/DiF_1/images/'
    INPUT_CSV_PATH = '/Users/seancheey/Downloads/DiF/DiF_v1.csv'
    main()


def test_output(image_path: str):
    """
    :param image_path:
    :return:
    >>> test_output('output/0000004-01.png')
    """
    points_path = image_path.replace('.png', '.pts')
    assert os.path.isfile(image_path)
    assert os.path.isfile(points_path)
    image = read_image(image_path)
    m = read_csv(points_path, header=None).values
    print(m)
    classification = m[0, 0]
    bounding_box = m[1:3, :]
    landmarks = m[3:71, :]
    plot.imshow(image)
    for xs, ys in _face_segments(landmarks):
        plot.plot(xs, ys, color='cyan', linewidth=0.5)
    plot.gca().add_patch(
        Rectangle(bounding_box[0], bounding_box[1, 0] - bounding_box[0, 0], bounding_box[1, 1] - bounding_box[0, 1],
                  fill=False))
    plot.show()


def _face_segments(points):
    yield points[0:17, 0], points[0:17, 1]
    yield points[17:27, 0], points[17:27, 1]
    yield points[27:36, 0], points[27:36, 1]
    yield points[36:42, 0], points[36:42, 1]
    yield points[42:48, 0], points[42:48, 1]
    yield points[48:68, 0], points[48:68, 1]


if __name__ == '__main__':
    if TEST_MODE:
        test_convert()
    else:
        parser = ArgumentParser(description="python script to convert DiF points to separated csv points file")
        parser.add_argument('-s', '--start', help="start line number", default=START_LINE, required=True)
        parser.add_argument('-n', '--num', help='number of points to convert', default=CONVERT_NUM, required=True)
        parser.add_argument('-c', '--csv', help='input csv file or pkl file to read', default=INPUT_CSV_PATH,
                            required=False)
        parser.add_argument('-b', '--buffer', help='buffer image folder', default=IMAGE_BUFFER_PATH, required=False)
        parser.add_argument('-o', '--output', help='destination folder to store points', required=True)

        args = parser.parse_args()
        START_LINE = int(args.start)
        CONVERT_NUM = int(args.num)
        INPUT_CSV_PATH = args.csv
        IMAGE_BUFFER_PATH = args.buffer
        OUTPUT_FOLDER = args.output
        main()
