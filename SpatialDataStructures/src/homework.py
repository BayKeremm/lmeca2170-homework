from contact import Contact
from AABBTree import AABBTree, Node, AABB, union_volume, aabb_intersects, union
import time
import numpy as np

class Homework:
    def __init__(self, simulator):
        """
        Caled at the start of the simulation.

        You can use this to set the initial state of the datastructures that you will need.

        The simulator object contains the following attributes:
            - radii: array of shape (N,)
            - positions: array of shape (N, 3)
            - rotations: array of shape (N, 4), storing rotations as quaternions
              (each row contains the scalar first, followed by the
               x, y, and z components).
            - angular_velocities: array of shape (N, 3)
            - velocities: array of shape (N, 3)

        where N is the number of objects being simulated.

        You may use all of these attributes throughout the homework.
        """
        a = np.asarray([0,0,0])
        # Trigger njit
        x = union_volume(a,a,a,a)
        y = aabb_intersects(a,a,a,a)
        z = union(a,a,a,a)
        self.k = x + y + z[0][0] 

    def object_added(self, simulator, i):
        """
        Called every time an object is added to the simulation.

        This can be used to update the data structures you use, if they change
        significantly when new objects are added to the simulation.

        i is the index of the new object.
        """
        pass

    def find_intersections(self, simulator) -> list[Contact]:
        """
        Return all contacts between objects in the simulation.

        simulator.intersect(i, j) returns:
          - None if the objects don't intersect, or
          - a Contact object if they do. This object contains all information the
            simulator needs to resolve the contact.

        The default implementation works, but is not efficient. You should use a
        spatial datastructure to reduce the computational complexity of this method.
        """
        # Code 1: Naive code
        self.k += 1
        start_time = time.time()

 
        #contacts = []
        #for i in range(len(simulator.radii)):
            #for j in range(i + 1, len(simulator.radii)):
                #contact = simulator.intersect(i,j)
                #if contact:
                    #contacts.append(contact)

        # Code 2: Optimized
        # Rebuild the tree at each step, otherwise we need to remove and 
        # insert to the tree and it makes the code more complex
        tree = AABBTree()
        positions = np.array(simulator.positions)
        radii = np.array(simulator.radii)
        min_points = positions - radii[:, None] 
        max_points = positions + radii[:, None]
        for i, (min_point, max_point) in enumerate(zip(min_points, max_points)):
            aabb = AABB(min_point, max_point)
            tree.insert(Node(leaf=True, aabb=aabb, sphere=i))


        contacts = []
        pairs = tree.get_collision_pairs()
        for pair in pairs:
            contact = simulator.intersect(pair[0], pair[1])
            if contact:
                contacts.append(contact)
        time_code_1 = time.time() - start_time
        if self.k == 100:
            print(time_code_1)
            self.k = 0
        return contacts
