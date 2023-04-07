import os
import numpy as np
from natsort import natsorted
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--scenes_dir', type=str, default="scenes")
parser.add_argument('--normals', action='store_true', default=False)
args = parser.parse_args()

if args.normals:
    ending = '_normals.jpg'
else:
    ending = '.jpg'

scenes_path = args.scenes_dir
scenes_paths = os.listdir(scenes_path)
scenes_paths = [os.path.join(scenes_path, path) for path in scenes_paths]
scenes_paths = natsorted(scenes_paths)

list_of_images = []
for scene_path in scenes_paths:
    selected_viewpoints = os.path.join(scene_path, 'selected_viewpoints.npy')
    selected_viewpoints = np.load(selected_viewpoints)
    for i in range(1, len(selected_viewpoints)):
        if selected_viewpoints[i - 1] not in [0, 12]:
            image_path = os.path.join(scene_path, 'images', str(i) + ending)
            list_of_images.append(image_path)
# print(list_of_images[0])
# print(len(list_of_images))
np.save('list_of_images.npy', list_of_images)
