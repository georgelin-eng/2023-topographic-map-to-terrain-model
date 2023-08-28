from PIL import Image
import numpy as np
import cv2 as cv

def create_binary_img(pixels, width, height):
    for x in range (width): 
        for y in range (height):
            r, g, b = pixels[x,y]
            if (max(r,g,b) - min(r,g,b) < 10): # Detects grays / whites
                pixels[x,y] = (0, 0, 0) # Black
            else:
                pixels[x,y] = (255, 255, 255) # White

def get_colorbar_index (size):
    sorted_sizes = sorted(size)
    second_largest_size = (sorted_sizes[len(sorted_sizes)-2])
    colorbar_index = np.where(size == second_largest_size)[0][0] 

    return colorbar_index

def get_contour_data (contours):
    index = 0
    size = np.zeros (len(contours))
    contour_data = []

    # create array of sizes
    for c in contours:
        # get area information and information of bounding boxes
        area = cv.contourArea(contours[index])
        x,y,w,h = cv.boundingRect(c)
        bounding_box_area = w*h

        # determining rectangular contours 
        #   rectangularness is measured based on bounding box vs contour area
        #   bounding_box_area/area ~ 1 means a perfect rectangle. 1.3 is chosen for some wiggle room

        if area > 80:
            if bounding_box_area/area < 1.4:
                # print (f"box area = {w*h}, Countor area = {area}, Index = {index}")
                size[index] = area
                contour_data.append({
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'area': area,
                'index': index
                })

        index = index + 1
    
    # Creating area array and deleting the largest rectangle
    areas = np.zeros (len(contour_data))
    for i in range (len(contour_data)):
        areas[i] = contour_data[i]['area']

    # Delete the largest rectangle if it is 10x larger than the smallest
    if max(areas)/min(areas) > 10:
        max_area_index = np.where(areas == max(areas))[0][0]
        contour_data = np.delete (contour_data, max_area_index)

    else: # Don't delete entries if the topography is a unique shape 
        pass

    return contour_data

def getRGB_values (pixel_map, contour_data):

    # If the color bar is a single solid rectangle
    if len(contour_data) == 1: 
        num_color_samples = 400

        entry = contour_data[0]
        
        x, y, w, h = rectDims(entry)
        color_To_Depth_Data = ColorArray(num_color_samples)

        if w > h: # horizontal bar - iterate by changing x
            sample_cords = np.linspace(x+5, x+w-5, num_color_samples).astype(int)
            color_To_Depth_Data = sample_right(color_To_Depth_Data, pixel_map, sample_cords, int(y+h/2))
        
        else: # vertical bar - iterate by changing y
            sample_cords = np.linspace(y+5, y+h-5, num_color_samples).astype(int)
            color_To_Depth_Data = sample_down(color_To_Depth_Data, pixel_map, sample_cords, int(x+w/2))

    # If the color bars are instead multiple discrete rectangles
    # 1. get the coordinates of each rectangle
    # 2. determine whether to iterate by going right or down (horizontal vs vertical colorbar)
    # 3. 
    else:
        x1, y1, _, _ = rectDims(contour_data[0])
        x2, y2, _, _ = rectDims(contour_data[1])
        
        contour_data = np.flip(contour_data)
        sample_cords = create_coordinate_array(contour_data, x2, x1)
        sample_cords = np.flip(sample_cords)        

        for entry in contour_data:
            x, y, w, h = rectDims(entry)
            
        if abs(x2-x1) > 5: #iterate by changing x
            color_To_Depth_Data = ColorArray (len(sample_cords)) # make the same length as the coordinate array
            color_To_Depth_Data = sample_right(color_To_Depth_Data, pixel_map, sample_cords, int(y+h/2))

        else: #iterate by changing y
            color_To_Depth_Data = ColorArray (len(sample_cords)) # make the same length as the coordinate array
            color_To_Depth_Data = sample_down(color_To_Depth_Data, pixel_map, sample_cords, int(x+w/2))

    return color_To_Depth_Data


def sample_down (data, RGB_pixels, sample_cords, midSection):
    index = 0
    
    for cordinate in sample_cords:
        r, g, b = RGB_pixels[midSection,cordinate]
        data [index][0] = r
        data [index][1] = g
        data [index][2] = b

        index = index + 1

    return data

def sample_right (data, RGB_pixels, sample_cords, midSection):
    index = 0
    # sample_cords = np.flip(sample_cords) # Reverse the array so that it fits properly
    for cordinate in sample_cords:
        r, g, b = RGB_pixels[cordinate,midSection]
        data [index][0] = r
        data [index][1] = g
        data [index][2] = b

        index = index + 1

    return data

# Creates an empty array that will store data in the following format
# [r, g, b, depth] 
def ColorArray(num_color_samples):
    cols = 4
    rows = num_color_samples # generic value just for accuracy. Match with the length of a vector for depth info

    color_To_Depth_Data = [[0]*cols for _ in range(rows)]

    return color_To_Depth_Data

def rectDims(entry):

    x = entry['x']
    y = entry['y']
    w = entry['w']
    h = entry['h']

    return x, y, w, h

def create_coordinate_array (contour_data, x2, x1):
    coordinate_vector = []

    for entry in contour_data:
        x, y, w, h = rectDims(entry)

        if abs(x2-x1) > 3:
            num_color_samples = w - 10
            cord_vec = np.linspace(x+5,x+w-5, num_color_samples).astype(int)
            # cord_vec = np.flip(cord_vec)
            coordinate_vector.extend(cord_vec)

        else:
            num_color_samples = h - 10
            cord_vec = np.linspace(y+5, y+h-5, num_color_samples).astype(int)
            # cord_vec = np.flip(cord_vec)

            coordinate_vector.extend(cord_vec)

    coordinate_vector = np.array(coordinate_vector)

    return coordinate_vector

# TODO: pass bounding box information about the largest array
def getTopographyData(width, height, spacing, pixels, RGB_heights):
    cols = 3
    rows = width*height
    TopographyData = [[0]*cols for _ in range(rows)]
    index = 0
    
    for x in range (0, width): 
        for y in range (height):
            r_im, g_im, b_im = pixels[x,y]
            indexClosest = getClosestIndex(r_im, g_im, b_im, RGB_heights)

            if indexClosest is not None:
                TopographyData[index][0] = x                
                TopographyData[index][1] = y                
                TopographyData[index][1] = RGB_heights[indexClosest][3]           

            index +=1


    return TopographyData

# This will find the location of the rgb in the RGB_heights array that matches closest to the color of the pixel
def getClosestIndex (r_im, g_im, b_im, RGB_heights):

    min_diff = 255*3
    min_index = 0
    index = 0

    for entry in RGB_heights:
        diff = RGB_difference(r_im, g_im, b_im, entry)
        
        if diff < min_diff:
            min_diff = diff
            min_index = index
        
        index+=1
    if (max(r_im, g_im, b_im) - min(r_im, g_im, b_im) < 10):
        min_index = None

    return min_index
        
def RGB_difference (r_im, g_im, b_im, entry):
    r = entry[0]
    g = entry[1]
    b = entry[2]

    return abs (r_im - r) + abs(g_im - g) + abs(b_im - b)