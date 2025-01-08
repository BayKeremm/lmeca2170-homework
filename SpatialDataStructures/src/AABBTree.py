import heapq 
import numpy as np
from numba import njit
@njit(cache=True)
def aabb_intersects(lmin, lmax, rmin, rmax):
    """
    Check if two axis-aligned bounding boxes (AABBs) intersect.

    Parameters
    ----------
    lmin : array_like
        Minimum point of the first AABB (3D coordinates).
    lmax : array_like
        Maximum point of the first AABB (3D coordinates).
    rmin : array_like
        Minimum point of the second AABB (3D coordinates).
    rmax : array_like
        Maximum point of the second AABB (3D coordinates).

    Returns
    -------
    bool
        True if the AABBs intersect, False otherwise.
    """
    return (
        lmin[0] <= rmax[0] and lmax[0] >= rmin[0] and
        lmin[1] <= rmax[1] and lmax[1] >= rmin[1] and
        lmin[2] <= rmax[2] and lmax[2] >= rmin[2]
    )
@njit(cache=True)
def union_volume(min_point_1, min_point_2, max_point_1, max_point_2):
    """
    Calculate the volume of the union of two AABBs.

    Parameters
    ----------
    min_point_1 : array_like
        Minimum point of the first AABB.
    min_point_2 : array_like
        Minimum point of the second AABB.
    max_point_1 : array_like
        Maximum point of the first AABB.
    max_point_2 : array_like
        Maximum point of the second AABB.

    Returns
    -------
    float
        Volume of the union of the two AABBs.
    """
    min_x, min_y, min_z = min(min_point_1[0], min_point_2[0]), min(min_point_1[1], min_point_2[1]), min(min_point_1[2], min_point_2[2])
    max_x, max_y, max_z = max(max_point_1[0], max_point_2[0]), max(max_point_1[1], max_point_2[1]), max(max_point_1[2], max_point_2[2])

    dim_x = max_x - min_x
    dim_y = max_y - min_y
    dim_z = max_z - min_z

    volume = dim_x * dim_y * dim_z
    return volume

@njit(cache=True)
def union(min_point_1, min_point_2, max_point_1, max_point_2):
    """
    Calculate the union of two AABBs.

    Parameters
    ----------
    min_point_1 : array_like
        Minimum point of the first AABB.
    min_point_2 : array_like
        Minimum point of the second AABB.
    max_point_1 : array_like
        Maximum point of the first AABB.
    max_point_2 : array_like
        Maximum point of the second AABB.

    Returns
    -------
    tuple
        A tuple containing:
        - min_point : ndarray
            Minimum point of the union AABB.
        - max_point : ndarray
            Maximum point of the union AABB.
    """
    min_point = np.minimum(min_point_1, min_point_2)
    max_point = np.maximum(max_point_1, max_point_2)
    return min_point, max_point

class Node:
    """
    A class representing a node in the AABB tree.

    Attributes
    ----------
    is_leaf : bool
        True if the node is a leaf node, False otherwise.
    aabb : AABB
        The bounding box associated with the node.
    parent : int or None
        Index of the parent node, or -1 if the node is the root.
    left : int or None
        Index of the left child, or None if no child exists (meaning it is a leaf).
    right : int or None
        Index of the right child, or None if no child exists (meaning it is a leaf).
    sphere : any
        The sphere object index associated with this leaf node, corresponds to 
            the sphere index in homework.py.
    """
    def __init__(self, leaf=False, aabb = None, 
                 parent = None, left = None, right = None, sphere = None):
        self.is_leaf = leaf 
        self.aabb = aabb 
        self.parent = parent
        self.left =left
        self.right = right
        self.sphere = sphere
