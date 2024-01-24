
import cv2
import os
import shutil
import numpy as np
import pandas as pd
import skimage
from skimage import io
from skimage.feature import blob_doh
from skimage.filters import gaussian
import skimage.morphology as skm
from PIL import Image
from pathlib import Path 

import sys
sys.path.append(r'Modules')

import glob

# glob. glob(path, recursive=True)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OPENSLIDE_PATH = r'{}\Modules\External\openslide-win64-20171122\bin'.format(os.getcwd())


def printpath():
    print(os.getcwd())
    print(os.path.relpath("F:\Alex\GitHub\MICROSCOPY_AI_Cryoinjuries_AFOG\Modules\External\openslide-win64-20171122\bin"))

if hasattr(os, 'add_dll_directory'):
    # Python >= 3.8 on Windows
    with os.add_dll_directory(OPENSLIDE_PATH):
        import openslide
else:
    import openslide


class wholeslideTools:  
        """ 
        Description:
        -----------
        
        A tool to show, detect, scale and export sections from .ndpi and .mrxs images.
        Initialize the tool by creating an wholeslideTools object. 
        
        ...
        Usage example:
        -----------
        slide = wholeslideTools(input_folder)
        slide.exportAllSections(output_folder)
        
        ...
        
        Arguments:
        -----------
        
        path: str 
            Path to the .ndpi or .mrxs slide file
        
        cropSize: int 
            The default parameter cropSize defines the bounding box around the heart section 
        
        ...
        
        Public methods:
        -----------
        
        showSlide() : Show the slide at low resolution level
        
        localizeSections() : Detect heart sections on the slide at low resolution
        
        showLocalizedSections() : Show the detected section numbered and with bounding box
        
        unscaleLocalized() : Calculate the position of the sections with the full resolution
        
        exportAllSections() : Save the sections as .tiff files
        
        ...
        
        Helper methods:
        -----------
        
        _scaleSlide() : Calculate the size of the image relative to the images we used to setup the tool 
        
        _min_max_scale() : Normalization of the intensity
        
        _saveImages() : Helper function to downscale and export
        
        """

        def __init__(self,path,cropSize = 5000, gaus=5, max_sig=100, thres=0.05, gaus_thres=0.85):  
            self.path = path
            self.cropSize = cropSize
            self.refSize = 0.4527
            self.myslide = openslide.OpenSlide(path)
            self.extension = os.path.splitext(path)[1]    
            self.scale_info = self._scaleSlide()  
            self.image = self.showSlide(show=False)
            self.gaus=gaus
            self.max_sig=max_sig
            self.thres=thres
            self.gaus_thres=gaus_thres
        
        def _scaleSlide(self):
            myslide = self.myslide
            refSize = self.refSize
            ySize = float(myslide.properties['openslide.mpp-y'])
            
            
            pixelRatio = round(refSize/ySize,2)
            relativeRealSize=refSize/ySize
            
            if 1. < relativeRealSize  < 1.9:
                level_ = [6, myslide.level_dimensions[6]]
                
            elif relativeRealSize  >= 1.9:
                level_ = [7, myslide.level_dimensions[7]]
                
            elif relativeRealSize  < 1.:
                level_ = [5, myslide.level_dimensions[5]]    
            
            level_0 = myslide.level_dimensions[0]

            downscale = (level_0[0]/level_[1][0])/relativeRealSize
            
            info = {"Level_used":level_,"Pixel_ratio":pixelRatio,"Relative_size": relativeRealSize,"Downscale_factor": downscale, "Original_XY_µm":ySize,           "Downscaled_XY_µm": ySize * downscale}
            return info
        
        def showSlide(self,show=True):
            myslide = self.myslide
            scaleInfo = self.scale_info
            
            level_ = scaleInfo.get("Level_used")
            level_size = myslide.level_dimensions[level_[0]]
            # Read full slide in low resolution using openslide
            image = np.array(myslide.read_region(location=(0,0), level=level_[0], size=level_size))
            image = image/image.max()
            
            #if image.shape[1] < image.shape[0]:
            #        image = skimage.transform.rotate(image, angle=90, resize=True)          
            #        print("rotate 90")
            if show:    
                plt.figure(figsize=(20, 10))
                plt.title(self.path)
                plt.imshow(image)
                plt.show()
            
            else:
                return image
            
        def localizeSections(self):
            myslide = self.myslide
            cropSize = self.cropSize
            gaus=self.gaus
            gaus_thres=self.gaus_thres
            max_sig=self.max_sig
            thres=self.thres
            
            
            image = self.showSlide(show=False)
            
            scaleInfo = self.scale_info
            level_ = scaleInfo.get("Level_used")
            downscale = scaleInfo.get("Downscale_factor")

            # Convert to numpy array, select only 3rd channel (red) since the muscle are red, apply gaussian, apply threshold
            
            pix = np.array(image)[:,:,2]
            
            image_gaussian = gaussian(pix/pix.max(), gaus) # default 10 ##5 works
            image_thresholded = image_gaussian < gaus_thres #default was 0.85 ##0.90 works better
            
            # Detect heart sections, using skimage blob detection, difference of hessian
            blobs_doh = blob_doh(image_thresholded, max_sigma=max_sig, threshold=thres,overlap=0)## threshold=0.025 better 0.005 also works but many empty images
            # blobs_doh = blob_doh(image_thresholded, max_sigma=100, threshold=.05,overlap=0)
            
            return blobs_doh
        
        def showLocalizedSections(self,cropLoc=1,drop=[],show=True,filterSections=True,upperStd=0.25,lowerStd=0.04):
            
            myslide = self.myslide
            cropSize = self.cropSize
            
            
            patches = self.localizeSections()
            image = self.image
            
            scaleInfo = self.scale_info
            level_ = scaleInfo.get("Level_used")
            downscale = scaleInfo.get("Downscale_factor")
            
            # Convert to numpy array, select only 2nd channel, apply gaussian, apply threshold
            
            if show:
                fig,ax=plt.subplots(1,figsize=(20,20))
                io.imshow(image)
            
            selectedPatches = []
            for num,i in enumerate(patches):
                if num not in drop:

                    x = i[1]-(i[2]*cropLoc)
                    y = i[0]-(i[2]*cropLoc)
                    WideHigh = cropSize/downscale
                    b = mpatches.Rectangle(width=WideHigh,height=WideHigh,xy=[x,y],color="r", linewidth=2, fill=False)
                    bbound = b.get_bbox()
                    std = np.nanstd(image[int(bbound.y0):int(bbound.y1),int(bbound.x0):int(bbound.x1),0])
                     
                    if  (filterSections) & (upperStd > std > lowerStd):
                        if show:
                            plt.text(i[1], i[0], num, bbox=dict(fill=False, edgecolor='red', linewidth=2))
                            ax.add_patch(b)
                        selectedPatches.append((x,y,WideHigh))
                    elif not filterSections:
                        if show:
                            plt.text(i[1], i[0], num, bbox=dict(fill=False, edgecolor='red', linewidth=2))
                            ax.add_patch(b)
                        selectedPatches.append((x,y,WideHigh))
                        
            if show:
                plt.show()
            else:
                return selectedPatches
            
        def unscaleLocalized(self,cropLoc=1,drop=[],show=False,filterSections=True,upperStd=0.25,lowerStd=0.04):
            
            scaleInfo = self.scale_info
            cropSize = self.cropSize         
            myslide=self.myslide
            selectedPatches = self.showLocalizedSections(cropLoc=cropLoc,drop=drop,show=show,filterSections=filterSections,upperStd=upperStd,lowerStd=lowerStd)
            
            level_ = scaleInfo.get("Level_used")
            downscale = scaleInfo.get("Downscale_factor")
            ratio = scaleInfo.get("Pixel_ratio")
            relativeRealSize = scaleInfo.get("Relative_size")
            
            if (ratio > 1.25) | (ratio < 0.75):
                scaleWideHigh = int(cropSize*ratio)
            else:
                scaleWideHigh = int(cropSize)
            self.ratioCrop = scaleWideHigh
            patchesCalibrated = []
        
            for num,i in enumerate(selectedPatches):
                scaleX = i[0]*downscale*ratio
                scaleY = i[1]*downscale*ratio
                blobs = (scaleX,scaleY,scaleWideHigh)
                patchesCalibrated.append(blobs)
            
            return patchesCalibrated
        
        def _min_max_scale(self,inputImage):
            return ((inputImage - inputImage.min()) * (1/(inputImage.max() - inputImage.min())* 255)).astype(np.uint8)
        
        def _saveImages(self, imageRegion, numberImage, pixel_size, pathOutput,downscale = None, minmaxScale = True,fileOut = True,arrayOut = True):
            pathInput = self.path
            name = Path(pathInput).name#.rsplit("/",1)[1].rsplit(".",1)[0]
            extName = name + "_" + str(numberImage) + ".tif"   

            if fileOut:
                if not os.path.exists(pathOutput):
                    os.mkdir(pathOutput)
            imageRegion = Image.fromarray(imageRegion, 'RGBA')
            imageRegion = np.array(imageRegion.convert("RGB"))
            
            if minmaxScale:
                imageRegion = self._min_max_scale(imageRegion)
            
            if downscale != None:
                imageRegion = skimage.transform.resize(imageRegion,(downscale,downscale),anti_aliasing=False,preserve_range=True).astype(np.uint8)
                cropSize = self.cropSize
                relativePixelSize = cropSize/downscale
                pixel_size = float(pixel_size)*relativePixelSize
                
            
            
            if fileOut:
                io.imsave(os.path.join(pathOutput,extName), arr=imageRegion, metadata={'Pixel width': pixel_size,'Pixel height': pixel_size, "Resolution": pixel_size})
            
            if arrayOut:
                
                return imageRegion
        
        def exportAllSections(self, pathOutput = None, cropLoc = 1,drop = [], filterSections = True, upperStd = 0.25, lowerStd = 0.04, downscale = None, arrayOut = False):
            myslide = self.myslide
            pixSize = myslide.properties['openslide.mpp-y']
            if downscale:
                self.final_pixelsize = float(pixSize) * float(self.cropSize/downscale)
            else:
                self.final_pixelsize = pixSize
                
            if pathOutput == None:
                fileOut = False
                arrayOut = True
            else:
                fileOut = True
                
            patchesCalibrated = self.unscaleLocalized(drop = drop,cropLoc = cropLoc,show = False, filterSections = filterSections, upperStd = upperStd, lowerStd = lowerStd)
            if arrayOut:
                if downscale != None:
                    imageCollect = np.zeros([len(patchesCalibrated),downscale,downscale,3],dtype="uint8")
                else:
                    imageCollect = np.zeros([len(patchesCalibrated),self.ratioCrop,self.ratioCrop,3],dtype="uint8")

            for num,patches in enumerate(patchesCalibrated):
                (scaleX, scaleY, scaleWideHigh) = patches
                print(scaleX, scaleY, scaleWideHigh)
                fullImageregion = np.array(myslide.read_region(location = (int(scaleX),int(scaleY)), level = 0,size = (self.ratioCrop, self.ratioCrop)))
                
                if arrayOut:
                    imageCollect[num,:,:,:] = self._saveImages(fullImageregion, num, pixSize, pathOutput = pathOutput,downscale = downscale, arrayOut = arrayOut, fileOut = fileOut)
                else:
                    self._saveImages(fullImageregion, num, pixSize, pathOutput = pathOutput,downscale = downscale, arrayOut = arrayOut, fileOut = fileOut)
            
            if arrayOut:
                return imageCollect
        