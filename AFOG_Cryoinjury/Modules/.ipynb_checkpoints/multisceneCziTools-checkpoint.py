import cv2
import slideio
from skimage.transform import resize
from skimage.filters import gaussian
from skimage.feature import blob_doh
import numpy as np
from model_predict import minMaxScale

class multiscene_czi_export():
    
    def __init__(self, filepath, out_size = 512, fullframe = 8192, all_single = True):
        self.filepath = filepath
        self.slide = slideio.open_slide(filepath, driver="CZI")
        self.all_single = all_single
        self.out_size = out_size
        self.fullframe = fullframe
        self.scene0 = self.slide.get_scene(0)
        self.full_resolution = self.scene0.resolution[0] * (10**6)
        self.downscale_factor = fullframe/out_size
        self.downscaled_resolution = (self.full_resolution * self.downscale_factor)
    
    def _scaleSlide(self):
        resolution = {'Downscaled_XY_µm':self.downscaled_resolution, "Downscale_factor": self.downscale_factor, "Original_XY_µm":self.full_resolution}
        return resolution 
    
    def _setBorder(self,image, width=50, value=0):
        image[:, :width] = value
        image[:width, :] = value
        image[(image.shape[0] - width):,:] = value
        image[:,(image.shape[1] - width):] = value
        return image
    
    def showSlide(self, show=False):
        slide = self.slide
        slide_image = minMaxScale(cv2.cvtColor(slide.get_aux_image_raster('SlidePreview'), cv2.COLOR_BGR2RGB))
        if show:
            imshow(slide_image)
            
        return slide_image
        
    def detect_sections(self):
        blobs = []
        slide = self.slide
        single = self.all_single
        fullframe = self.fullframe
        filename = self.filepath
        

        for i in range(slide.num_scenes):
            try:
                scene = slide.get_scene(i)
            except:
                print("Index error in file.")
                return blobs
            
            scene_i = gaussian(cv2.cvtColor(scene.read_block(size=(int(scene.size[0]/16),int(scene.size[1]/16))), cv2.COLOR_BGR2RGB)[:,:,0],20)

            image_thresholded = self._setBorder(((scene_i < 0.9) & (scene_i > 0.01)))
            
            if single:
                def_size=int((scene.size[0]/16)/2)
                blobs.append( (i, ((def_size,def_size,fullframe/16))))
            
            else:
                blobs_doh = blob_doh(image_thresholded, max_sigma=360, threshold=.05,overlap=0.)

                if blobs_doh.size == 0:
                    blobs_doh = blob_doh(image_thresholded, max_sigma=100, threshold=.04,overlap=0.)
                    print("step 1",blobs_doh.size)

                if blobs_doh.size == 0:
                    blobs_doh = blob_doh(image_thresholded, max_sigma=200, threshold=.04,overlap=0.)
                    print("step 2",blobs_doh.size)

                if blobs_doh.size > 3:
                    image_thresholded = self._setBorder((scene_i < 0.9) & (scene_i > 0.01),width=100)
                    blobs_doh = blob_doh(image_thresholded, max_sigma=100, threshold=.04,overlap=0.)
                    print("step 3",blobs_doh.size)
                
                print(filename)
                [blobs.append((i,blob)) for blob in blobs_doh if len(blob) != 0]
        return blobs
    
    def section_toarray(self):
        
        blobs = self.detect_sections()
        out_size = self.out_size 
        fullframe = self.fullframe
        collect_arrays = np.zeros((len(blobs),out_size,out_size,3),dtype="uint8")  
        slide = self.slide
        print(blobs)
        for n, (scene_n,(x1,y1,r)) in enumerate(blobs):
            rect_coord=(int((16*y1)-fullframe/2),int(int(16*x1)-fullframe/2),fullframe,fullframe)
            try:
                scene = slide.get_scene(scene_n)
                
            except RuntimeError as e:
                print(e)
                return collect_arrays
            scene_full = np.array(cv2.cvtColor(scene.read_block(rect=rect_coord,size=(out_size,out_size)), cv2.COLOR_BGR2RGB))
            collect_arrays[n,:,:,:] = scene_full
        collect_arrays[collect_arrays==0]= collect_arrays.max()   
        
        return collect_arrays
    