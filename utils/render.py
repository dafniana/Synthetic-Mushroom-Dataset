import numpy as np
import open3d as o3d


def load_view_point(pcd, filename, height_, width_, img_name_, bc, normals=False):
    """
    Given the path of a viewpoint and a 3D scene renders and saves
    either RGB or normal image of that scene from that viewpoint
    :param pcd: list of meshes that exist in the 3D scene
    :param filename: path of Open3D viewpoint
    :param height_: height of image to render
    :param width_: render of image to render
    :param img_name_: path to save image
    :param bc: RGB background of image to render
    :param normals: if True render a normals image
    :return: the parameters of the viewpoint
    """
    vis_ = o3d.visualization.Visualizer()
    vis_.create_window(height=height_, width=width_, visible=False)
    ctr = vis_.get_view_control()
    param = o3d.io.read_pinhole_camera_parameters(filename)
    for every_object_ in pcd:
        vis_.add_geometry(every_object_)
    ctr.convert_from_pinhole_camera_parameters(param)
    param = ctr.convert_to_pinhole_camera_parameters()
    if not normals:
        opt = vis_.get_render_option()
        opt.background_color = np.asarray(bc)
        opt.light_on = True
    else:
        vis_.get_render_option().mesh_color_option = o3d.visualization.MeshColorOption.Normal
    vis_.poll_events()
    vis_.update_renderer()
    vis_.capture_screen_image(img_name_, do_render=True)
    vis_.destroy_window()
    return param


def save_view_point(pcd, filename):
    """
    Saves the viewpoint that the user creates
    :param pcd: list of meshes that exist in a 3D scene
    :param filename: path to save the viewpoint
    """
    vis_ = o3d.visualization.Visualizer()
    vis_.create_window()
    for every_object_ in pcd:
        vis_.add_geometry(every_object_)
    opt = vis_.get_render_option()
    opt.background_color = np.asarray([152 / 255, 118 / 255, 84 / 255])
    vis_.run()  # user changes the view and press "q" to terminate
    param = vis_.get_view_control().convert_to_pinhole_camera_parameters()
    o3d.io.write_pinhole_camera_parameters(filename, param)
    vis_.destroy_window()

