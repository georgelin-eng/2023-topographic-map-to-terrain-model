# topographic-map-to-3D-terrain-model
 

## Project Overview

This is a program which converts any 2d raster image scaled by color and converts it to a 3d terrain model. 

It is intended for use specifically with topographic images as an extension of my [sonar depth mapping project](https://github.com/georgelin-eng/Sonar-Depth-Mapping-System/tree/main), but will work in given these general requirements

1. A colored region where each pixel has some height which corresponds to a color
2. A color bar (either discrete segments or whole) separate from the image
3. Topography is colored and not gray

The program works automatically, with the user only needing to specify the file name of the image with some additional configurable options 
1. max and min depth values on the color bar
2. the amount of downscaling when sampling from the 2d image
3. the number of distinct heights in the 3d plot


10x downscaling and 15 discrete heights yields this following output when taking the image to the right as the input (output on left).


![](https://github.com/georgelin-eng/topographic-map-to-3D-terrain-model/blob/main/topographic-map-to-3D-terrain-model.png)




## Technical Details

### High level overview of steps
1. Preprocessing
2. Contour detection
3. Assigning heights to RGB values
4. Creating topographic data
5. Creating the 3d model

### 1. Preprocessing:
This is done through iterating through each pixel in order to create what is known as a binary image. Based on general requirements outlined previously, the simplest way to do this would be to convert all gray/white to black, while any colored pixel becomes white. 

Grays are sometimes used as a background in topographic image. Therefore, traditional thresholding methods which are based on intensity would not yield the results needed as region in the color bar may be removed unintentionally or the gray region may become white if the thresholding value is set low low.

For this reason, RGB values rather than intensity are used. This is a more robust feature to look for as the each topographic image can be split into 3 segments:
1. White regions
2. Colored regions
3. Gray regions

All white and gray regions can be ignored and only colored regions are significant. This gives justification for creating a binary image based comparison with the color of each pixel rather than the intensity compared to threshold value. Additionally, this skips the required step that the image first be converted to grayscale.

White pixels have an RGB value of (255, 255, 255) while gray pixels will generally have an RGB of (x, x, x) with slight variation. 

Grayness in this case can be measured as: `max(r, g, b) - min(r, g, b)`

Larger differences would be seen in something like pure red (255, 0, 0) while a perfect gray like (128, 128, 128) would have a difference of 0. A small but above zero value is chosen as the threshold for grayness. 

Below is the original image and the binary output after the preprocessing step: 
<img src="https://github.com/georgelin-eng/topographic-map-to-3D-terrain-model/blob/main/images/Topo1.png" width="650">
<img src="https://github.com/georgelin-eng/topographic-map-to-3D-terrain-model/blob/main/images/Binary%20image.png" width="650">

### 2. Contour detection
Contour detection was done using OpenCV which is a library used for computer vision tasks. Specifically, `cv2.findContours()` is used, and returns two values, contours and hierarchy. Hierarchy can be ignored, while contours is a list of all the contours in the image, stored as an NumPy array of (x, y) coordinates of the contour boundary

Two other functions are used:
1. `cv.contourArea()` - returns the area bounding by the contour
2. `cv.boundingRect()` - creates a straight rectangle around a contour. It returns (x, y) coordinates of the top left corner and a width and height

The program iterates through each contour, storing the information of each contour within a dictionary in a list. 


After going through all contours, the contours need to be grouped into 3 categories:
1. Region corresponding to the topography
2. Regions corresponding to the color bar
3. Noise


The first is easy to address. Select the largest contour. This works for all square/rectangular topographies which is most cases. For the above case where a unique island shape is used, this works as well. 

Color bar detection works by measuring how rectangular each contour is. Given that the area of a bounding box will always be larger than the area of the contour is encompasses, this gives a simple but robust way to detect for rectangular regions. 

For a perfect rectangle, the `area_bounding_box / area_Contour == 1`. 1.3 is chosen as the threshold for when a feature is considered rectangular to allow for some variation in how contours are selected by OpenCV. 

Finally, noise can be easily by only considering regions with area above a certain level e.g. 80 pixels. 

A subset of the original list is then created which stores only the rectangles of the color bar. 


**Program selected contours drawn shown below**
![](https://github.com/georgelin-eng/topographic-map-to-3D-terrain-model/blob/main/images/Contour%20detection.png)

### 3. Assigning heights to RGB values

The relevant characteristics of each rectangle in the color bar is saved to a dictionary, these being:
- x, y - location of the upper left corner
- w - width of the rectangle
- h - height of the rectangle

The RGB colors present in the image are contained in the color bar, and can be obtained by either sampling leftwards or downwards depending on the orientation. 

The type of direction of the sampling is used determined based on these conditions

| Condition |   One bar   | Multiple bars |
|:---------:|:-----------:|:-------------:|
|   h > w   | sample down |    ignore     | 
|   w > h   | sample left |    ignore     |
| x changes |   ignore    |  sample left  |
| y changes |   ignore    |  sample down  |

Next, to assign heights to each RGB value, the difference between one RGB to the next is added to a growing sum. Once this sum reaches a threshold value, it is reset. The index of this change occurs is tracked which will be used to determine the height of that RGB value. This is done through using `numpy.linspace()` from the min to max height values over the total number of RGB values. The index where a color changes, for that same index in the `numpy.linespace()` NumPy array, conveniently is the height value of that color.   

This process allows for the automatic generation of a 2d matrix that relates RGB values to heights.

![](https://github.com/georgelin-eng/topographic-map-to-3D-terrain-model/blob/main/images/Pasted%20image%2020230829184806.png)

Later, this array is filtered for distinct colors, then if needed, reduced further so that there is a as many RGB values as the specified number of distinct heights the user requests. 

### 4. Creating topographic data

Based on the results of step 2, the x, y, w, h parameters of the largest contour are used to crop the input image. 

This creates a smaller cropped version of the image to work from for increased efficiency. At this stage, the cropped image is also then scaled down.

The output array is initialized with the minimum depth values, and a the RGB value of each pixel is used to find the closest match in a `heights_of_RGB` list. The corresponding height of the closest matching color is used as the height of the pixel. 

The output of this process is an array with 3 columns, `(x, y, height)` which is a couple thousand pixels long.





### 5. Creating the 3d model
The final 3d model was created using the  `plot_surface()` in Matplotlib and simply requires the data from the matrix created in step 4 to be passed as parameters, x, y, z lists. 

## Conclusions and Future Work

For step 4, every time the comparison is done it's necessary to iterate through the entirety of the `heights_of_RGB`. For large images and if a high depth resolution is wanted, this dramatically increases computation time. 

An alternative search algorithm for the closest RGB value should be employed so that this process can be sped up. However, the program takes generally takes 1-2 seconds to run, and up to 10 seconds for 4k images, so accounting for the extra time it takes to import the extra modules necessary for better search algorithms, the time improvements may be marginal. 

Another thing that I would like to improve is overall how robust the system for more reliable color bar detection. Implementing OCR on the color bar would also be an improvement I'm looking to make so that the user doesn't need to specific min and max depths and these would instead be obtained automatically. 
