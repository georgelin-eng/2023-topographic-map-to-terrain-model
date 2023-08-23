from PIL import Image
import numpy as np
import cv2 as cv

def gray_to_white(pixels, width, height):
    for x in range (width): 
        for y in range (height):
            r, g, b = pixels[x,y]
            if (max(r,g,b) - min(r,g,b) < 10):
                pixels[x,y] = (255, 255, 255) # Convert to white

def create_binary_img (pixels, width, height):
    for x in range(width): 
        for y in range(height):
            if pixels[x,y] == (255, 255, 255): # Convert to black
                pixels[x,y] = (0, 0 ,0)
            else:                                                                                              
                pixels[x,y] = (255, 255, 255) # Convert to white

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
        area = cv.contourArea(contours[index])
        x,y,w,h = cv.boundingRect(c)
        bounding_box_area = w*h

        # determining rectangular contours 
        #   rectangularness is measured based on bounding box vs contour area
        #   bounding_box_area/area ~ 1 means a perfect rectangle. 1.3 is chosen for some wiggle room
        if area > 80:
            if bounding_box_area/area < 1.3:
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

    if max(areas)/min(areas) > 10:
        max_area_index = np.where(areas == max(areas))[0][0]
        contour_data = np.delete (contour_data, max_area_index)

    else: # Don't delete entries if the topography is a unique shape 
        pass

    return contour_data

def colorToDepth (DATAFILE, RGB_pixels, contour_data, depthRes, xyRes, depth):

    # If the color bar is a single solid rectangle
    if len(contour_data) == 1: 
        x, y, w, h = rectDims(contour_data)
        color_To_Depth_Data = ColorArray(depth)

        if w > h: # iterate by changing x
            sample_cords = np.linspace(x+5, x+w-5, 400).astype(int)

            color_To_Depth_Data = sample_right(color_To_Depth_Data, RGB_pixels, depth, sample_cords, int(y+h/2))
        
        else: # iterate by changing y
            sample_cords = np.linspace(y+5, y+h-5, 400).astype(int)

            color_To_Depth_Data = sample_down(color_To_Depth_Data, RGB_pixels, depth, sample_cords, int(x+w/2))

    # If the color bars are instead multiple discrete rectangles
    else:
        for entry in contour_data:
            pass

    return color_To_Depth_Data


def sample_down (data, RGB_pixels, depth, sample_cords, midSection):
    index = 0
    for cordinate in sample_cords:
        r, g, b = RGB_pixels[midSection,cordinate]
        data [index][0] = r
        data [index][1] = g
        data [index][2] = b

        index = index + 1
    # TODO: Calculate number of unique colors and their relative indexes > map to depths

    return data

def ColorArray(depth):
    cols = 4
    if len(depth) == 2:
        rows = depthRes
    else:
        rows = len(depth)
    

    rows = 400 # remove later

    color_To_Depth_Data = [[0]*cols for _ in range(rows)]

    return color_To_Depth_Data

def rectDims(contour_data):

    x = contour_data[0]['x']
    y = contour_data[0]['y']
    w = contour_data[0]['w']
    h = contour_data[0]['h']

    return x, y, w, h


def getPixelsImage (RGB_pixels):
    width = 920
    height = 860

    output_image = Image.new('RGB', (width, height))
    
    for y in range(height):
        for x in range(width):
            pixel = RGB_pixels[x,y]
            output_image.putpixel((x, y), pixel)

    output_image.save('output_image.jpg')