class AABB:
    """
    A class representing an axis-aligned bounding box (AABB).

    Attributes
    ----------
    min_point : ndarray
        Minimum corner of the bounding box (3D coordinates).
    max_point : ndarray
        Maximum corner of the bounding box (3D coordinates).
    _volume : float or None
        Cached volume of the bounding box (calculated on demand).

    Methods
    -------
    volume()
        Calculate and cache the volume of the bounding box.
    """
    def __init__(self, min_point, max_point):
        self.min_point = min_point
        self.max_point = max_point
        self._volume = None  # Lazy calculation of volume

    def volume(self):
        """
        Calculate (lazily) and cache the volume of the bounding box.

        Returns
        -------
        float
            Volume of the bounding box.
        """
        if self._volume is None:
            dimensions = self.max_point - self.min_point
            self._volume = dimensions[0] * dimensions[1] * dimensions[2]  
        return self._volume

class AABBTree:
    """
    A class representing an AABB tree for collision detection.

    Attributes
    ----------
    nodes : list
        List of nodes in the tree.
    free_list : list
        Indices of free slots in the nodes list.
    node_count : int
        Total number of nodes in the tree.
    root : int or None
        Index of the root node, or None if the tree is empty.

    Methods
    -------
    append_node(node)
        Append a node to the tree.
    pick_best(index)
        Pick the best location to insert a new leaf node.
    insert(leaf)
        Insert a leaf node into the tree.
    get_collision_pairs()
        Get all pairs of colliding objects in the tree.
    check_collision(left, right, pairs, checked)
        Recursively check for collisions between two nodes.
    """
    def __init__(self):
        self.nodes = []   
        self.free_list = []
        self.node_count = 0
        self.root = None
    def append_node(self, node):
        """
        Append a node to the tree, reusing a slot if available.

        Parameters
        ----------
        node : Node
            The node to be appended.

        Returns
        -------
        int
            Index of the appended node.
        """
        if self.free_list:
            # Reuse a slot from the free list
            index = self.free_list.pop()
            self.nodes[index] = node
        else:
            # Add a new node to the end of the list
            index = len(self.nodes)
            self.nodes.append(node)
        self.node_count += 1
        return index
    def pick_best(self, index):
        """
        Pick the best sibling for a new leaf node based on insertion cost.

        Parameters
        ----------
        index : int
            Index of the new leaf node.

        Returns
        -------
        int
            Index of the best sibling node.
        """
        new_aabb = self.nodes[index].aabb
        new_aabb_vol = new_aabb.volume()
        root_aabb = self.nodes[self.root].aabb

        # initial best cost is joining the new aabb with the root
        best_cost = union_volume(root_aabb.min_point, new_aabb.min_point,
                                 root_aabb.max_point, new_aabb.max_point)
        best_sibling = self.root

        # Priority queue: (cost, node_index)
        queue = []
        heapq.heappush(queue, (0, self.root))

        while queue:
            inherited_cost, current_index = heapq.heappop(queue)
            current_node = self.nodes[current_index]
            current_aabb = current_node.aabb
            # combined volume if we insert the leaf at the current node
            combined_volume = union_volume(new_aabb.min_point,
                                           current_aabb.min_point,
                                           new_aabb.max_point,
                                           current_aabb.max_point)

            # Update the cost with the combined volume
            cost = combined_volume + inherited_cost
            if cost < best_cost:
                best_cost = cost
                best_sibling = current_index

            if current_node.is_leaf:
                continue

            # Update the inherited cost with the change you will get if you add
            # the leaf at this level
            inherited_cost += combined_volume - current_aabb.volume()

            # lower bound cost is the new volume + inherited cost so far
            # Since this would be the best case (maxing the lower bound cost)
            # if they are touching just at the
            # edge
            lower_bound_cost = new_aabb_vol + inherited_cost

            # If this maximized lower cost is smaller than best_cost
            # we need to investigate the tree further
            if lower_bound_cost < best_cost:
                heapq.heappush(queue, (inherited_cost, current_node.left))
                heapq.heappush(queue, (inherited_cost, current_node.right))


        return best_sibling

    def insert(self, leaf):
        """
        Insert a leaf node into the tree.

        Parameters
        ----------
        leaf : Node
            The leaf node object to insert.
        """
        index = self.append_node(leaf)

        if self.node_count == 1:
            self.root = index
            self.nodes[index].parent = -1
            return 

        # Stage 1: pick the best place to insert
        best_index = self.pick_best(index)

        # Stage 2: create a new parent
        old_parent = self.nodes[best_index].parent
        new_parent = self.append_node(Node())
        self.nodes[new_parent].parent = old_parent
        
        new_aabb = leaf.aabb
        best_aabb = self.nodes[best_index].aabb
        self.nodes[new_parent].aabb = union(new_aabb.min_point,
                                            best_aabb.min_point,
                                            new_aabb.max_point,
                                            best_aabb.max_point)

        if old_parent != -1:
            # The sibling was not the root (-1 means the root)
            if self.nodes[old_parent].left == best_index:
                self.nodes[old_parent].left = new_parent
            else:
                self.nodes[old_parent].right = new_parent
            
            self.nodes[new_parent].left = best_index
            self.nodes[new_parent].right = index
            self.nodes[best_index].parent = new_parent
            self.nodes[index].parent = new_parent
        else:
            # The sibling was the root
            self.nodes[new_parent].left = best_index
            self.nodes[new_parent].right = index
            self.nodes[best_index].parent = new_parent
            self.nodes[index].parent = new_parent
            self.root = new_parent

        # Stage 3: walk back up the tree refitting AABBs
        i = leaf.parent
        while i != -1:
            curr = self.nodes[i]
            left = curr.left
            right = curr.right

            left_aabb, right_aabb = self.nodes[left].aabb, self.nodes[right].aabb
            min_point, max_point = union(left_aabb.min_point,
                                         right_aabb.min_point,
                                         left_aabb.max_point,
                                         right_aabb.max_point)
            curr.aabb = AABB(min_point, max_point)

            i = curr.parent
    
    def get_collision_pairs(self):
        """
        Get all pairs of colliding objects in the tree.

        Returns
        -------
        list
            List of pairs of colliding objects.
        """
        # If the root is not defined return
        if self.root == None:
            return []
        colliding_pairs = [] 
        checked = set()
        if not self.nodes[self.root].is_leaf:
            self.check_collision(self.nodes[self.root].left, self.nodes[self.root].right, colliding_pairs, checked)
        return colliding_pairs

    def check_collision(self, left, right, pairs, checked):
        """
        Helper function for get_collision_pairs()
        Recursively check for collisions between two nodes.

        Parameters
        ----------
        left : int
            Index of the left node.
        right : int
            Index of the right node.
        pairs : list
            List of detected collision pairs.
        checked : set
            Set of already checked node pairs.
        """
        
        # Compute a key given left and right indexes using the Cantor function
        key = (left +right) * (left + right + 1) // 2 + right

        if key in checked:
            return

        checked.add(key)

        left_node, right_node = self.nodes[left], self.nodes[right]

        left_min_point, left_max_point = left_node.aabb.min_point, left_node.aabb.max_point

        right_min_point, right_max_point = right_node.aabb.min_point, right_node.aabb.max_point
        children_intersect = aabb_intersects(left_min_point, left_max_point, right_min_point, right_max_point)

        if left_node.is_leaf and right_node.is_leaf:
            if children_intersect:
                pairs.append([left_node.sphere, right_node.sphere])
        elif not left_node.is_leaf and not right_node.is_leaf:
            self.check_collision(left_node.left, left_node.right, pairs, checked)
            self.check_collision(right_node.left, right_node.right, pairs, checked)
            if children_intersect:
                self.check_collision(left_node.left, right_node.left, pairs, checked)
                self.check_collision(left_node.left, right_node.right, pairs, checked)
                self.check_collision(left_node.right, right_node.left, pairs, checked)
                self.check_collision(left_node.right, right_node.right, pairs, checked)
        elif left_node.is_leaf and not right_node.is_leaf:
            self.check_collision(right_node.left, right_node.right, pairs, checked)
            if children_intersect:
                self.check_collision(left, right_node.left, pairs, checked)
                self.check_collision(left, right_node.right, pairs, checked)
        elif not left_node.is_leaf and right_node.is_leaf:
            self.check_collision(left_node.left, left_node.right, pairs, checked)
            if children_intersect:
                self.check_collision(right, left_node.left, pairs, checked)
                self.check_collision(right, left_node.right, pairs, checked)