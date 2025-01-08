from AABBTree import * 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def draw_aabb(ax, min_point, max_point, color="blue"):
    """
    Draw an AABB as a 3D rectangular box.
    """
    x_min, y_min, z_min = min_point
    x_max, y_max, z_max = max_point

    # Define the vertices of the AABB
    vertices = [
        [x_min, y_min, z_min], [x_max, y_min, z_min], [x_max, y_max, z_min], [x_min, y_max, z_min],  # Bottom face
        [x_min, y_min, z_max], [x_max, y_min, z_max], [x_max, y_max, z_max], [x_min, y_max, z_max]   # Top face
    ]

    # Define the six faces of the AABB
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom face
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # Top face
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front face
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # Back face
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # Right face
        [vertices[0], vertices[3], vertices[7], vertices[4]]   # Left face
    ]

    # Create a 3D polygon collection for the faces
    poly3d = Poly3DCollection(faces, alpha=0.25, edgecolor=color, facecolor=color)
    ax.add_collection3d(poly3d)

def draw_sphere(ax, center, radius, sphere, color="red"):
    """
    Plot a 3D sphere given its center and radius.
    """
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = center[0] + radius * np.cos(u) * np.sin(v)
    y = center[1] + radius * np.sin(u) * np.sin(v)
    z = center[2] + radius * np.cos(v)

    ax.plot_wireframe(x, y, z, color=color, alpha=0.5)
    ax.text(center[0], center[1], center[2] + radius, sphere, color="r", fontsize=10)



def visualize_tree(tree):
    """
    Visualize all spheres and their AABBs in the AABB tree.
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Draw each node in the tree
    for node in tree.nodes:
        if node is None:  # Skip invalid nodes
            continue
        if node.is_leaf:
            # Draw the sphere
            center = np.array(node.aabb.min_point) + (np.array(node.aabb.max_point) - np.array(node.aabb.min_point)) / 2
            radius = np.array((node.aabb.max_point) - np.array(node.aabb.min_point))[0] / 2  # Assuming uniform size
            draw_sphere(ax, center, radius, node.sphere, color="red" )
        # Draw the AABB
        draw_aabb(ax, node.aabb.min_point, node.aabb.max_point, color="blue")

    # Set axis labels and equal scaling
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect([1, 1, 1])  # Equal scaling
    set_axes_equal(ax)
    plt.show()
    plt.show()

def set_axes_equal(ax):
    """
    Set equal scaling for 3D axes so that spheres look correct.
    This makes the aspect ratio of the axes equal.
    """
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = x_limits[1] - x_limits[0]
    y_range = y_limits[1] - y_limits[0]
    z_range = z_limits[1] - z_limits[0]

    # Determine the maximum range among axes
    max_range = max(x_range, y_range, z_range)

    # Calculate midpoints
    x_mid = (x_limits[0] + x_limits[1]) / 2
    y_mid = (y_limits[0] + y_limits[1]) / 2
    z_mid = (z_limits[0] + z_limits[1]) / 2

    # Set new limits to make all ranges equal
    ax.set_xlim3d([x_mid - max_range / 2, x_mid + max_range / 2])
    ax.set_ylim3d([y_mid - max_range / 2, y_mid + max_range / 2])
    ax.set_zlim3d([z_mid - max_range / 2, z_mid + max_range / 2])


# Example usage with AABBTree
tree = AABBTree()

leafs = []
r = 0.49
spheres = [[r,[0.5,0.5,0]], [r,[0.5,1.5,0]], [r,[4.5,1.5,0]], [r,[5.5,1.5,0]] , [r,[1.5,5.5,0]], [r,[1.8,5.5,0]]]
i = 0
for sphere in spheres:
    radius = sphere[0]
    position = sphere[1]

    min_point = np.asarray([position[dim] - radius for dim in range(3)])
    max_point = np.asarray([position[dim] + radius for dim in range(3)])
    aabb = AABB(min_point, max_point)
    leafs.append(Node(leaf=True, aabb=aabb, sphere=i))
    tree.insert(leafs[i])
    visualize_tree(tree)
    i += 1
    
print(tree.get_collision_pairs())
visualize_tree(tree)
