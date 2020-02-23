from random import randint, seed
import numpy as np

# Generate a repeatable random HSV image
np.random.seed(42)
h, w = 4, 5
HSV = np.random.randint(1,100,(h,w,3),dtype=np.uint8)
print('Initial HSV\n',HSV)

# Create mask of all pixels with acceptable Hue, i.e. H > 50
HueOK = HSV[...,0] > 50
print('HueOK\n',HueOK)

# Create mask of all pixels with acceptable Saturation, i.e. S > 20 AND S < 80
SatOK = np.logical_and(HSV[...,1]>20, HSV[...,1]<80)
print('SatOK\n',SatOK)

# Create mask of all pixels with acceptable value, i.e. V < 20 OR V > 60
ValOK = np.logical_or(HSV[...,2]<20, HSV[...,2]>60)
print('ValOK\n',ValOK)

# Combine masks
combinedMask = HueOK & SatOK & ValOK
print('Combined\n',combinedMask)
print(combinedMask.dtype, combinedMask.shape)

# Now, if you just want to set the masked pixels to 255
HSV[combinedMask] = 255
print('Result1\n',HSV)

# Or, if you want to set the masked pixels to one value and the others to another value
HSV = np.where(combinedMask,255,0)
print('Result2\n',HSV)