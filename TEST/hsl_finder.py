import cv2
import numpy as np

def nothing(x):
    pass

# Load image
image = cv2.imread('35.png')

# Create a window
cv2.namedWindow('image')

# Create trackbars for color change
# Hue is from 0-179 for Opencv
cv2.createTrackbar('HMin', 'image', 0, 179, nothing)
cv2.createTrackbar('SMin', 'image', 0, 255, nothing)
cv2.createTrackbar('LMin', 'image', 0, 255, nothing)
cv2.createTrackbar('HMax', 'image', 0, 179, nothing)
cv2.createTrackbar('SMax', 'image', 0, 255, nothing)
cv2.createTrackbar('LMax', 'image', 0, 255, nothing)

# Set default value for Max HSL trackbars
cv2.setTrackbarPos('HMax', 'image', 179)
cv2.setTrackbarPos('SMax', 'image', 255)
cv2.setTrackbarPos('LMax', 'image', 255)

# Initialize HSL min/max values
hMin = sMin = lMin = hMax = sMax = lMax = 0
phMin = psMin = plMin = phMax = psMax = plMax = 0

while(1):
    # Get current positions of all trackbars
    hMin = cv2.getTrackbarPos('HMin', 'image')
    sMin = cv2.getTrackbarPos('SMin', 'image')
    lMin = cv2.getTrackbarPos('LMin', 'image')
    hMax = cv2.getTrackbarPos('HMax', 'image')
    sMax = cv2.getTrackbarPos('SMax', 'image')
    lMax = cv2.getTrackbarPos('LMax', 'image')

    # Set minimum and maximum HSV values to display
    lower = np.array([hMin, lMin, sMin])
    upper = np.array([hMax, lMax, sMax])

    # Convert to HLS format and color threshold
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)

    # Print if there is a change in HSV value
    if((phMin != hMin) | (psMin != sMin) | (plMin != lMin) | (phMax != hMax) | (psMax != sMax) | (plMax != lMax) ):
        print("(hMin = %d , sMin = %d, lMin = %d), (hMax = %d , sMax = %d, lMax = %d)" % (hMin , sMin , lMin, hMax, sMax , lMax))
        phMin = hMin
        psMin = sMin
        plMin = lMin
        phMax = hMax
        psMax = sMax
        plMax = lMax

    # Display result image
    cv2.imshow('image', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()