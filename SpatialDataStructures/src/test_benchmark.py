import cProfile
import pstats
import timeit
import time
from AABBTree import *
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

# Sample data generation
def generate_test_data(num_spheres):
    """Generate test radii and positions for a given number of spheres."""
    radii = [random.uniform(0.5, 2.0) for _ in range(num_spheres)]
    positions = [
        [random.uniform(-10, 10) for _ in range(3)] for _ in range(num_spheres)
    ]
    return radii, positions

def find_intersections_KD(radii, positions):
    tree = cKDTree(positions)
    pairs = tree.query_pairs(np.max(radii) * 2)  # Maximum interaction distance is twice the largest radius
    return pairs
# Original function for profiling
def find_intersections(radii, positions):
    tree = AABBTree()
    for i in range(len(radii)):
        radius = radii[i]
        position = positions[i]
        min_point = np.asarray([position[dim] - radius for dim in range(3)])
        max_point = np.asarray([position[dim] + radius for dim in range(3)])
        aabb = AABB(min_point, max_point)
        tree.insert(Node(leaf=True, aabb=aabb, sphere=i))

    pairs = tree.get_collision_pairs()
    return pairs
def find_intersections_naive(radii, positions):
    contacts = []
    def intersect(pair1, pair2):
        dist = np.linalg.norm(np.array(pair1[0]) - np.array(pair2[0]))
        return dist < pair1[1] + pair2[1]
 
    for i in range(len(radii)):
        for j in range(i + 1, len(radii)):
            contact = intersect([positions[i], radii[i]],[positions[j], radii[j]] )
            if contact:
                contacts.append(contact)
        

# Profiling with cProfile
def profile_find_intersections(num_spheres):
    radii, positions = generate_test_data(num_spheres)
    profiler = cProfile.Profile()
    profiler.enable()
    find_intersections(radii, positions)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats(10)  # Print top 10 functions by time

# Timing with timeit
def time_find_intersections(num_spheres):
    radii, positions = generate_test_data(num_spheres)
    
    # Define the function to be tested
    def test_function():
        find_intersections(radii, positions)

    # Use timeit to measure the execution time
    timing = timeit.timeit(test_function, number=10)
    print(f"Average execution time over 10 runs: {timing / 10:.6f} seconds")

# Run profiling tests
if __name__ == "__main__":
    a = np.asarray([0,0,0])
    # Trigger njit
    x = union_volume(a,a,a,a)
    y = aabb_intersects(a,a,a,a)
    z = union(a,a,a,a)
    bo = x + y + z[0] 

    num_spheres = 1000  # Adjust the number of spheres for testing
    print("Profiling results:")
    profile_find_intersections(num_spheres)

    print("\nTiming results:")
    time_find_intersections(num_spheres)
    num_spheres_list = [10, 50, 100, 500, 1000, 2000]

    times_aabb = []
    times_naive = []



    for num_spheres in num_spheres_list:
        radii, positions = generate_test_data(num_spheres)
        start = time.time()
        find_intersections(radii, positions)
        times_aabb.append(time.time() - start)
        start = time.time()
        find_intersections_naive(radii, positions)
        times_naive.append(time.time() - start)
        # Plotting the results

    plt.figure(figsize=(10, 6))
    plt.plot(num_spheres_list, times_aabb, label='AABB Tree Method', marker='o')
    plt.plot(num_spheres_list, times_naive, label='Naive Method', marker='s')
    plt.xlabel('Number of Spheres')
    plt.ylabel('Time (seconds)')
    plt.title('Comparison of Execution Time for Intersection Methods')
    plt.legend()
    plt.grid(True)
    plt.show()
