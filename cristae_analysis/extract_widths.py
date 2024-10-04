import argparse
import os
import time
import numpy as np
import pandas as pd
from skimage import io
from skimage.morphology import medial_axis
from skimage.segmentation import find_boundaries
from scipy.spatial.distance import cdist

def calculate_widths(image_path, conversion_factor,measurement):
    start_time = time.time()

    try:
        image = io.imread(image_path)
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return {}

    unique_labels = np.unique(image)
    widths_dict = {}

    for label_id in unique_labels:
        if label_id == 0:
            continue

        object_mask = image == label_id
        skeleton = medial_axis(object_mask)

        border_mask = find_boundaries(object_mask, mode='inner')
        border_coords = np.array(np.where(border_mask)).T
        widths = cdist(np.argwhere(skeleton), border_coords).min(axis=1)
        if measurement == 'max':
            widths = np.max(widths) * 2 
        elif measurement == 'mean':
            widths = np.mean(widths) * 2
        else:    
            print('Error: measurement must be either max or mean')
            exit()
        #
        widths = np.round(widths * conversion_factor, 2)
        widths_dict[label_id] = widths.tolist()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processing {image_path} took {elapsed_time:.2f} seconds")

    return widths_dict

def main(folder_path, conversion_factor,measurement):
    widths_dict_list = []

    for filename in os.listdir(folder_path):
        if filename.endswith('_cristae.tif'):
            image_path = os.path.join(folder_path, filename)
            widths_dict = calculate_widths(image_path, conversion_factor,measurement)
            for label_id, widths in widths_dict.items():
                widths_dict_list.append([filename, label_id, np.mean(widths) * 2])

    df = pd.DataFrame(widths_dict_list, columns=['Filename', 'Label ID', 'Width (nm)'])
    df.to_csv(os.path.join(folder_path, 'mean_widths_medial_border.csv'), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract distance between medial axis and borders of labeled object from binary images and save to CSV')
    parser.add_argument('folder_path', type=str, help='Folder path of the binary images')
    parser.add_argument('conversion_factor', type=float, help='Conversion factor from pixels to nanometers')
    parser.add_argument('measurement', type=float, help='Choose between mean and max width of individual crista')
    args = parser.parse_args()

    main(args.folder_path, args.conversion_factor)
