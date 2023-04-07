import numpy as np
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon
from PIL import Image
import json
import os
import argparse


def create_sub_masks(mask_image):
    width, height = mask_image.size

    # Initialize a dictionary of sub-masks indexed by RGB colors
    sub_masks = {}
    for x in range(width):
        for y in range(height):
            # Get the RGB values of the pixel
            pixel = mask_image.getpixel((x, y))[:3]
            if pixel[0] > 240:
                sub_mask = sub_masks.get('(255, 255, 255)')
                if sub_mask is None:
                    sub_masks['(255, 255, 255)'] = Image.new('1', (width + 2, height + 2))
                sub_masks['(255, 255, 255)'].putpixel((x + 1, y + 1), 1)

    return sub_masks


def create_sub_mask_annotation(sub_mask, image_id, category_id, annotation_id, is_crowd):
    # Find contours (boundary lines) around each sub-mask
    sub_mask = np.array(sub_mask)
    contours = measure.find_contours(sub_mask, 0.5, positive_orientation='low')

    segmentations = []
    polygons = []
    for contour in contours:
        for i in range(len(contour)):
            row, col = contour[i]
            contour[i] = (col - 1, row - 1)

        poly = Polygon(contour)
        poly = poly.simplify(1.0, preserve_topology=False)
        polygons.append(poly)
        segmentation = np.array(poly.exterior.coords).ravel().tolist()
        segmentations.append(segmentation)

    multi_poly = MultiPolygon(polygons)
    x, y, max_x, max_y = multi_poly.bounds
    width = max_x - x
    height = max_y - y
    bbox = (x, y, width, height)
    area = multi_poly.area

    annotation = {
        'segmentation': segmentations,
        'iscrowd': is_crowd,
        'image_id': image_id,
        'category_id': category_id,
        'id': annotation_id,
        'bbox': bbox,
        'area': area
    }

    return annotation


parser = argparse.ArgumentParser()
parser.add_argument('--scene_dir', type=str, default="scenes")
parser.add_argument('--train_split', int=85, default="scenes")
args = parser.parse_args()


json_categories = [{'id': 0, 'name': 'mushroom'}]
json_images = []
json_annotations = []
test_images = []
test_annotations = []
mushroom_id = 0
category_ids = {'(255, 255, 255)': mushroom_id}
is_crowd_ = 0
annotation_id_ = 1
image_id_ = 1
scenes = os.listdir(args.scene_dir)
# scenes_paths = [os.path.join(args.scene_dir, sc) for sc in scenes]

for i in range(1, args.train_split):
    scene_path = args.scene_dir + '/scene' + str(i)
    print(i, scene_path)
    images_path = os.path.join(scene_path, 'images')
    visible_path = os.path.join(scene_path, 'visible')
    for j in range(1, 31):
        image_dir = os.path.join(images_path, str(i))
        im = Image.open(image_dir + '.jpg')
        image = {
            'file_name': image_dir + '.jpg',
            'height': im.size[1],
            'width': im.size[0],
            'id': image_id_
        }
        json_images.append(image)
        print(json_images[-1])
        visible_instances = np.load(os.path.join(visible_path, str(j) + '.npy'))
        mask_images = []
        for instance in visible_instances:
            mask_images.append(Image.open(os.path.join(image_dir, str(instance) + '.jpg')))

            # Create the annotations
        for mask_image_ in mask_images:
            # print(mask_image_)
            # print(mask_image_)
            sub_masks_ = create_sub_masks(mask_image_)
            # print(sub_masks_)
            for color, sub_mask_ in sub_masks_.items():
                category_id_ = category_ids[color]
                annotation_ = create_sub_mask_annotation(sub_mask_, image_id_,
                                                         category_id_, annotation_id_, is_crowd_)
                json_annotations.append(annotation_)
            annotation_id_ += 1
        image_id_ += 1

    # print(json_categories, json_images, json_annotations)
    out_file = open("train_data.json", "w")
    dictionary = {
        'images': json_images,
        'annotations': json_annotations,
        'categories': json_categories
    }
    json.dump(dictionary, out_file, indent=6)
    out_file.close()

for i in range(args.train_split, len(scenes)):
    scene_path = args.scene_dir + '/scene' + str(i)
    print(i, scene_path)
    images_path = os.path.join(scene_path, 'images')
    visible_path = os.path.join(scene_path, 'visible')
    for j in range(1, 31):
        image_dir = os.path.join(images_path, str(j))
        print(j, image_dir)
        im = Image.open(image_dir + '.jpg')
        image = {
            'file_name': image_dir + '.jpg',
            'height': im.size[1],
            'width': im.size[0],
            'id': image_id_
        }
        test_images.append(image)
        # print(json_images[-1])
        visible_instances = np.load(os.path.join(visible_path, str(j) + '.npy'))
        mask_images = []
        for instance in visible_instances:
            mask_images.append(Image.open(os.path.join(image_dir, str(instance) + '.jpg')))

            # Create the annotations
        for mask_image_ in mask_images:
            # print(mask_image_)
            # print(mask_image_)
            sub_masks_ = create_sub_masks(mask_image_)
            # print(sub_masks_)
            for color, sub_mask_ in sub_masks_.items():
                category_id_ = category_ids[color]
                annotation_ = create_sub_mask_annotation(sub_mask_, image_id_,
                                                         category_id_, annotation_id_, is_crowd_)
                test_annotations.append(annotation_)
            annotation_id_ += 1
        image_id_ += 1

    # print(json_categories, json_images, json_annotations)
    out_file = open("test_data.json", "w")
    dictionary = {
        'images': test_images,
        'annotations': test_annotations,
        'categories': json_categories
    }
    json.dump(dictionary, out_file, indent=6)
    out_file.close()
