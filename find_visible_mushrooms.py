import os
import json
from natsort import natsorted
import argparse
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Create random mesh mushroom scene')
parser.add_argument('--scene_dir', type=str, default="scenes")
parser.add_argument('--scene_name', type=str, default='1')
args = parser.parse_args()


scene_path = os.path.join(args.scene_dir, args.scene_name)
images_path = os.path.join(scene_path, 'images')
visible_path = os.path.join(scene_path, 'visible')
if not os.path.exists(visible_path):
    os.mkdir(os.path.join(scene_path, 'visible'))
viewpoints = [d for d in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, d))]
viewpoints = natsorted(viewpoints)
viewpoints = [os.path.join(images_path, name) for name in viewpoints]
number = 1025 * 1853
for j, vp in enumerate(viewpoints):
    keep = []
    print(vp)
    objects = natsorted(os.listdir(vp))[:-1]
    objects = [os.path.join(vp, obj) for obj in objects]
    white_pixels = 0
    white_pixels_list = []
    count = 0
    for i, image_path in enumerate(objects):
        image = cv.imread(image_path)
        white_pixels_list.append(np.sum(image[:, :, 0]) / 255)
        if np.sum(image[:, :, 0]) / 255 != 0:
            count = count + 1
            white_pixels = white_pixels + np.sum(image[:, :, 0]) / 255
    white_pixels_mean = white_pixels / count
    for i, every in enumerate(white_pixels_list):
        if (100 * every / white_pixels_mean) > 15:
            keep.append(i+1)
    print(keep)
    np.save(os.path.join(visible_path, str(j+1) + '.npy'), keep)
