from PIL import Image
import img_processing
import colors_processing
import plot
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Import the 3D plotting toolkit

# PARAMETERS
    # DATAFILE - File name of topography image to process
    # XY_RESOLUTION - Samples the image for every nth data point when creating 3d image
    # MAX_DEPTH - Depth listed at right or top
    # MIN_DEPTH - Depth at left or bottom
    # DEPTH_RESOLUTION - sets limit to the number of rows in (r, g, b) to depth matrix (controls the veritical resolution of the output)


DATAFILE = 'Topo4.png'
XY_RESOLUTION = 10
MAX_DEPTH = 2250
MIN_DEPTH = -5500
DEPTH_RESOLUTION = 15

##################################################################
# PREPROCESSING STEP
# The specific file is loaded as a pixel map and each individual becomes either black or white based on a specified condition
# This process is iterated for each pixel for O(n) performance where n is the number of pixels
# TODO: Use matrix manipulations to achieve better runtime efficiency

plot_colorbar = 'off'
plot_3D_map_status = 'off'

im = Image.open(DATAFILE, 'r')
width, height = im.size

rgb_im = im.convert('RGB')
pixels = rgb_im.load() # create the pixel map
# pixel_map = rgb_im.load()

img_processing.create_binary_img(pixels, width, height) # Create binary image by converting white/grays > black and all others to white
rgb_im.save('File.png')

##################################################################
# DETECTION STEP
# The binary file is read and the findContours function function from openCV is used to detect the contours of each region
# After the contour of all regions is obtained, the specific contours of rectangular regions is saved in a dictionary
# This step has a fairly high confidence of returning all relevant contours of the colorbar region while excluding other points
# TODO: What input arguments and their datatypes does cv.findContours take?
# TODO: Find if findContours can be used on the pixel map directly without the image save and read step


im = cv.imread('File.png')
imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 127, 255, 0)
contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # Obtain contours 
 
# Computing locations of rectangular features
contour_data, x_of_max, y_of_max, w_of_max, h_of_max = img_processing.get_contour_data(contours)

# Create image with contours around colorbar drawn
for entry in contour_data:
    cnt = contours[entry['index']]
    im = cv.drawContours(im, [cnt], -1, (0,0,255), 2)

    print (f"x = {entry['x']}, y = {entry['y']}, w = {entry['w']}, h = {entry['h']}")

cv.imwrite ("Contour_output.png", im)


im = Image.open(DATAFILE, 'r')
rgb_im = im.convert('RGB')
pixel_map = rgb_im.load()

# Cropping image step

im_to_Crop = rgb_im
crop_dim = (x_of_max+2, y_of_max+4, x_of_max+w_of_max-4, y_of_max+h_of_max-4)
im_crop = im_to_Crop.crop(crop_dim)
im_resized = im_crop.resize((int(w_of_max/XY_RESOLUTION), int(h_of_max/XY_RESOLUTION)))

im_resized.save('Cropped_image.png')

##################################################################
# IMAGE SAMPLING STEP
# This step is broken into 2 sub-steps
#   1. Takes the original image and obtains the heights of each RGB value
#   2. For each pixel, return a height based on the closest color in RGB_heights


# Getting every rgb color via sampling the colorbar
rgb_values = img_processing.getRGB_values(pixel_map, contour_data)

# Obtaining new array of unique colors and asigning a depth to each color
# Outputs an array in the form [r, g, b, depth]
RGB_heights = colors_processing.getRGBHeights(rgb_values, MIN_DEPTH, MAX_DEPTH)

# Processing topology data
# RGB_heights = colors_processing.removeDramaticChanges(RGB_heights)
RGB_heights = colors_processing.removeEntries(RGB_heights, DEPTH_RESOLUTION+1)
RGB_heights = colors_processing.removeBadColors(RGB_heights)

print(f"\n {RGB_heights}")

cropped_pixel_map = im_resized.load()
cropped_width = int(w_of_max/XY_RESOLUTION)
cropped_height = int(h_of_max/XY_RESOLUTION)
TopographyData = img_processing.getTopographyData(cropped_width, cropped_height, cropped_pixel_map, RGB_heights, MIN_DEPTH)

##########################################################################

# Plotting Function Data 

##########################################################################

# 3d Plot 
if plot_3D_map_status == 'on':
    plot.create_3D_map(TopographyData)

# Creating Colorbar plot
if plot_colorbar == 'on':
    colorbar_rgb_data = plot.extract_RGB(RGB_heights)
    plot.create_color_bar(colorbar_rgb_data)


print("\n\n\n")
print (np.linspace(MIN_DEPTH, MAX_DEPTH, 12).astype(int))
