import matplotlib.pyplot as plt
import numpy as np

def extract_RGB(topologyData):
    rgb_values = [entry[:3] for entry in topologyData]
    return rgb_values

def create_color_bar(rgb_values):
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 1))

    # Create a colormap using the provided RGB values
    cmap = np.array(rgb_values) / 255.0

    # Create a colorbar using the colormap
    cax = ax.matshow(np.arange(len(rgb_values)).reshape(1, -1), cmap=plt.cm.colors.ListedColormap(cmap))
    fig.colorbar(cax, orientation='horizontal', ticks=np.arange(len(rgb_values)))

    # Remove ticks and labels from the axis
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Set the title of the colorbar
    ax.set_title('RGB Colorbar')

    # Display the colorbar
    plt.show()
