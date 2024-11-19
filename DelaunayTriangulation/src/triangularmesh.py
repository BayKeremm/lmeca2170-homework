from proj_utils import color
from halfedge import *
from geompreds import incircle
import matplotlib.pyplot as plt
import numpy as np
class TriangularMesh:
    def __init__(self, vertices, halfedges, triangles,debug):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges
        self.convexhullvertices = []
        self.debug = debug
        self.step = 0

        j = 0
        for t in triangles:
            # Create a new Face object (j = current index, t[0] = first vertex) and append it to the list
            f = Face(j,t[0])
            self.faces.append(f)
            # Associate the created face with each vertex of the triangle.
            t[0].face = f #first vertex
            t[1].face = f #second vertex
            t[2].face = f #third vertex
            j +=1
    # Old exporting method
    #def export(self,file):
        #tris = []
        #for face in self.faces:
            #v1,v2,v3 = face.halfedge.vertex, face.halfedge.next.vertex, face.halfedge.next.next.vertex
            #tris.append([v1.as_tuple(),v2.as_tuple(), v3.as_tuple()])
        #for tri in tris:
            #triangle = [f"({pt[0]}, {pt[1]})" for pt in tri]
            ## Write the triangle to the output file
            #file.write(" ".join(triangle) + "\n")
    def export_homework(self,file):
        tris = []
        for face in self.faces:
            # Extract the vertices of the triangle from the half-edge structure
            # 'halfedge' is the starting edge of the face, and 'next' gives the subsequent edges
            # i1 = index of the current half-edge, 
            # i2 = index of the next half-edge in the loop around the face 
            # i3 = index of the half-edge after that
            i1,i2,i3 = face.halfedge.vertex.index, face.halfedge.next.vertex.index, face.halfedge.next.next.vertex.index
            tris.append([i1,i2,i3])
        file.write(str(len(tris)) + "\n")
        for tri in tris:
            tri = sorted(tri)
            triangle = f"{tri[0]} {tri[1]} {tri[2]}" 
            # Write the triangle to the output file
            file.write(triangle + "\n")

    def compute_convex_hull(self):
        #print("-----------------")
        #for i in self.vertices:
            #print(i)
        #print("-----------------")
        inside_vertices =  self.vertices[:-4]
        #print("Vertices: ", [v.index for v in inside_vertices])
        #print("Faces: ", [[f.halfedge.vertex.index,
                           #f.halfedge.next.vertex.index,
                           #f.halfedge.next.next.vertex.index] for f in self.faces])
        # Sort the vertices based on their x-coordinates
        x_sorted = sorted(inside_vertices, key=lambda v: v.x)
        # Initialize the upper hull
        # upper hull is the part of the convex hull running from the leftmost point p1 to the rightmost point
        # pn when the vertices are listed in clockwise order
        L_upper = [] 
        L_upper.append(x_sorted[0]) #leftmost point
        L_upper.append(x_sorted[1])
        # Build the upper hull
        for i in range(2,len(inside_vertices)):
            L_upper.append(x_sorted[i])
            # check if the last three points make a left turn
            # if they do, we have to remove the second vertex of the triangle 
            # we iterate until every last three points in the upper hull make a right turn
            while len(L_upper) > 2 and orient2d(L_upper[-3].as_tuple(),
                                                L_upper[-2].as_tuple(),
                                                L_upper[-1].as_tuple()) >0:
                L_upper.remove(L_upper[-2])
        # Initialize the lower hull
        L_lower = []
        L_lower.append(x_sorted[-1])
        L_lower.append(x_sorted[-2])
        # Iterate over the remaining vertices in reverse order to construct the lower hull
        for j in reversed(range(0,len(inside_vertices)-2)):
            L_lower.append(x_sorted[j])
            while len(L_lower) > 2 and orient2d(L_lower[-3].as_tuple(),
                                                L_lower[-2].as_tuple(),
                                                L_lower[-1].as_tuple()) >0:
                L_lower.remove(L_lower[-2])
        # Remove the first and last points from the lower hull, as they are duplicates of the upper hull
        # they're the points where the upper and lower hull meet
        L_lower.remove(L_lower[0])
        L_lower.remove(L_lower[-1])
        # Combine upper and lower hull
        self.convexhullvertices = L_upper + L_lower
        return L_upper + L_lower
    
    def get_dual_voronoi(self):
        def compute_circumcenter(vertex1, vertex2, vertex3):
            x1, y1 = vertex1.x, vertex1.y
            x2, y2 = vertex2.x, vertex2.y
            x3, y3 = vertex3.x, vertex3.y

            # Calculate the circumcenter using perpendicular bisectors
            d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
            ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
            uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
            return ux, uy

        centers = []
        circumcenters = {}
        for face in self.faces:
            he = face.halfedge

            # Get the three vertices of the triangle for the current face
            vertex1 = he.vertex
            vertex2 = he.next.vertex
            vertex3 = he.next.next.vertex

            # Compute the circumcenter of the triangle
            circumcenter_x, circumcenter_y = compute_circumcenter(vertex1, vertex2, vertex3)

            circumcenters[face] = (circumcenter_x, circumcenter_y)
            centers.append([circumcenter_x, circumcenter_y])
        return centers, circumcenters 
    
    def handle_boundaries(self, boundary_hes, boundary_vs):
        for he in boundary_hes:
            # Remove the face associated with the boundary half-edge from the list of faces
            self.faces.remove(he.face)
            # Remove the half-edge itself and its next two linked half-edges from the list of half-edges
            self.halfedges.remove(he)
            self.halfedges.remove(he.next)
            self.halfedges.remove(he.next.next)
            # Check if 'next' half-edge has an opposite; if it does, clear its opposite pointer
            # setting to none means that it doesn't have the opposite. That means that it is now a boundary
            if he.next.opposite is not None:
                he.next.opposite.opposite = None
            if he.next.next.opposite is not None:
                he.next.next.opposite.opposite = None
        # Find the half-edges associated with boundary vertices
        to_remove = []
        for he in self.halfedges:
            if he.vertex in boundary_vs:
                to_remove.append(he)

        for he in to_remove:
            if he.opposite is not None:
                #print("SPECIAL FLIP")
                self.special_flip(he, boundary_vs)

        #if self.debug:
            #self.print_mesh("After special flip")


        to_remove = []
        for he in self.halfedges:
            if he.vertex in boundary_vs:
                to_remove.append(he)
                to_remove.append(he.next)
                to_remove.append(he.next.next)
                self.faces.remove(he.face)

        # Now remove them
        for he in to_remove:
            if he in self.halfedges:
                self.halfedges.remove(he)

        for v in boundary_vs:
            self.vertices.remove(v)

    def special_flip(self, he, boundary_vertices):
        # Retrieve the vertices associated with the half-edge
        v_1 = he.vertex  
        v_2 = he.next.vertex  
        v_3 = he.next.next.vertex 
        # its opposite
        v_4 = he.opposite.vertex 
        v_5 = he.opposite.next.vertex 
        v_6 = he.opposite.next.next.vertex 
        # Ensure that the vertices match the expected configuration for a valid flip.
        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for special_flip"
        # Check that the first vertex is indeed a boundary vertex.
        assert v_1 in boundary_vertices, "v_1 not correct"

        # If v_3 v_2 v_6 make a left hand turn flip (reconfiguration is needed)
        res = orient2d(v_3.as_tuple(), v_2.as_tuple(), v_6.as_tuple())
        if res > 0:
            #print("FLIP FLIP SPECIAL")
            # Step 1: Cache the `next` pointers before modifying them
            he_next = he.next
            he_next_next = he.next.next
            op_he_next = he.opposite.next
            op_he_next_next = he.opposite.next.next

            # Step 2: Reassign vertices for the halfedges
            he.vertex = v_6
            he.opposite.vertex = v_3

            # Step 3: Update the `next` pointers to reflect the new edge structure
            # Triangle 1 (around he)
            he.next = he_next_next  
            he.next.next = op_he_next  
            he.next.next.next = he

            # Triangle 2 (around he.opposite)
            he.opposite.next = op_he_next_next  
            he.opposite.next.next = he_next  
            he.opposite.next.next.next = he.opposite

            # Step 4: Update faces
            self.faces.remove(he.face) # Remove the old face associated with the current half-edge
            self.faces.remove(he.opposite.face) # Remove the old face associated with the opposite half-edge
            f1 = Face(len(self.faces),he) # Create a new face for the current half-edge
            self.faces.append(f1) # Add the new face to the list
            he.face = f1 # Assign the new face to the current half-edge
            f2 = Face(len(self.faces),he.opposite) #same for the opposite
            self.faces.append(f2)
            he.opposite.face = f2
            # Update the faces for the next half-edges in the triangles
            he.next.face = he.face
            he.next.next.face = he.face
            he.opposite.next.face = he.opposite.face
            he.opposite.next.next.face = he.opposite.face
            return True #flip performed
        return False # flip not performed

    def edge_flip(self, he, pr):
        v_1 = he.vertex  # This is the starting vertex of he
        v_2 = he.next.vertex  # The next vertex in he's triangle
        v_3 = he.next.next.vertex  # The last vertex in he's triangle

        v_4 = he.opposite.vertex  # The starting vertex of he.opposite
        v_5 = he.opposite.next.vertex  # The next vertex in he.opposite's triangle
        v_6 = he.opposite.next.next.vertex  # The last vertex in he.opposite's triangle

        # Ensure this is a valid edge for flipping: v2 == v4 and v1 == v5
        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        res = incircle(v_1.as_tuple(), v_2.as_tuple(), v_6.as_tuple(), v_3.as_tuple())
        res_x = incircle(v_1.as_tuple(), v_2.as_tuple(), v_3.as_tuple(), v_6.as_tuple())

        if pr == v_6:
            # This is an insanly critical return, otherwise the code recursively goes crazy
            # This is due to turning around the triangle to legalize edges and not terminating
            return False


        if res > 0  :
            # Step 1: Cache the `next` pointers before modifying them
            he_next = he.next
            he_next_next = he.next.next
            op_he_next = he.opposite.next
            op_he_next_next = he.opposite.next.next

            # Step 2: Reassign vertices for the halfedges
            he.vertex = v_6
            he.opposite.vertex = v_3

            # Step 3: Update the `next` pointers to reflect the new edge structure
            # Triangle 1 (around he)
            he.next = he_next_next  
            he.next.next = op_he_next  
            he.next.next.next = he

            # Triangle 2 (around he.opposite)
            he.opposite.next = op_he_next_next  
            he.opposite.next.next = he_next  
            he.opposite.next.next.next = he.opposite

            # Step 4: Update faces
            self.faces.remove(he.face)
            self.faces.remove(he.opposite.face)
            f1 = Face(len(self.faces),he)
            self.faces.append(f1)
            he.face = f1
            f2 = Face(len(self.faces),he.opposite)
            self.faces.append(f2)
            he.opposite.face = f2

            he.next.face = he.face
            he.next.next.face = he.face

            he.opposite.next.face = he.opposite.face
            he.opposite.next.next.face = he.opposite.face

            return True

        return False
    
    def legalize_edge(self, pr, he):
        # Check if the half-edge has an opposite edge; if not, it's a boundary edge and doesn't need legalizing
        if he.opposite == None:
            return
        he_next = he.next
        he_next_next = he.next.next
        op = he.opposite
        op_n = he.opposite.next #next half-edge in the opposite triangle
        op_nn = he.opposite.next.next
        if self.edge_flip(he, pr):
             # If the edge is flipped, recursively call `legalize_edge` on all surrounding half-edges
             # to ensure each triangle in the area adheres to Delaunay conditions
            self.legalize_edge(pr, he_next) 
            self.legalize_edge(pr, he_next_next) 
            self.legalize_edge(pr, op) 
            self.legalize_edge(pr, op_n) 
            self.legalize_edge(pr, op_nn) 

    def print_tris(self):
        for face in self.faces:
            v1,v2,v3 = face.halfedge.vertex, face.halfedge.next.vertex, face.halfedge.next.next.vertex
            print([v1.index,v2.index, v3.index])

    def triangulate(self):
        to_triangulate = self.vertices[:-4]
        # Since last 4 we have manually triangulated
        for vertex in to_triangulate:
            # Check each face (triangle) to see if the vertex is inside or on an edge
            for face in self.faces:
                res = face.inside(vertex)
                if res == True:     # inside the triangle

                    #STEP 1: draw edges from 3 corners to the new point

                    he = face.halfedge
                    init_he_next = he.next
                    init_he_next_next = init_he_next.next
                    # Ensure that the face is a valid triangle
                    assert init_he_next_next.next == he, print("Not a triangle homie")
                    # Create new halfedges from the vertices of the triangle to the new vertexAHAHA
                    he1 = Halfedge(vertex=(he.next.vertex),index=len(self.halfedges))
                    self.halfedges.append(he1)

                    he2 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                    self.halfedges.append(he2)

                    he3 = Halfedge(vertex=(he.vertex),index=len(self.halfedges))
                    self.halfedges.append(he3)

                    he4 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                    self.halfedges.append(he4)

                    he5 = Halfedge(vertex=(he.next.next.vertex),index=len(self.halfedges))
                    self.halfedges.append(he5)

                    he6 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                    self.halfedges.append(he6)

                    # Remove the face we are going to destroy now
                    self.faces.remove(face)
                    # link the halfedges and create the triangles
                    #   1
                    he.next = he1
                    he1.next = he2
                    he2.next = he
                    # This now created a new face
                    f1 = Face(len(self.faces),he)
                    self.faces.append(f1)
                    he.face = f1
                    he1.face = f1
                    he2.face = f1

                    #   2
                    init_he_next.next = he5
                    he5.next = he6
                    he6.next = init_he_next
                    f2 = Face(len(self.faces),init_he_next)
                    self.faces.append(f2)
                    init_he_next.face = f2
                    he5.face = f2
                    he6.face = f2
                    
                    #   3
                    init_he_next_next.next = he3
                    he3.next = he4
                    he4.next = init_he_next_next
                    f3 = Face(len(self.faces),init_he_next_next)
                    self.faces.append(f3)
                    init_he_next_next.face = f3
                    he3.face = f3
                    he4.face = f3
                    
                    # set the opposites
                    he1.opposite = he6
                    he6.opposite = he1
                    he2.opposite = he3
                    he3.opposite = he2
                    he4.opposite = he5
                    he5.opposite = he4

                    #self.print_mesh("Before legalizing he")
                    self.legalize_edge(vertex, he)
                    #print("1")
                    #self.print_mesh("Before legalizing init_he_next", highlight=init_he_next)
                    self.legalize_edge(vertex,init_he_next)
                    #print("2")
                    #self.print_mesh("Before legalizing he next next ", highlight=init_he_next_next)
                    self.legalize_edge(vertex,init_he_next_next)
                    #print("3")
                    #print("TRIS:---------------")
                    #self.print_tris()
                    #self.print_mesh("BEFORE NEXT ITERATION inside face")
                    #print("Len faces after in triangle: ", len(self.faces))
                    break


                elif res == -1:
                    # on the triangle
                    #print("AAAAAAAAAAAAAAAAAAAAAAA")
                    he1 = face.halfedge
                    he2 = he1.next 
                    he3 = he2.next 

                    v1 = he1.vertex
                    v2 = he2.vertex
                    v3 = he3.vertex

                    # Determine which edge the vertex is lying on using orientation tests
                    r1 = orient2d((v1.x,v1.y),(v2.x,v2.y),(vertex.x,vertex.y))
                    r2 = orient2d((v2.x,v2.y),(v3.x,v3.y),(vertex.x,vertex.y))
                    r3 = orient2d((v3.x,v3.y),(v1.x,v1.y),(vertex.x,vertex.y))
                    #print("r1: ", v1.index, v2.index , r1)
                    #print("r2: ", v2.index, v3.index, r2)
                    #print("r3: ", v3.index, v1.index, r3)

                    # this means that it is already a vertex we do not need to add it again.
                    if (r1 == 0 and r2 == 0) or (r2 == 0 and r3 == 0) or (r3 == 0 and r1 == 0):
                        break

                    edge = None
                    if r1 == 0:
                        edge = he1
                    elif r2 == 0:
                        edge = he2
                    elif r3 == 0:
                        edge = he3
                    
                    #print("point is on edge: ", edge.vertex.index, edge.opposite.vertex.index)

                    # store initials
                    edge_opp = edge.opposite
                    edge_opp_n = edge.opposite.next
                    edge_opp_nn = edge.opposite.next.next

                    edge_n = edge.next
                    edge_nn = edge.next.next

                    # remove 2 triangles which are going to turn into 4 triangles
                    self.faces.remove(face)
                    self.faces.remove(edge_opp.face)

                    # check triangles and get diagonal points we are going to connect 

                    p_1 = edge.next.next.vertex 
                    p_2 = edge_opp.next.next.vertex 

                    assert edge.next.next.next == edge and edge_opp.next.next.next == edge_opp, print("Not a triangle, kendine gel")

                    # create the new halfedges for the new triangles
                    
                    v_to_p1 = Halfedge(len(self.halfedges), vertex=vertex)
                    v_to_p2 = Halfedge(len(self.halfedges) + 1, vertex=vertex)

                    p1_to_v = Halfedge(len(self.halfedges) + 2, vertex=p_1)
                    p2_to_v = Halfedge(len(self.halfedges) + 3, vertex=p_2)

                    v_to_ver_edge = Halfedge(len(self.halfedges) + 4, vertex=vertex)
                    v_to_ver_edge_opp = Halfedge(len(self.halfedges) + 5, vertex=vertex)

                    
                    self.halfedges.extend([v_to_ver_edge_opp, v_to_ver_edge, p2_to_v, p1_to_v, v_to_p1, v_to_p2])

                     
                    # set up faces
                    # face 1 (original edge and new halfedges)
                    face_1 = Face(index=len(self.faces), halfedge=edge)
                    edge.next = v_to_p1
                    edge.next.next = edge_nn
                    edge.next.next.next = edge

                    edge.opposite = v_to_ver_edge
                    v_to_ver_edge.opposite = edge

                    v_to_p1.opposite = p1_to_v
                    p1_to_v.opposite = v_to_p1

                    edge.face = face_1
                    edge.next.face = face_1
                    edge.next.next.face = face_1

                    # face 2 (opposite edges)
                    face_2 = Face(index=len(self.faces)+1, halfedge=v_to_ver_edge_opp)
                    v_to_ver_edge_opp.next = edge_n
                    v_to_ver_edge_opp.next.next = p1_to_v
                    v_to_ver_edge_opp.next.next.next = v_to_ver_edge_opp

                    v_to_ver_edge_opp.opposite = edge_opp
                    edge_opp.opposite = v_to_ver_edge_opp

                    v_to_ver_edge_opp.face = face_2
                    v_to_ver_edge_opp.next.face = face_2
                    v_to_ver_edge_opp.next.next.face = face_2

                    # face 3 (remaining vertices and halfedges)
                    face_3 = Face(index=len(self.faces)+2, halfedge=edge_opp)
                    edge_opp.next = v_to_p2
                    edge_opp.next.next = edge_opp_nn
                    edge_opp.next.next.next = edge_opp

                    v_to_p2.opposite = p2_to_v
                    p2_to_v.opposite = v_to_p2

                    
                    edge_opp.face = face_3
                    edge_opp.next.face = face_3
                    edge_opp.next.next.face = face_3

                    # face 4 (final halfedges)
                    face_4 = Face(index=len(self.faces)+3, halfedge=v_to_ver_edge)
                    v_to_ver_edge.next = edge_opp_n
                    v_to_ver_edge.next.next = p2_to_v
                    v_to_ver_edge.next.next.next = v_to_ver_edge

                    v_to_ver_edge.face = face_4
                    v_to_ver_edge.next.face = face_4
                    v_to_ver_edge.next.next.face = face_4
                    # Add all four new faces to the face list
                    self.faces.extend([face_1, face_2, face_3, face_4])

                    # Legalize edges for Delaunay condition after splitting
                    
                    #print("------------------")
                    #print("before legalize")
                    #self.print_tris()
                    self.legalize_edge(vertex, edge_n)
                    self.legalize_edge(vertex, edge_nn)
                    self.legalize_edge(vertex, edge_opp_n)
                    self.legalize_edge(vertex, edge_opp_nn)
                    #self.print_tris()
                    #print("--on edge----------------")
                    #self.print_tris()
                    #self.print_mesh("on edge")
                    break

    def resethalfedges(self):
        for he in self.halfedges:
            he.visited = False

    def plot_convexhull(self):
        # Check if there are convex hull vertices; if not, exit the method
        if len(self.convexhullvertices) == 0:
            return 
        # Plotting the original points and the convex hull
        plt.figure()
        # Original points (x and y coordinates of the vertex)
        plt.plot([v.x for v in self.vertices], [v.y for v in self.vertices], 'o', label='Points')

        # Convex hull (x and y coordinates)
        hull_x = [v.x for v in self.convexhullvertices] + [self.convexhullvertices[0].x]  # closing the polygon
        hull_y = [v.y for v in self.convexhullvertices] + [self.convexhullvertices[0].y]  # closing the polygon
        plt.plot(hull_x, hull_y, 'r-', label='Convex Hull')

        plt.title("Convex Hull")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.legend()
        plt.show()

    def print_mesh(self, title="Fig", highlight=None):
        # Extract x and y coordinates from vertices for plotting
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        
        # Plot vertices
        plt.scatter(x, y, color='blue')
        for v in self.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')
        i = 1
        # Plot faces and halfedges
        for face in self.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            indexes = []
            start_he = he

            while True:
                vertex = he.vertex
                next_vertex = he.next.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)
                indexes.append(vertex.index)

                midpoint_x = (vertex.x + next_vertex.x) / 2
                midpoint_y = (vertex.y + next_vertex.y) / 2
                # Check if the half-edge has been visited (prevent double plotting)
                if he.visited:
                    he = he.next
                    if he == start_he:
                        break
                    continue
                # If the half-edge has no opposite, we can skip annotation (treat as boundary half-edge)
                if he.opposite is None:
                    pass
                    #plt.text(midpoint_x, midpoint_y, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='orange', ha='center')
                else:
                    # Mark the opposite half-edge as visited
                    he.opposite.visited = True
                    #plt.text(midpoint_x -0.2, midpoint_y -0.2, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='purple', ha='center')
                    #plt.text(midpoint_x , midpoint_y, f"he{he.opposite.index}\n→he{he.opposite.next.index}",
                            #fontsize=8, color='purple', ha='center')
                # Mark the current half-edge as visited
                he.visited = True


                # Move to the next half-edge in the loop
                he = he.next
                if he == start_he:
                    break

            # Close the triangle by adding the first point again
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])
            if i < 2:
                print(indexes)
                i +=1
            if indexes == [312, 449, 751] or indexes == [312, 449, 935]:
                print("YES------------------")
                plt.plot(triangle_x, triangle_y, color='blue')
            else:
                plt.plot(triangle_x, triangle_y, color='black')

        # Plot configuration
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(title)
        plt.grid(True)
        plt.show()
        self.resethalfedges()

    def check_exists(self, vertex):
        for v in self.vertices:
            if v.x == vertex.x and v.y == vertex.y:
                return True
        return False
    
    def triangulate_one_step(self, new_vertex=None):
        # Since last 4 we have manually triangulated
        if new_vertex is not None:
            vertex = new_vertex
            self.vertices.insert(-4, vertex)
        else:
            print("to triangulate: ", len(self.vertices[:-4]))
            print("Step: ", self.step)
            if self.step >= len(self.vertices[:-4]):
                return
            vertex = self.vertices[:-4][self.step]
            self.step +=1

        if vertex.done:
            print("Alrady triangulated, going to next")
            return
        vertex.done = True
        # Check each face (triangle) to see if the vertex is inside or on an edge
        for face in self.faces:
            res = face.inside(vertex)
            if res == True:
                #print("Inside triangle")
                #print("We are inside: ", he.vertex.index, init_he_next.vertex.index,
                        #init_he_next_next.vertex.index)
                # inside the triangle
                #STEP 1: draw edges from 3 corners to the new point

                he = face.halfedge
                init_he_next = he.next
                init_he_next_next = init_he_next.next
                # Ensure that the face is a valid triangle
                assert init_he_next_next.next == he, print("Not a triangle homie")
                # Create new halfedges from the vertices of the triangle to the new vertex
                he1 = Halfedge(vertex=(he.next.vertex),index=len(self.halfedges))
                self.halfedges.append(he1)

                he2 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                self.halfedges.append(he2)

                he3 = Halfedge(vertex=(he.vertex),index=len(self.halfedges))
                self.halfedges.append(he3)

                he4 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                self.halfedges.append(he4)

                he5 = Halfedge(vertex=(he.next.next.vertex),index=len(self.halfedges))
                self.halfedges.append(he5)

                he6 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                self.halfedges.append(he6)

                # Remove the face we are going to destroy now
                self.faces.remove(face)
                # link the halfedges and create the triangles
                #   1
                he.next = he1
                he1.next = he2
                he2.next = he
                # This now created a new face
                f1 = Face(len(self.faces),he)
                self.faces.append(f1)
                he.face = f1
                he1.face = f1
                he2.face = f1

                #   2
                init_he_next.next = he5
                he5.next = he6
                he6.next = init_he_next
                f2 = Face(len(self.faces),init_he_next)
                self.faces.append(f2)
                init_he_next.face = f2
                he5.face = f2
                he6.face = f2
                    
                #   3
                init_he_next_next.next = he3
                he3.next = he4
                he4.next = init_he_next_next
                f3 = Face(len(self.faces),init_he_next_next)
                self.faces.append(f3)
                init_he_next_next.face = f3
                he3.face = f3
                he4.face = f3
                    
                # set the opposites
                he1.opposite = he6
                he6.opposite = he1
                he2.opposite = he3
                he3.opposite = he2
                he4.opposite = he5
                he5.opposite = he4

                #self.print_mesh("Before legalizing he")
                self.legalize_edge(vertex, he)
                #print("1")
                #self.print_mesh("Before legalizing init_he_next", highlight=init_he_next)
                self.legalize_edge(vertex,init_he_next)
                #print("2")
                #self.print_mesh("Before legalizing he next next ", highlight=init_he_next_next)
                self.legalize_edge(vertex,init_he_next_next)
                #print("3")
                #print("TRIS:---------------")
                #self.print_tris()
                #self.print_mesh("BEFORE NEXT ITERATION inside face")
                #print("Len faces after in triangle: ", len(self.faces))
                break


            elif res == -1:
                # on the triangle
                print("AAAAAAAAAAAAAAAAAAAAAAA")
                he1 = face.halfedge
                he2 = he1.next 
                he3 = he2.next 

                v1 = he1.vertex
                v2 = he2.vertex
                v3 = he3.vertex

                # Determine which edge the vertex is lying on using orientation tests.
                r1 = orient2d((v1.x,v1.y),(v2.x,v2.y),(vertex.x,vertex.y))
                r2 = orient2d((v2.x,v2.y),(v3.x,v3.y),(vertex.x,vertex.y))
                r3 = orient2d((v3.x,v3.y),(v1.x,v1.y),(vertex.x,vertex.y))
                print("r1: ", v1.index, v2.index , r1)
                print("r2: ", v2.index, v3.index, r2)
                print("r3: ", v3.index, v1.index, r3)
                print("vertex: ", vertex)
                edge = None

                # this means that it is already a vertex we do not need to add it again.
                if (r1 == 0 and r2 == 0) or (r2 == 0 and r3 == 0) or (r3 == 0 and r1 == 0):
                    return

                if r1 == 0:
                    edge = he1
                elif r2 == 0:
                    edge = he2
                elif r3 == 0:
                    edge = he3
                    
                print("point is on edge: ", edge.vertex.index, edge.opposite.vertex.index)

                # store initials
                edge_opp = edge.opposite
                edge_opp_n = edge.opposite.next
                edge_opp_nn = edge.opposite.next.next

                edge_n = edge.next
                edge_nn = edge.next.next

                # remove 2 triangles which are going to turn into 4 triangles
                self.faces.remove(face)
                self.faces.remove(edge_opp.face)

                # check triangles and get diagonal points we are going to connect 

                p_1 = edge.next.next.vertex 
                p_2 = edge_opp.next.next.vertex 

                assert edge.next.next.next == edge and edge_opp.next.next.next == edge_opp, print("Not a triangle, kendine gel")

                # create the new halfedges for the new triangles
                    
                v_to_p1 = Halfedge(len(self.halfedges), vertex=vertex)
                v_to_p2 = Halfedge(len(self.halfedges) + 1, vertex=vertex)

                p1_to_v = Halfedge(len(self.halfedges) + 2, vertex=p_1)
                p2_to_v = Halfedge(len(self.halfedges) + 3, vertex=p_2)

                v_to_ver_edge = Halfedge(len(self.halfedges) + 4, vertex=vertex)
                v_to_ver_edge_opp = Halfedge(len(self.halfedges) + 5, vertex=vertex)

                    
                self.halfedges.extend([v_to_ver_edge_opp, v_to_ver_edge, p2_to_v, p1_to_v, v_to_p1, v_to_p2])

                     
                # set up faces
                # face 1
                face_1 = Face(index=len(self.faces), halfedge=edge)
                edge.next = v_to_p1
                edge.next.next = edge_nn
                edge.next.next.next = edge

                edge.opposite = v_to_ver_edge
                v_to_ver_edge.opposite = edge

                v_to_p1.opposite = p1_to_v
                p1_to_v.opposite = v_to_p1

                edge.face = face_1
                edge.next.face = face_1
                edge.next.next.face = face_1

                # face 2
                face_2 = Face(index=len(self.faces)+1, halfedge=v_to_ver_edge_opp)
                v_to_ver_edge_opp.next = edge_n
                v_to_ver_edge_opp.next.next = p1_to_v
                v_to_ver_edge_opp.next.next.next = v_to_ver_edge_opp

                v_to_ver_edge_opp.opposite = edge_opp
                edge_opp.opposite = v_to_ver_edge_opp

                v_to_ver_edge_opp.face = face_2
                v_to_ver_edge_opp.next.face = face_2
                v_to_ver_edge_opp.next.next.face = face_2

                # face 3
                face_3 = Face(index=len(self.faces)+2, halfedge=edge_opp)
                edge_opp.next = v_to_p2
                edge_opp.next.next = edge_opp_nn
                edge_opp.next.next.next = edge_opp

                v_to_p2.opposite = p2_to_v
                p2_to_v.opposite = v_to_p2

                    
                edge_opp.face = face_3
                edge_opp.next.face = face_3
                edge_opp.next.next.face = face_3

                # face 4
                face_4 = Face(index=len(self.faces)+3, halfedge=v_to_ver_edge)
                v_to_ver_edge.next = edge_opp_n
                v_to_ver_edge.next.next = p2_to_v
                v_to_ver_edge.next.next.next = v_to_ver_edge

                v_to_ver_edge.face = face_4
                v_to_ver_edge.next.face = face_4
                v_to_ver_edge.next.next.face = face_4

                self.faces.extend([face_1, face_2, face_3, face_4])

                    
                #print("------------------")
                #print("before legalize")
                #self.print_tris()
                self.legalize_edge(vertex, edge_n)
                self.legalize_edge(vertex, edge_nn)
                self.legalize_edge(vertex, edge_opp_n)
                self.legalize_edge(vertex, edge_opp_nn)
                #self.print_tris()
                #print("--on edge----------------")
                #self.print_tris()
                #self.print_mesh("on edge")
                    
                break