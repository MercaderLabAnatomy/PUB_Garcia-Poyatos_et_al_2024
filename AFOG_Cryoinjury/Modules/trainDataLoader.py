import os
import numpy as np
import albumentations as A
import cv2
from skimage.io import imsave, imread
from skimage.transform import resize
from skimage.exposure import rescale_intensity

import tensorflow


"""This package was adapted from https://github.com/qubvel/segmentation_models/blob/master/examples/multiclass%20segmentation%20(camvid).ipynb"""
    

class Dataset:
    """
    
    Args:
        images_dir (str): path to images folder
        masks_dir (str): path to segmentation masks folder
        class_values (list): values of classes to extract from segmentation mask
        augmentation (albumentations.Compose): data transfromation pipeline 
            (e.g. flip, scale, etc.)
        preprocessing (albumentations.Compose): data preprocessing 
            (e.g. noralization, shape manipulation, etc.)
    
    """
    
    def __init__(self, images_dir, masks_dir, augmentation=None, preprocessing=None):
        self.ids = os.listdir(images_dir)
        self.images_fps = [os.path.join(images_dir, image_id) for image_id in self.ids]
        self.masks_fps = [os.path.join(masks_dir, image_id) for image_id in self.ids]
        
        # convert str names to class values on masks
        
        self.augmentation = augmentation
        self.preprocessing = preprocessing
    
    def __getitem__(self, i):
        # read data
        image = cv2.imread(self.images_fps[i])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = cv2.imread(self.masks_fps[i])
        
        # apply augmentations
        if self.augmentation:
            sample = self.augmentation(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']
        
        # apply preprocessing
        if self.preprocessing:
            sample = self.preprocessing(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']
            
        return image, mask
        
    def __len__(self):
        return len(self.ids)
    
class Dataloder(tensorflow.keras.utils.Sequence):
    """Load data from dataset and form batches
    
    Args:
        dataset: instance of Dataset class for image loading and preprocessing.
        batch_size: Integet number of images in batch.
        shuffle: Boolean, if `True` shuffle image indexes each epoch.
    """
    
    def __init__(self, dataset, batch_size, shuffle=False):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indexes = np.arange(len(dataset))

        self.on_epoch_end()

    def __getitem__(self, i):
        
        # collect batch data
        start = i * self.batch_size
        stop = (i + 1) * self.batch_size
        data = []
        for j in range(start, stop):
            data.append(self.dataset[j])
        
        # transpose list of lists
        batch = np.array([np.stack(samples, axis=0) for samples in zip(*data)])
        X=batch[0]
        y=batch[1].astype("float32")
        return (X,y)
    
    def __len__(self):
        """Denotes the number of batches per epoch"""
        return len(self.indexes) // self.batch_size
    
    def on_epoch_end(self):
        """Callback function to shuffle indexes each epoch"""
        if self.shuffle:
            self.indexes = np.random.permutation(self.indexes)
            
def get_training_augmentation(size=(512,512)):
    """Define how the images are augmented for the training
    Args:
        add a tuple of the desired image size
    """
    train_transform = [
        
        A.HorizontalFlip(p=0.5),
        
        
        A.ShiftScaleRotate(scale_limit=0.05, rotate_limit=90, shift_limit=0.005, p=1, border_mode=1),#changed shift_limit 0.1-->0.05 scale_limit 0.5 -->0.1
        
        A.PadIfNeeded(min_height=size[0], min_width=size[1], always_apply=True, border_mode=1),
        
        
        A.OneOf(
            [
                #A.CLAHE(p=1),
                A.RandomBrightnessContrast (brightness_limit=0.2, contrast_limit=0.2, brightness_by_max=True, always_apply=False, p=0.5),
                #A.RandomGamma(p=1),
            ],
            p=0.9,
        ),

        A.OneOf(
            [
                A.Sharpen(p=1),
                A.Blur(blur_limit=3, p=1),
            ],
            p=0.9,
        ),

        A.OneOf(
            [
                A.RandomContrast(p=1),
                #A.HueSaturationValue(p=1),
                A.transforms.RGBShift (r_shift_limit=20, g_shift_limit=20, b_shift_limit=20, always_apply=False, p=0.5)
            ],
            p=0.9,
        ),
        A.Lambda(mask=round_clip_0_1)
    ]
    return A.Compose(train_transform)


def get_validation_augmentation(size=(512,512)):
    """Add paddings to make image shape divisible by 32
    Args:
        add a tuple of the desired image size
    """
    test_transform = [
        A.PadIfNeeded(size[0], size[1])
    ]
    return A.Compose(test_transform)

def get_preprocessing(preprocessing_fn):
    """Construct preprocessing transform
    
    Args:
        preprocessing_fn (callbale): data normalization function 
            (can be specific for each pretrained neural network)
    Return:
        transform: albumentations.Compose
    
    """
    
    _transform = [
        A.Lambda(image=preprocessing_fn),
    ]
    return A.Compose(_transform)



def match_annotation_to_train(folderpath,name = "INT"):
    folder_list = os.listdir(folderpath)
    parent_path = os.path.dirname(folderpath).rsplit("/",1)
    new_dir = os.path.join(parent_path[0], parent_path[1] + "_" + name) 
    
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    
    for images in folder_list:
        image_path = os.path.join(folderpath,images)
        save_path = os.path.join(new_dir,images)
        im = imread(image_path)
        im = min_max_scale(im)
        
        imsave(save_path, im)

def compare_dimensions(image, batch=True):
    
    ref_dim = (512,512,3)
    
    if image.shape == ref_dim:
        if not batch:
            print("The image dimensions are correct.")
        else:
            return True
    
    elif image.shape[-1] != 3:
        if not batch:
            print("The image is not RGB or the dimension order is not XYC (C=Channel)")
            print(image.shape)
        else:
            return "Not RGB check:"
        
    elif image.shape[0] != 512:
        if not batch:
            print("The dimensions XY are not 512*512. You will have to adapt the Dataloader")
            print(image.shape)
        else:
            return image.shape
        
def im_compare(str1,str2):
    return compare_dimensions(imread(os.path.join(str1,str2)))

def check_images(x_train_path):
    dict_={i:  im_compare(x_train_path,i) for i in os.listdir(x_train_path)}
    for i in dict_.items():
        if i[1] != True:
            print(i[1],i[0])    

# classes for data loading and preprocessing
def round_clip_0_1(x, **kwargs):
    return x.round().clip(0, 1)

def min_max_scale(inputImage):
    return ((inputImage - inputImage.min()) * (1/(inputImage.max() - inputImage.min()) * 255)).astype('uint8')

def zero_one_scale(inputImage):
    image = np.zeros(inputImage.shape, dtype="uint8")
    image[inputImage == 255] = 1
    return image

def resize_trainingdata(image, outsize=(512,512,3), mask="Images"):
    

    if image.shape != outsize:
        image = resize(image, outsize, anti_aliasing = False)
        
        if mask == "Annotations":
            image = round_clip_0_1(image)

        else:
            image = min_max_scale(image)
    
    else:
        if mask == "Annotations":
            image = zero_one_scale(image)
        else:
            image = min_max_scale(image)
   
    return image.astype("uint8")