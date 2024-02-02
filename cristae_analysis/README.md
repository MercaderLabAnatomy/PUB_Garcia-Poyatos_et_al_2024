Scripts to analyze cristae widths in TEM image data: 
- `denoise.py` employs [tk_r_em](https://github.com/Ivanlh20/tk_r_em), a pre-trained CNN to denoise TEM images.
-  `extract_widths.py` takes a folder of label images, calculates the widths of all label objects in each image and saves the results to a single CSV.
