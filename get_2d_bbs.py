import argparse
import os
from natsort import natsorted
from utils.generation import *
from utils.render import *
import pickle


parser = argparse.ArgumentParser(description='Get 2d bounding boxes')
parser.add_argument('--scene_dir', type=str, default="scenes")
parser.add_argument('--scene_name', type=str, default='1')
args = parser.parse_args()

scene_path = os.path.join(args.scene_dir, args.scene_name)
bb_path = os.path.join(scene_path, 'bb')
bbs_files = natsorted(os.listdir(bb_path))
bbs_files = [os.path.join(bb_path, file) for file in bbs_files]
data = []
for bbs_file in bbs_files:
    with open(bbs_file, 'rb') as f:
        data.append(pickle.load(f)['points'])


viewpoints_path = 'data/vp'  # ready_viewpoints
viewpoints = natsorted(os.listdir(viewpoints_path))
viewpoints = [os.path.join(viewpoints_path, vp) for vp in viewpoints]
selected_viewpoints = os.path.join(scene_path, 'selected_viewpoints.npy')
selected_viewpoints = np.load(selected_viewpoints)
selected_viewpoints = [viewpoints[index] for index in selected_viewpoints]

os.mkdir(os.path.join(scene_path, '2d_bb'))
bb_dir = os.path.join(scene_path, '2d_bb')
for i, viewpoint in enumerate(selected_viewpoints):
    param = o3d.io.read_pinhole_camera_parameters(viewpoint)
    os.mkdir(os.path.join(bb_dir, str(i+1)))
    save_dir = os.path.join(bb_dir, str(i+1))
    find_2d_bb(data, param, save_dir)
