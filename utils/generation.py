import numpy as np
import open3d as o3d
from scipy.interpolate import RBFInterpolator
import copy


def compute_max_r(obj):
    """
    Computes maximum radii of mesh object along x and y axis
    :param obj: an open3D mesh object
    :return: a tuple with the maximum radii along x and y axis (rx, ry)
    """
    r_x = max(abs(obj.get_center()[0] - obj.get_max_bound()[0]),
              abs(obj.get_center()[0] - obj.get_min_bound()[0]))
    r_y = max(abs(obj.get_center()[1] - obj.get_max_bound()[1]),
              abs(obj.get_center()[1] - obj.get_min_bound()[1]))
    max_r = max(r_x, r_y)
    return max_r


def find_cup(obb):
    """
    Given a mushroom mesh returns the oriented bounding box of the cup only
    :param obb: an open3D mushroom mesh object
    :return: an Open3D Oriented Bounding Box of the mushroom's cup
    """
    points = obb.get_box_points()
    # Split up and down points
    up_points = []
    down_points = []
    for point in points:
        if point[2] < obb.center[2]:
            down_points.append(point)
        else:
            up_points.append(point)

    # find pairs of up and down points
    d_1_0 = down_points[1] - down_points[0]
    d_2_1 = down_points[2] - down_points[1]
    n = np.cross(d_1_0, d_2_1)
    n_hat = n / np.linalg.norm(n)
    ordered = []
    for up_point in up_points:
        ordered.append(up_point)
        diff = []
        for down_point in down_points:
            diff_i = up_point - down_point
            diff_i_hat = diff_i / np.linalg.norm(diff_i)
            diff.append(abs(abs(np.inner(n_hat, diff_i_hat)) - 1))
        ind = np.argmin(diff)
        ordered.append(down_points[ind])

    # move down points
    k = 0.45
    new_points = []
    diff = ordered[0] - ordered[1]
    for i in range(0, len(ordered), 2):
        new_points.append(ordered[i])
        new_point = ordered[i+1] + k * diff
        new_points.append(new_point)

    new_pcd = o3d.geometry.PointCloud()
    new_pcd.points = o3d.utility.Vector3dVector(new_points)
    cup_obb = new_pcd.get_oriented_bounding_box()
    cup_obb.color = (0, 1, 0)
    return cup_obb


def l_deform(mesh, use_normals=False, voxel_size=0.014):
    """
    Deforms the surface of an Open3D mesh.
    :param mesh: an Open3D mesh object
    :param use_normals: if True move vertices proportionally to the normals values
    :param voxel_size: voxel_size
    :return: a new mesh object of the deformed initial mesh
    """
    vertices = np.asarray(mesh.vertices)
    k = int(0.05 * vertices.shape[0])
    rnd_idxs = np.random.choice(vertices.shape[0], k, replace=False)
    points_trgt = 1 * (np.random.uniform(size=(k, 1)) > 0.5).astype(float) * (np.random.uniform(size=(k, 3)) - 0.5)
    ppred = RBFInterpolator(vertices[rnd_idxs], points_trgt, kernel='thin_plate_spline', smoothing=10)(vertices)
    if use_normals:
        mesh.compute_vertex_normals()
        normals = np.asarray(mesh.vertex_normals)
        vertices += 100 * voxel_size * ppred * normals
    else:
        vertices += 100 * voxel_size * ppred
    new_mesh = copy.deepcopy(mesh)
    new_mesh.vertices = o3d.utility.Vector3dVector(vertices)
    return new_mesh
