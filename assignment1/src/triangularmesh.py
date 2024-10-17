from proj_utils import color
from halfedge import *
from geompreds import incircle
import matplotlib.pyplot as plt
import numpy as np
class TriangularMesh:
    def __init__(self, vertices, halfedges, triangles):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges
        self.convexhullvertices = []

        j = 0
        for t in triangles:
            f = Face(j,t[0])
            self.faces.append(f)
            t[0].face = f
            t[1].face = f
            t[2].face = f
            j +=1
    def export(self,file):
        tris = []
        for face in self.faces:
            v1,v2,v3 = face.halfedge.vertex, face.halfedge.next.vertex, face.halfedge.next.next.vertex
            tris.append([v1.as_tuple(),v2.as_tuple(), v3.as_tuple()])
        for tri in tris:
            triangle = [f"({pt[0]}, {pt[1]})" for pt in tri]
            # Write the triangle to the output file
            file.write(" ".join(triangle) + "\n")
    def compute_convex_hull(self):
        x_sorted = sorted(self.vertices, key=lambda v: v.x)

        L_upper = []
        L_upper.append(x_sorted[0])
        L_upper.append(x_sorted[1])

        for i in range(2,len(self.vertices)):
            L_upper.append(x_sorted[i])
            while len(L_upper) > 2 and orient2d(L_upper[-3].as_tuple(),L_upper[-2].as_tuple(),L_upper[-1].as_tuple()) >0:
                L_upper.remove(L_upper[-2])
        L_lower = []
        L_lower.append(x_sorted[-1])
        L_lower.append(x_sorted[-2])

        for j in reversed(range(0,len(self.vertices)-2)):
            L_lower.append(x_sorted[j])
            while len(L_lower) > 2 and orient2d(L_lower[-3].as_tuple(),L_lower[-2].as_tuple(),L_lower[-1].as_tuple()) >0:
                L_lower.remove(L_lower[-2])
        
        L_lower.remove(L_lower[0])
        L_lower.remove(L_lower[-1])

        self.convexhullvertices = L_upper + L_lower
    def handle_boundaries(self, boundary_hes):
        TODO()
        faces_to_remove = []
        halfedges_to_remove = []
        faces_to_add = []
        for he in boundary_hes:
            v_1 = he.vertex
            v_2 = he.next.vertex
            v_3 = he.next.next.vertex

            v_4 = he.next.opposite.vertex # v_3
            v_5 = he.next.next.opposite.vertex # v_1

            assert v_4 == v_3 and v_5 == v_1, "Setup does not match expected in handle boundaries"

            v_6 = he.next.opposite.next.next.vertex
            v_7 = he.next.next.opposite.next.next.vertex

            res = orient2d(v_6.as_tuple(), v_3.as_tuple(), v_7.as_tuple())
            if res < 0:
                faces_to_remove.extend([he.face, he.next.opposite.face, he.next.next.opposite.face])
                new_he = Halfedge(vertex=v_7,index=len(self.vertices))
                new_face = Face(index=len(self.faces),halfedge=new_he)
                new_he.next = he.next.opposite.next.next.next
                he.next.opposite.next.next.next = he.next.next.opposite.next
                he.next.next.opposite.next.next = new_he
                new_he.face = new_face
                new_he.next.face = new_face
                new_he.next.next.face = new_face
                faces_to_add.append(new_face)
            else:
                faces_to_remove.append(he.face)
                halfedges_to_remove.append(he)
        for f in faces_to_remove:
            self.faces.remove(f)
        for f in faces_to_add:
            self.faces.append(f)
            self.halfedges.append(f.halfedge)
    def special_flip(self, he, boundary_vertices):

        v_1 = he.vertex  
        v_2 = he.next.vertex  
        v_3 = he.next.next.vertex 

        v_4 = he.opposite.vertex 
        v_5 = he.opposite.next.vertex 
        v_6 = he.opposite.next.next.vertex 

        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for special_flip"
        
        assert v_1 in boundary_vertices, "v_1 not correct"

        
        #for i in boundary_vertices:
            #if i == v_1:
                #pt = v_1.as_tuple()
                #break
        
        #if pt == (-1,2):
            #res = orient2d(v_3.as_tuple(), v_2.as_tuple(), v_6.as_tuple())
        #elif pt == (-1,-1):
            #pass
        #elif pt == (2,-1):
            #pass
        #elif pt == (2,2):
            #pass


        # If v_3 v_2 v_6 make a left hand turn flip
        res = orient2d(v_3.as_tuple(), v_2.as_tuple(), v_6.as_tuple())

        if res > 0:
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

    def edge_flip(self, he, pr):
        v_1 = he.vertex  # This is the starting vertex of he
        v_2 = he.next.vertex  # The next vertex in he's triangle
        v_3 = he.next.next.vertex  # The last vertex in he's triangle

        v_4 = he.opposite.vertex  # The starting vertex of he.opposite
        v_5 = he.opposite.next.vertex  # The next vertex in he.opposite's triangle
        v_6 = he.opposite.next.next.vertex  # The last vertex in he.opposite's triangle

        # Ensure this is a valid edge for flipping: v2 == v4 and v1 == v5
        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        assert pr != v_6, "WARNING: pr =! v_6"
        res1 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_3.as_tuple(), v_6.as_tuple())
        res2 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_6.as_tuple(), v_3.as_tuple())

        if res2 >= 0 :
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
        if he.opposite == None:
            return
        he_next = he.next
        he_next_next = he.next.next
        op = he.opposite
        op_n = he.opposite.next
        op_nn = he.opposite.next.next
        if self.edge_flip(he, pr):
            #for he in self.halfedges:
                #self.legalize_edge(pr,he)
            self.legalize_edge(pr, he_next) 
            self.legalize_edge(pr, he_next_next) 
            self.legalize_edge(pr, op) 
            self.legalize_edge(pr, op_n) 
            self.legalize_edge(pr, op_nn) 

    def triangulate(self):
        to_triangulate = self.vertices[:-4]
        # Since last 4 we have manually triangulated
        for vertex in to_triangulate:
            for face in self.faces:
                res = face.inside(vertex)
                if res == True:
                    # inside the triangle
                    #STEP 1: draw edges from 3 corners to the new point

                    he = face.halfedge
                    init_he_next = he.next
                    init_he_next_next = init_he_next.next
                    assert init_he_next_next.next == he, print("Not a triangle homie")
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

                    #self.print_mesh("Before legalizing he", highlight=he)
                    self.legalize_edge(vertex, he)
                    #self.print_mesh("Before legalizing init_he_next", highlight=init_he_next)
                    self.legalize_edge(vertex,init_he_next)
                    #self.print_mesh("Before legalizing he next next ", highlight=init_he_next_next)
                    self.legalize_edge(vertex,init_he_next_next)
                    #self.print_mesh("After legalizing")


                elif res == -1:
                    # on the triangle
                    print("AAAAAAAAAAAAAAAAAAAAAAA")
                    pass
    def resethalfedges(self):
        for he in self.halfedges:
            he.visited = False
    def plot_convexhull(self):
        if len(self.convexhullvertices) == 0:
            return 
        # Plotting the original points and the convex hull
        plt.figure()
        # Original points
        plt.plot([v.x for v in self.vertices], [v.y for v in self.vertices], 'o', label='Points')

        # Convex hull
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
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        
        # Plot vertices
        plt.scatter(x, y, color='blue')
        for v in self.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')

        # Plot faces and halfedges
        for face in self.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            start_he = he

            while True:
                vertex = he.vertex
                next_vertex = he.next.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)

                midpoint_x = (vertex.x + next_vertex.x) / 2
                midpoint_y = (vertex.y + next_vertex.y) / 2

                if he.visited:
                    he = he.next
                    if he == start_he:
                        break
                    continue

                if he.opposite is None:
                    pass
                    #plt.text(midpoint_x, midpoint_y, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='orange', ha='center')
                else:
                    he.opposite.visited = True
                    #plt.text(midpoint_x -0.2, midpoint_y -0.2, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='purple', ha='center')
                    #plt.text(midpoint_x , midpoint_y, f"he{he.opposite.index}\n→he{he.opposite.next.index}",
                            #fontsize=8, color='purple', ha='center')

                he.visited = True



                he = he.next
                if he == start_he:
                    break

            # Close the triangle by adding the first point again
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])
            plt.plot(triangle_x, triangle_y, color='black')

        # Plot configuration
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(title)
        plt.grid(True)
        plt.show()
        self.resethalfedges()
    def print_boundary(self):
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        
        # Plot vertices
        plt.scatter(x, y, color='blue')
        for v in self.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')

        # Plot faces and halfedges
        for face in self.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            start_he = he

            while True:
                vertex = he.vertex
                next_vertex = he.next.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)

                midpoint_x = (vertex.x + next_vertex.x) / 2
                midpoint_y = (vertex.y + next_vertex.y) / 2

                if he.visited:
                    he = he.next
                    if he == start_he:
                        break
                    continue

                if he.opposite is None:
                    pass
                    #plt.text(midpoint_x, midpoint_y, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='orange', ha='center')
                else:
                    he.opposite.visited = True
                    #plt.text(midpoint_x -0.2, midpoint_y -0.2, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='purple', ha='center')
                    #plt.text(midpoint_x , midpoint_y, f"he{he.opposite.index}\n→he{he.opposite.next.index}",
                            #fontsize=8, color='purple', ha='center')

                he.visited = True



                he = he.next
                if he == start_he:
                    break

            # Close the triangle by adding the first point again
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])
            plt.plot(triangle_x, triangle_y, color='black')

        to_plot = []
        for he in self.halfedges:
            if he.opposite is None:
                to_plot.append(he)
        
        xs = [h.vertex.x for h in to_plot]
        ys = [h.vertex.y for h in to_plot]

        plt.scatter(xs, ys, color='orange')

        plt.title("Boundary")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()





    #def mandatory_edge_flip(self, he):
        #if he.opposite == None:
            #he_up = he.next
        #else:
            #he_up = he
        #v_1 = he_up.vertex  # This is the_up starting vertex of he_up
        #v_2 = he_up.next.vertex  # The_up next vertex in he_up's triangle
        #v_3 = he_up.next.next.vertex  # The_up last vertex in he_up's triangle

        #v_4 = he_up.opposite.vertex  # The_up starting vertex of he_up.opposite
        #v_5 = he_up.opposite.next.vertex  # The_up next vertex in he_up.opposite's triangle
        #v_6 = he_up.opposite.next.next.vertex  # The_up last vertex in he_up.opposite's triangle

        ## Ensure this is a valid edge for flipping: v2 == v4 and v1 == v5
        #assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        ## Che_upck Delaunay condition using incircle test (commented res1 as it was unused)
        ##res1 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_3.as_tuple(), v_6.as_tuple())

        ## Step 1: Cache_up the_up `next` pointers before modifying the_upm
        #he_up_next = he_up.next
        #he_up_next_next = he_up.next.next
        #op_he_up_next = he_up.opposite.next
        #op_he_up_next_next = he_up.opposite.next.next

        ## Step 2: Reassign vertices for the_up halfedges
        #he_up.vertex = v_6
        #he_up.opposite.vertex = v_3

        ## Step 3: Update the_up `next` pointers to reflect the_up new edge structure
        ## Triangle 1 (around he_up)
        #he_up.next = he_up_next_next  
        #he_up.next.next = op_he_up_next  
        #he_up.next.next.next = he_up

        ## Triangle 2 (around he_up.opposite)
        #he_up.opposite.next = op_he_up_next_next  
        #he_up.opposite.next.next = he_up_next  
        #he_up.opposite.next.next.next = he_up.opposite

        ## Step 4: Update faces
        #if he_up.face in self.faces:
            #self.faces.remove(he_up.face)
        #if he_up.opposite.face in self.faces:
            #self.faces.remove(he_up.opposite.face)
        #f1 = Face(len(self.faces),he_up)
        #self.faces.append(f1)
        #he_up.face = f1
        #f2 = Face(len(self.faces),he_up.opposite)
        #self.faces.append(f2)
        #he_up.opposite.face = f2
        #he_up.next.face = he_up.face
        #he_up.next.next.face = he_up.face
        #he_up.opposite.next.face = he_up.opposite.face
        #he_up.opposite.next.next.face = he_up.opposite.face
