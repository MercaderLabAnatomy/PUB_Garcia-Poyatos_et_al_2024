<h1>Cryo Injury Analysis by Unet</h1>
<h2>Setup, data preparation, training and analysis</h2>

<b>Installation:</b>

1. (Optional, only the first time you want to use your computer)  
	Prepare Cuda for GPU processing with Tensorflow (only if you have an Nvidia GPU)
	- Everything should be according to the requirements in "https://www.tensorflow.org/install/pip"
	- A tutorial how to do this: "https://towardsdatascience.com/installing-tensorflow-with-cuda-cudnn-and-gpu-support-on-windows-10-60693e46e781"

2. Install Mini Conda
	- https://docs.conda.io/en/latest/miniconda.html#windows-installers

3. Open Anaconda Powershell Prompt

4. In Prompt Window type (execution will take a moment):
	conda env create -f >>PATH TO REPOSITORY<<\environment.yml -n AI_Cryoinjuries

5. In Prompt Window type:
	conda activate AI_Cryoinjuries

6. Go to directory with your repository,
   In Prompt Window type:
	cd >>ENTER DIRECTORY<<
7. In Prompt Window type:
	jupyter lab

8. Open the 1st notebook in jupyter lab:
   	1st_NOTEBOOK_Prepare_Training.ipynb

9. Test the package import cell, if some package cannot be loaded, see the error message, if the package was not installed
	use in the jupyter lab: !pip install >>PACKAGE NAME<<
10. If one of the modules in this repository cannot be loaded check that the system path is correctly defined (python sys module see notebook)

<b>Usage:</b>
Each notebook contains instructions on how to use them.

Preparation:
1. Before python: Use the MICROSCOPY_Basics ImageJ-macro in annotation mode
	https://github.com/MercaderLabAnatomy/MICROSCOPY_Basics
2. If you have the annotations ready in a folder, put also the real images that you annotated in a folder

3. Open and follow the instructions in the 1st_NOTEBOOK

Training
1. Open and follow the instructions in the 2nd_NOTEBOOK

  
Analysis
1. Open and follow the instructions in the 3rd_NOTEBOOK
