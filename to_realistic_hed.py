from share import *
from utils import config
import cv2
import os
import json
import einops
import numpy as np
import torch
import random
import argparse
from utils.MushroomDataset import MushroomDataset
from pytorch_lightning import seed_everything
from annotator.util import resize_image, HWC3
from annotator.hed import HEDdetector
from cldm.model import create_model, load_state_dict
from cldm.ddim_hacked import DDIMSampler
from utils.realistic import *


def get_map(input_image, detect_resolution=384, image_resolution=512):
    with torch.no_grad():
        input_image = HWC3(input_image)
        detected_map = apply_hed(resize_image(input_image, detect_resolution))
        detected_map = HWC3(detected_map)
        img = resize_image(input_image, image_resolution)
        h, w, c = img.shape

        detected_map = cv2.resize(detected_map, (w, h), interpolation=cv2.INTER_LINEAR)
    return detected_map, h, w


def process(detected_map, h, w, prompt, strength, scale, seed, ddim_steps=20, num_samples=1,
            guess_mode=False, eta=0.0, a_prompt='best quality, extremely detailed',
            n_prompt='longbody, lowres, bad anatomy, bad hands, missing fingers,'
                     'extra digit, fewer digits, cropped, worst quality, low quality'):
    with torch.no_grad():
        control = torch.from_numpy(detected_map[:, :, ::-1].copy()).float().cuda() / 255.0
        control = torch.stack([control for _ in range(num_samples)], dim=0)
        control = einops.rearrange(control, 'b h w c -> b c h w').clone()

        if seed == -1:
            seed = random.randint(0, 65535)
        seed_everything(seed)

        cond = {"c_concat": [control],
                "c_crossattn": [model.get_learned_conditioning([prompt + ', ' + a_prompt] * num_samples)]}
        un_cond = {"c_concat": None if guess_mode else [control],
                   "c_crossattn": [model.get_learned_conditioning([n_prompt] * num_samples)]}
        shape = (4, h // 8, w // 8)

        model.control_scales = [strength * (0.825 ** float(12 - i)) for i in range(13)]\
            if guess_mode else ([strength] * 13)
        samples, intermediates = ddim_sampler.sample(ddim_steps, num_samples,
                                                     shape, cond, verbose=False, eta=eta,
                                                     unconditional_guidance_scale=scale,
                                                     unconditional_conditioning=un_cond)

        x_samples = model.decode_first_stage(samples)
        x_samples = (einops.rearrange(x_samples, 'b c h w -> b h w c') * 127.5 + 127.5)\
            .cpu().numpy().clip(0, 255).astype(np.uint8)

        results = [x_samples[i] for i in range(num_samples)]
    return [detected_map] + results


parser = argparse.ArgumentParser(description='Generate realistic images')
parser.add_argument('--save_dir', type=str, default="RealisticDataset")
parser.add_argument('--start', type=int, default=9000)  # start saving images from start.png
parser.add_argument('--images_per_image', type=int, default=3)
args = parser.parse_args()

save_dir = args.save_dir

apply_hed = HEDdetector()
dataset = MushroomDataset()

torch.cuda.set_device(0)
model = create_model('./models/cldm_v15.yaml').cpu()
model.load_state_dict(load_state_dict('./models/control_sd15_normal.pth', location='cuda'))
model = model.cuda()
ddim_sampler = DDIMSampler(model)

if not os.path.exists(save_dir):
    os.mkdir(save_dir)
source_dir = os.path.join(save_dir, 'source')
maps_dir = os.path.join(save_dir, 'maps')
results_dir = os.path.join(save_dir, 'results')
jsons_dir = os.path.join(save_dir, 'jsons')
if not os.path.exists(source_dir):
    os.mkdir(source_dir)
if not os.path.exists(maps_dir):
    os.mkdir(maps_dir)
if not os.path.exists(results_dir):
    os.mkdir(results_dir)
if not os.path.exists(jsons_dir):
    os.mkdir(jsons_dir)

n = args.start
for k in range(0, len(dataset)):
    data = dataset[k]
    im, name = data['source'], data['name']
    map, h_, w_ = get_map(input_image=im)
    for j in range(args.images_per_image):
        seed_, strength_, scale_, prompt_ = get_random_params()
        dict_ = {'source': name, 'prompt': prompt_,
                 'seed': seed_, 'strength': strength_, 'scale': scale_}
        _, result = process(detected_map=map, h=h_, w=w_, prompt=prompt_, strength=strength_, scale=scale_, seed=seed_)
        cv2.imwrite(os.path.join(source_dir, str(n) + '.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        cv2.imwrite(os.path.join(maps_dir, str(n) + '.png'), cv2.cvtColor(map, cv2.COLOR_RGB2BGR))
        cv2.imwrite(os.path.join(results_dir, str(n) + '.png'), cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
        with open(os.path.join(jsons_dir, str(n) + '.json'), "w") as fp:
            json.dump(dict_, fp)
        n += 1
