#!/bin/bash
cd data
for i in {1..100}
do
	printf '%i\n' $i
	python scene_generation.py --deformations --scene_name scene$i
	python rendering.py --scene_name scene$i
	python get_2d_bbs.py --scene_name scene$i
	python find_visible_mushrooms.py --scene_name scene$i
done

python get_all_images_path.py
cd ControlNet
python to_realistic_normals.py 

