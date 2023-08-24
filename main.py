from PIL import Image
import img_processing
import colors_processing
import plot
import numpy as np
import cv2 as cv

# PARAMETERS
    # DATAFILE - File name of topography image to process
    # XY_RESOLUTION - Samples the image for every nth data point when creating 3d image
    # MAX_DEPTH - Depth listed at right or top
    # MIN_DEPTH - Depth at left or bottom

DATAFILE = 'topo1.png'
XY_RESOLUTION = 3
MAX_DEPTH = 0
MIN_DEPTH = 150
DEPTH_RESOLUTION = 20 # If 2 entries are given for depth (Low depth and high depth), sample based on this value


##################################################################


im = Image.open(DATAFILE, 'r')
width, height = im.size

rgb_im = im.convert('RGB')
pixels = rgb_im.load() # create the pixel map
RGB_pixels = rgb_im.load()

img_processing.gray_to_white(pixels, width, height) # Converting gray regions to white
img_processing.create_binary_img (pixels, width, height) # Create binary image by converting white > black and all others to white
rgb_im.save('File.png')

# Working on detecting regions
im = cv.imread('File.png')
imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 127, 255, 0)
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # Obtain contours 
 
# Computing locations of rectangular features
contour_data = img_processing.get_contour_data(contours)

# Create image with contours around colorbar drawn
for entry in contour_data:
    cnt = contours[entry['index']]
    im = cv.drawContours(im, [cnt], -1, (0,0,255), 1)

    print (f"x = {entry['x']}, y = {entry['y']}, w = {entry['w']}, h = {entry['h']}")

cv.imwrite ("Contour_output.png", im)


im = Image.open(DATAFILE, 'r')
rgb_im = im.convert('RGB')
pixel_map = rgb_im.load()

# Getting every rgb color via sampling the colorbar
rgb_data = img_processing.getBarRGB(pixel_map, contour_data)

# Obtaining new array of unique colors and asigning a depth to each color
# Outputs an array in the form [r, g, b, depth]

topologyData = colors_processing.getTopographyData(rgb_data, MIN_DEPTH, MAX_DEPTH)


##########################################################################

# Plotting Function Data 

##########################################################################

# Processing topology data
topologyData = colors_processing.removeBadColors(topologyData)
# topologyData = colors_processing.removeDramaticChanges(topologyData)
topologyData = colors_processing.removeEntries(topologyData, DEPTH_RESOLUTION)

# Creating Colorbar plot
colorbar_rgb_data = plot.extract_RGB(topologyData)
plot.create_color_bar(colorbar_rgb_data)


print(f"\n {topologyData}")

