import os
import pickle
import random
import argparse
from utils.generation import *

parser = argparse.ArgumentParser(description='Create random mushroom scene')
parser.add_argument('--data_dir', type=str, default="data")
parser.add_argument('--mushroom_name', type=str, default="mushroom.obj")
parser.add_argument('--ground_dir', type=str, default="ground")
parser.add_argument('--min_number_of_mushrooms', type=int, default=30)
parser.add_argument('--max_number_of_mushrooms', type=int, default=60)
parser.add_argument('--position_bias', type=float, default=2.00)
parser.add_argument('--scale_min', type=float, default=0.50)
parser.add_argument('--scale_max', type=float, default=1.50)
parser.add_argument('--uneven_scale_min', type=float, default=0.85)
parser.add_argument('--uneven_scale_max', type=float, default=1.15)
parser.add_argument('--rotation_threshold', type=float, default=np.pi / 8)
parser.add_argument('--deformations', action='store_true', default=False)
parser.add_argument('--save_dir', type=str, default="scenes")
parser.add_argument('--scene_name', type=str, default='1')
parser.add_argument('--visualize', action='store_true', default=False)
args = parser.parse_args()

# Arguments
data_dir = args.data_dir
save_dir = args.save_dir
scene_name = args.scene_name
mushroom_name = args.mushroom_name
ground_dir = args.ground_dir
max_number_of_mushrooms = args.max_number_of_mushrooms
min_number_of_mushrooms = args.min_number_of_mushrooms
position_bias = args.position_bias
scale_min = args.scale_min
scale_max = args.scale_max
uneven_scale_min = args.uneven_scale_min
uneven_scale_max = args.uneven_scale_max
rotation_threshold = args.rotation_threshold
deformations = args.deformations
visualize = args.visualize

# Mushroom loading
mushroom_filename = os.path.join(data_dir, mushroom_name)
mushroom_mesh = o3d.io.read_triangle_mesh(mushroom_filename, True)
mushroom_mesh = mushroom_mesh.remove_unreferenced_vertices()
mushroom_mesh = mushroom_mesh.remove_duplicated_vertices()
mushroom_mesh.compute_vertex_normals()
mushroom_mesh.scale(0.005, center=mushroom_mesh.get_center())
mushroom_mesh.translate((0, 0, 0), relative=False)
if visualize:
    o3d.visualization.draw_geometries([mushroom_mesh])

# Ground loading
ground_dir = os.path.join(data_dir, ground_dir)
ground_choice = random.randint(1, 5)
ground_filename = 'ground_mesh_' + str(ground_choice) + '.obj'
ground_filename = os.path.join(ground_dir, ground_filename)
ground_mesh = o3d.io.read_triangle_mesh(ground_filename, True)
ground_mesh.translate((0, 0, 0), relative=False)
ground_mesh.scale(0.1, center=mushroom_mesh.get_center())
ground_mesh = l_deform(ground_mesh, voxel_size=0.015)
if visualize:
    o3d.visualization.draw_geometries([ground_mesh])

# Build scene
cultivation = []
scales, rotations, translations = [], [], []
transform = True
r_max = 0
cnt = 0
number_of_mushrooms = random.randint(min_number_of_mushrooms, max_number_of_mushrooms)
print('Creating a scene with', number_of_mushrooms, 'mushrooms...')
while cnt < number_of_mushrooms:
    mushroom = copy.deepcopy(mushroom_mesh)

    if transform:

        # Apply random transform : scale
        scale = round(random.uniform(scale_min, scale_max), 2)
        mushroom.scale(scale, center=mushroom.get_center())
        scales.append(scale)
        mushroom.translate((0, 0, scale * 0.3), relative=False)

        # Apply random transform : uneven scale
        uneven_scale_x = round(random.uniform(uneven_scale_min, uneven_scale_max), 2)
        uneven_scale_y = round(random.uniform(uneven_scale_min, uneven_scale_max), 2)
        uneven_scale_z = round(random.uniform(uneven_scale_min, uneven_scale_max), 2)
        mushroom.vertices = o3d.utility.Vector3dVector(
            np.asarray(mushroom.vertices) * np.array([uneven_scale_x, uneven_scale_y, uneven_scale_z]))

        # Apply random transform : rotation
        x_rot = round(random.uniform(-rotation_threshold, rotation_threshold), 2)
        y_rot = round(random.uniform(-rotation_threshold, rotation_threshold), 2)
        z_rot = round(random.uniform(-rotation_threshold, rotation_threshold), 2)
        R = mushroom.get_rotation_matrix_from_xyz((x_rot, y_rot, z_rot))
        mushroom.rotate(R, center=mushroom.get_center())
        rotations.append([x_rot, y_rot, z_rot])

        # Choose random position : translation
        x = round(random.uniform(-position_bias, position_bias), 2)
        y = round(random.uniform(-position_bias, position_bias), 2)

        mushroom.translate((x, y, 0))
        translations.append([x, y])
        r_max = compute_max_r(mushroom)

    # Check if a collision happened
    no_collision = True
    for j, previous_mushroom in enumerate(cultivation):
        if np.linalg.norm(mushroom.get_center() - previous_mushroom.get_center()) < \
           compute_max_r(previous_mushroom) + r_max:
            no_collision = False
            break

    if no_collision:
        if random.randint(0, 1) == 1:
            mushroom = l_deform(mushroom, use_normals=True, voxel_size=0.011)
        cultivation.append(mushroom)
        cnt += 1

# Get 3D bounding boxes of mushrooms
obb = []
for num, mushroom in enumerate(cultivation):
    bb = mushroom.get_oriented_bounding_box()
    cup_bb = find_cup(bb)
    obb.append(cup_bb)

# Add ground mesh to scene
cultivation.append(ground_mesh)
if visualize:
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    for pcd in cultivation:
        vis.add_geometry(pcd)
    for pcd in obb:
        vis.add_geometry(pcd)
    opt = vis.get_render_option()
    opt.background_color = np.asarray([90 / 255, random.randint(59, 69) / 255, random.randint(46, 56) / 255])
    vis.run()
    vis.destroy_window()
    o3d.visualization.draw_geometries(cultivation + obb)

print('Finished creating scene...')

# Save scene
scene_path = os.path.join(save_dir, scene_name)
os.mkdir(scene_path)
print('Saving in', scene_path, '...')
bb_path = os.path.join(scene_path, 'bb')
os.mkdir(bb_path)
for n, every in enumerate(cultivation):
    name = str(n+1) + '.obj'
    save_path = os.path.join(scene_path, name)
    o3d.io.write_triangle_mesh(save_path, every, write_triangle_uvs=True, print_progress=True)
    if n < len(obb):
        obb_name = str(n + 1) + 'bb.pkl'
        bb_save_path = os.path.join(bb_path, obb_name)
        dictionary = {'center': obb[n].center, 'R': obb[n].R, 'extent': obb[n].extent,
                      'points': np.asarray(obb[n].get_box_points())}
        f = open(bb_save_path, "wb")
        pickle.dump(dictionary, f)
        f.close()
