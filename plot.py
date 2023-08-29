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


def create_3D_map(TopographyData):
    x_vals = np.array([entry[0] for entry in TopographyData])
    y_vals = np.array([entry[1] for entry in TopographyData])
    height_vals = np.array([entry[2] for entry in TopographyData])

    # Create a mesh grid
    x_unique = np.unique(x_vals)
    y_unique = np.unique(y_vals)
    x_grid, y_grid = np.meshgrid(x_unique, y_unique)
    z_grid = np.zeros_like(x_grid)

    # Fill the grid with height values
    for i in range(len(TopographyData)):
        x_idx = np.where(x_unique == x_vals[i])
        y_idx = np.where(y_unique == y_vals[i])
        z_grid[y_idx, x_idx] = height_vals[i]

    # Create a figure and a 3D Axes object
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create the surface plot
    surf = ax.plot_surface(x_grid, y_grid, z_grid, cmap='viridis')

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Height')

    # Add a color bar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

    # Show the plot
    plt.show()
