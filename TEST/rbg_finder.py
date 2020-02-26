import cv2
import numpy as np

def nothing(x):
    pass

# Load image
image = cv2.imread('50.jpg')

# Create a window
cv2.namedWindow('image')

# Create trackbars for color change
# Hue is from 0-179 for Opencv
cv2.createTrackbar('RMin', 'image', 0, 255, nothing)
cv2.createTrackbar('BMin', 'image', 0, 255, nothing)
cv2.createTrackbar('GMin', 'image', 0, 255, nothing)
cv2.createTrackbar('RMax', 'image', 0, 255, nothing)
cv2.createTrackbar('BMax', 'image', 0, 255, nothing)
cv2.createTrackbar('GMax', 'image', 0, 255, nothing)

# Set default value for Max HSL trackbars
cv2.setTrackbarPos('RMax', 'image', 255)
cv2.setTrackbarPos('BMax', 'image', 255)
cv2.setTrackbarPos('GMax', 'image', 255)

# Initialize HSL min/max values
rMin = bMin = gMin = rMax = bMax = gMax = 0
prMin = pbMin = pgMin = prMax = pbMax = pgMax = 0

while(1):
    # Get current positions of all trackbars
    rMin = cv2.getTrackbarPos('RMin', 'image')
    bMin = cv2.getTrackbarPos('BMin', 'image')
    gMin = cv2.getTrackbarPos('GMin', 'image')
    rMax = cv2.getTrackbarPos('RMax', 'image')
    bMax = cv2.getTrackbarPos('BMax', 'image')
    gMax = cv2.getTrackbarPos('GMax', 'image')

    # Set minimum and maximum bgr values to display
    lower = np.array([rMin, gMin, bMin])
    upper = np.array([rMax, gMax, bMax])

    # Convert to HLS format and color threshold
    bgr = image
    mask = cv2.inRange(bgr, lower, upper)
    result = cv2.bitwise_not(mask)

    # Print if there is a change in bgr value
    if((prMin != rMin) | (pbMin != bMin) | (pgMin != gMin) | (prMax != rMax) | (pbMax != bMax) | (pgMax != gMax) ):
        print("(rMin = %d , bMin = %d, gMin = %d), (rMax = %d , bMax = %d, gMax = %d)" % (rMin , bMin , gMin, rMax, bMax , gMax))
        prMin = rMin
        pbMin = bMin
        pgMin = gMin
        prMax = rMax
        pbMax = bMax
        pgMax = gMax

    # Display result image
    cv2.imshow('image', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()