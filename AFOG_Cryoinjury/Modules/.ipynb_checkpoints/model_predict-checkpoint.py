""" These functions help or perform the segmentation using your trained model."""
import os
import numpy as np
from skimage import io, transform


def minMaxScale(input_image):
  return ((input_image - input_image.min()) * (1/(input_image.max() - input_image.min()) * 255)).astype('uint8')

def padNshrink(input_image,outputSize=512):
  input_image = minMaxScale(input_image)	
  shape = input_image.shape
  dim_max = np.max(shape)
  np_filler = np.ones([dim_max,dim_max,3],dtype="uint8")
  np_filler[:shape[0],:shape[1],:] = input_image
  
  return transform.resize(np_filler,(outputSize,outputSize,3), preserve_range=True,anti_aliasing=False).astype("uint8")

def model_predictions(MODEL,path_images,path_out=None,crop=4096,final_size=512,batch_size=4):
    """
    MODEL: your trained model using segmentation_models (Keras)
    path_images: the path to your input 
    path_out: where you want to save your images
    final_size: the format (squared) that will finally be scaled to
    batch_size: (to be implemented)
    """

    # If path_save is not default *False*, check whether path exists and create if not 
    
    if path_out != None:
              if not os.path.exists(path_out+"/Images_Downscaled/") and not os.path.exists(path_out+"/Predictions/"):
                os.mkdir(path_out+"/Images_Downscaled/")
                os.mkdir(path_out+"/Predictions/")
    
    # Get a list of all files in the directory            
    listImages=os.listdir(path_images)
    n_samples=len(listImages)
    
    # Create arrays for output, X <-- images, y <-- segmentations
    X = np.zeros((n_samples, final_size, final_size,3), dtype="uint8")
    y = np.zeros((n_samples, final_size, final_size,3), dtype=np.float32)  
    

    # Start a for loop to apply the model prediction to all images in the folder
    
    for count,i in enumerate(listImages):

        # Default file format is Tiff, change if you chose a different format        
        print(i)
        if ".tif" in i:
            
            # Read input images            
            img = io.imread(path_images+"/"+i)
            
            if img.shape != [512,512,3]:
              im2 = padNshrink(img,outputSize=512)
                        
            
            else:
              im2 = padNshrink(img,outputSize=final_size)
              
            img_arr=np.expand_dims(im2,axis=0)
            
            # Apply model for image segmentation
            preds_unseen = MODEL.predict(img_arr, verbose=1)
            
            # Save the images and masks            
            if path_out:
              if os.path.exists(path_out+"/Images_Downscaled/"):
                io.imsave(path_out+"/Images_Downscaled/Image_"+i,im2)
                io.imsave(path_out+"/Predictions/UNetSeg_"+i,preds_unseen)
            
            # Collect segmentations and images in two arrays              
            X[count,:,:,:]=im2
            y[count,:,:,:]=preds_unseen[0,:,:,:]
    return X,y,listImages