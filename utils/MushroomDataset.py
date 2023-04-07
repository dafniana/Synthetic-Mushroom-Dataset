import json
import cv2
import numpy as np

from torch.utils.data import Dataset


class MushroomDataset(Dataset):
    def __init__(self):
        self.data = np.load('list_of_mushroom_images.npy')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        source_filename = self.data[idx]
        print(source_filename)
        name = source_filename.split('/')
        idx = name[-3] + '_image' + name[-1]
        source = cv2.imread(source_filename)
        # Do not forget that OpenCV read images in BGR order.
        source = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
        # source = cv2.resize(source, (256, 256))
        # Normalize source images to [0, 1].
        # source = source.astype(np.float32) / 255.0
        return {'source': source, 'name': idx}


if __name__ == '__main__':
    dataset = MushroomDataset()
    print(len(dataset))

    data = dataset[1234]
    print(data['source'].shape)
    print(data['name'])
