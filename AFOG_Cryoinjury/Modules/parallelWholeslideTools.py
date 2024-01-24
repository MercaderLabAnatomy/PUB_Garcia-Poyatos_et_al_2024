from wholeslideTools import wholeslideTools
import os
import concurrent

class wholeSlideExport(wholeslideTools):
  
  """
  Parallel processing if multiple threads are available.
  Inheritage from wholeslideTools.
  
  ----

  path_in: Path with several ndpi files
  
  path_out: Folder to collect all images as section.
  """

  def __init__(self, path_in = "/content/Data/NDPI/",path_out = "/content/Data/Test", downscale = 512, array_out = False):
      self.pathIn = path_in
      self.pathOut = path_out
      self.downscale = downscale
      self.arrayOut = array_out
      
  def slideExport(self, file_name):
      print(os.path.join(self.pathIn, file_name))
      myslide = wholeslideTools(os.path.join(self.pathIn,file_name))
      print(self.pathOut)
      myslide.exportAllSections(pathOutput = self.pathOut, arrayOut = self.arrayOut, downscale = self.downscale)
      
  def parallelExport(self):
      file_names = os.listdir(self.pathIn)
      
      with concurrent.futures.ProcessPoolExecutor() as executor:
          executor.map(self.slideExport, file_names)
