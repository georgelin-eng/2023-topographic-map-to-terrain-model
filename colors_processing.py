import numpy as np

def getTopographyData (rgb_data, minDepth, maxDepth):

    indexColors = IndexUniqueColors(rgb_data)

    length_color_vec = len(rgb_data)
    depthVector = np.linspace(maxDepth, minDepth, length_color_vec)

    cols = 4
    rows = len(indexColors)
    topologyData = [[0]*cols for _ in range(rows)]
    
    i = 0
    for num in indexColors:
        topologyData[i][0] = rgb_data[num+1][0] # r value
        topologyData[i][1] = rgb_data[num+1][1] # g value
        topologyData[i][2] = rgb_data[num+1][2] # b value
        topologyData[i][3] = int(depthVector[num+1]) # b value

        i+=1

    return topologyData


# Params:
#   rgb_data: a vector containing all the rgb colors present in the color bar
#   
# Calculate the differences between two colors. 
# The difference is added to a total sum which will index at a certain threshold

def IndexUniqueColors (rgb_data):
    RGB_diff = 0
    indexColors = [0]

    for index in range(len(rgb_data)):
        if index < len(rgb_data)-1:
            r1, r2, g1, g2, b1, b2 = getColors(rgb_data, index)
            RGB_diff = RGB_diff+rgbDifference(r1, r2, g1, g2, b1, b2)

            if RGB_diff > 20: # 20 is the threshold value
                # print (f"difference = {RGB_diff}, RGB = {r1,g1,b1}, index = {index}")
                indexColors.append(index)
                RGB_diff = 0

            index = index + 1

    return indexColors


def getColors (rgb_data, index):
    r1 = rgb_data[index][0]
    r2 = rgb_data[index+1][0]
    g1 = rgb_data[index][1]
    g2 = rgb_data[index+1][1]
    b1 = rgb_data[index][2]
    b2 = rgb_data[index+1][2]

    return r1, r2, g1, g2, b1, b2

def rgbDifference(r1, r2, g1, g2, b1, b2):
    
    return abs(r2-r1) + abs(g2-g1) + abs(b2-b1)