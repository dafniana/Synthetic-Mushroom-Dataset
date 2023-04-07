import argparse
import os
import json
from natsort import natsorted
import random
from utils.generation import *
from utils.render import *

parser = argparse.ArgumentParser(description='Render images from a scene')
parser.add_argument('--scene_dir', type=str, default="scenes")
parser.add_argument('--scene_name', type=str, default='1')
parser.add_argument('--images_number', type=int, default=30)
parser.add_argument('--visualize', action='store_true', default=False)
args = parser.parse_args()

images_number = args.images_number
visualize = args.visualize
scene_dir = args.scene_dir
scene_name = args.scene_name
scene_path = os.path.join(scene_dir, scene_name)
scene = []
texture_less_scene = []
objs = os.listdir(scene_path)
objects = []
obb = []
for every in objs:
    if every[-3:] == 'obj':
        objects.append(every)
objects = natsorted(objects)
for every in objects:
    read_path = os.path.join(scene_path, every)
    obj_ = o3d.io.read_triangle_mesh(read_path, True)
    texture_less_obj_ = o3d.io.read_triangle_mesh(read_path)
    texture_less_obj_.paint_uniform_color([0, 0, 0])
    if int(every[:-4]) != len(objects):
        obj_.compute_vertex_normals()
        bb = obj_.get_oriented_bounding_box()
        cup_bb = find_cup(bb)
        obb.append(cup_bb)
    scene.append(obj_)
    texture_less_scene.append(texture_less_obj_)
    obb.append(obj_)

if visualize:
    o3d.visualization.draw_geometries(scene)

viewpoints_path = 'data/vp'  # ready_viewpoints
viewpoints = os.listdir(viewpoints_path)
viewpoints = natsorted(viewpoints)
choices = random.sample(range(0, len(viewpoints) - 1), images_number)
viewpoints = [viewpoints[x] for x in choices]
np.save(os.path.join(scene_path, 'selected_viewpoints.npy'), choices)
print(viewpoints)
viewpoints = [os.path.join(viewpoints_path, viewpoint)
              for viewpoint in viewpoints]

# render images
for i, viewpoint in enumerate(viewpoints):
    print('Rendering image:', i)
    images_path = os.path.join(scene_path, 'images')
    if not os.path.exists(images_path):
        os.mkdir(images_path)
    f = open(viewpoint)
    data = json.load(f)
    height = data["intrinsic"]["height"]
    width = data["intrinsic"]["width"]
    f.close()
    img_name = os.path.join(images_path, str(i+1) + '.jpg')
    img_name_bb = os.path.join(images_path, str(i + 1) + 'normals.jpg')
    colors = [[46, 34, 23], [105, 89, 73], [48, 32, 16], [36, 24, 11],
              [43, 32, 20], [92, 64, 51], [20, 18, 15], [46, 34, 23]]
    color = colors[random.randint(0, 7)]
    background_color = [(color[0] + random.randint(-2, 2)) / 255,
                        (color[1] + random.randint(-2, 2)) / 255,
                        (color[2] + random.randint(-2, 2)) / 255]
    param_ = load_view_point(scene, viewpoint, height, width, img_name, background_color)
    load_view_point(scene, viewpoint, height, width, img_name_bb, background_color)
    load_view_point(scene, viewpoint, height, width, img_name_bb, background_color, normals=True)
    # uncomment next line if you want to render image with bounding boxes
    # load_view_point(obb, viewpoint, height, width, img_name_bb, background_color)
    viewpoint_folder = os.path.join(images_path, str(i + 1))
    if not os.path.exists(viewpoint_folder):
        os.mkdir(viewpoint_folder)
    for j, mushroom in enumerate(texture_less_scene):
        if isinstance(texture_less_scene[j], o3d.cpu.pybind.geometry.OrientedBoundingBox):
            points = np.asarray(texture_less_scene[j].get_box_points())
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            load_view_point([pcd], viewpoint, height, width,
                            os.path.join(images_path, str(i + 1) + 'pcd_bb.jpg'), [0, 0, 0])
        else:
            img_name = os.path.join(viewpoint_folder, str(j + 1) + '.jpg')
            texture_less_scene[j].paint_uniform_color([1, 1, 1])
            load_view_point(texture_less_scene, viewpoint, height, width, img_name, [0, 0, 0])
            texture_less_scene[j].paint_uniform_color([0, 0, 0])
