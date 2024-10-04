import os
import cv2
import numpy as np
from tk_r_em import load_network
import tkinter as tk
from tkinter import filedialog

import tensorflow as tf
tf.config.run_functions_eagerly(True)

def fcn_set_gpu_id(gpu_visible_devices: str = "0") -> None:
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ['CUDA_VISIBLE_DEVICES'] = gpu_visible_devices

fcn_set_gpu_id("0")

def fcn_inference(x, net_name):
    """
    Perform inference on test data using a pre-trained model.
    Args:
        x (numpy.ndarray): Input data.
        net_name (str): Name of the network.
    Returns:
        y_p (numpy.ndarray): Predicted output.
    """
    r_em_nn = load_network(net_name)
    r_em_nn.summary()

    y_p = r_em_nn.predict_patch_based(x, patch_size=128, stride=128, batch_size=8)

    return y_p

def process_tif_folder(input_folder, output_folder):
    """
    Process a folder containing TIF files, perform inference, and save the output as 8-bit grayscale TIF files.
    
    Args:
        input_folder (str): Path to the folder containing input TIF files.
        output_folder (str): Path to the folder where output TIF files will be saved.
    """

    os.makedirs(output_folder, exist_ok=True)
    
    # List all files in the input folder
    tif_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]
    
    for tif_file in tif_files:
        input_path = os.path.join(input_folder, tif_file)
        input_image = cv2.imread(input_path, cv2.IMREAD_ANYDEPTH)
        net_name = 'sfr_lrtem' 
        output_image = fcn_inference(input_image, net_name)
        
        # Normalize the output image to [0, 255] range
        output_image = ((output_image - output_image.min()) / (output_image.max() - output_image.min()) * 255).astype(np.uint8)
        
        output_path = os.path.join(output_folder, tif_file)
        cv2.imwrite(output_path, output_image, [cv2.IMWRITE_TIFF_COMPRESSION, 1])

if __name__ == '__main__':
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open a folder selection dialog
    input_folder = filedialog.askdirectory(title="Select the folder containing TIF files to be denoised")
    
    if input_folder:  # Check if a folder was selected
        output_folder = os.path.join(input_folder, "denoised")
        
        process_tif_folder(input_folder, output_folder)
        print('Processing complete.')
    else:
        print('No folder selected. Exiting.')
