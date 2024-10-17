"""
This file generates different functions ensuring that the Jupyter
Notebook (main) works smoothly
"""

import os
from IPython.display import Image as Img

dir_assets = '../assets/'

# For displaying images:
def img_colab(image):
    display(Img(os.path.join(dir_assets, image)))
    return None