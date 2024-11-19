from matplotlib.widgets import Button, TextBox
import matplotlib.pyplot as plt
import numpy as np
from halfedge import Vertex
from proj_utils import *
from triangularmesh import TriangularMesh

class Delaunay_GUI:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.28)  
    
        # Generate manually button
        self.ax_button_toggle = plt.axes([0.1, 0.05, 0.2, 0.075])  
        self.button_toggle = Button(self.ax_button_toggle, 'Generate Manually')
        self.button_toggle.on_clicked(self.toggle_input)

        # Text box in the middle
        self.ax_text_box = plt.axes([0.4, 0.15, 0.15, 0.075])  
        self.text_box = TextBox(self.ax_text_box, "Enter number", initial="3")

        # Generate Points button below text box
        self.ax_button_generate = plt.axes([0.4, 0.05, 0.15, 0.075])  
        self.button_generate = Button(self.ax_button_generate, 'Generate Points')
        self.button_generate.on_clicked(self.get_points)

        # Next Step button on the right
        self.ax_button_next = plt.axes([0.6, 0.05, 0.2, 0.075])  
        self.button_next = Button(self.ax_button_next, 'Next Step')
        self.button_next.on_clicked(self.next_step)

        # Show convex hull
        self.ax_button_hull = plt.axes([0.1, 0.15, 0.15, 0.07])  # Generate Points button below text box
        self.button_hull = Button(self.ax_button_hull, 'Toggle convex hull')
        self.button_hull.on_clicked(self.toggle_convex_hull)
        
        # Show voronoi cells
        self.ax_button_voronoi = plt.axes([0.6, 0.15, 0.15, 0.07])  # Generate Points button below text box
        self.button_voronoi = Button(self.ax_button_voronoi, 'Voronoi Diagram')
        self.button_voronoi.on_clicked(self.toggle_voronoi_cells)
        
        
        self.ax.set_xlim(-0.5, 1.5)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_title("Homework 1 Interactive mode")

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.ch = True
    
    def show(self):
        plt.show() 

    def toggle_voronoi_cells(self, event):
        
        if not hasattr(self, 'TMESH') or self.TMESH is None or not hasattr(self, 'triangulation_lines'):
            return  # Exit if TMESH does not exist or is None

        # Clear any previous Voronoi cells if they exist
        if hasattr(self, 'voronoi_points') and self.voronoi_points is not None:
            for point in self.voronoi_points:
                point.remove()
            for line in self.voronoi_lines:
                line.remove()
            self.voronoi_points = None
            self.voronoi_lines = None
            for line in self.triangulation_lines:
                if line.get_color() == "gray":
                    continue
                line.set_alpha(0.3)
            plt.draw()
            return
        for line in self.triangulation_lines:
            if line.get_color() == "gray":
                continue
            line.set_alpha(0.05)  

        centers, circumcenters = self.TMESH.get_dual_voronoi()
        self.voronoi_points = []
        self.voronoi_lines = []

        for center in centers:
            point, = self.ax.plot(center[0], center[1])  
            self.voronoi_points.append(point)
        
        # Draw lines between circumcenters of neighboring faces
        for face in self.TMESH.faces:
            circumcenter_x, circumcenter_y = circumcenters[face]
            he = face.halfedge

            # Iterate through each neighboring face
            for i in range(3):
                if he.opposite is not None:  # Check if neighbor exists
                    neighbor = he.opposite.face
                    if neighbor in circumcenters:
                        neighbor_x, neighbor_y = circumcenters[neighbor]

                        # Draw line between this face's circumcenter and neighbor's circumcenter
                        line, = self.ax.plot([circumcenter_x, neighbor_x], [circumcenter_y, neighbor_y], 'red', alpha=0.4)
                        self.voronoi_lines.append(line)

                he = he.next  # Move to next half-edge
        plt.draw()

    def toggle_convex_hull(self, event):
        if not hasattr(self, 'TMESH') or self.TMESH is None:
            return  # Exit if TMESH does not exist or is None

        if self.ch:
            ch_vertices = self.TMESH.compute_convex_hull()
            if len(ch_vertices) == 0:
                return 

            # Convex hull
            hull_x = [v.x for v in ch_vertices] + [ch_vertices[0].x]  # Closing the polygon
            hull_y = [v.y for v in ch_vertices] + [ch_vertices[0].y]  # Closing the polygon
            self.hull_line, = self.ax.plot(hull_x, hull_y, 'r-', label='Convex Hull')
            plt.draw()
            self.ch = False
        else:
            self.ch = True
            # Remove the convex hull line
            if hasattr(self, 'hull_line'):
                self.hull_line.remove()
                plt.draw()

            

    def toggle_input(self, event):
        if self.button_generate.ax.get_visible():
            self.button_generate.ax.set_visible(False)
            self.ax_text_box.set_visible(False)
            points_at_inf, initial_hes, initial_faces = create_initial_triangulation(interactive=True)
            self.points_at_inf = points_at_inf
            self.TMESH = TriangularMesh(points_at_inf, initial_hes, initial_faces, debug=False)
            # I do not know why i put this 
            #self.TMESH.triangulate_one_step()
            #self.next_step(1)
            self.button_toggle.label.set_text('Reset')
        else:
            self.button_generate.ax.set_visible(True)
            self.ax_text_box.set_visible(True)
            self.button_toggle.label.set_text('Generate Manually')
            self.TMESH = None
        self.ax.cla()
    
        plt.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        
        if not hasattr(self, 'TMESH') or self.TMESH is None:
            return  # Exit if TMESH does not exist or is None
         
        v = Vertex(x=float(event.xdata),
                                    y=float(event.ydata),
                                    index=len(self.TMESH.vertices)) 
    
        # Re-plot with the new point
        self.ax.scatter(event.xdata, event.ydata, color='red')
        self.TMESH.triangulate_one_step(new_vertex=v)
        self.next_step(1)
        plt.draw()
    def get_points(self, event):
        try:
            num_points = int(self.text_box.text) 
        except ValueError:
            num_points = 3
    
        # Clear the current plot
        self.ax.cla()

        x_points = np.random.rand(num_points) 
        y_points = np.random.rand(num_points) 

        points = []
        for i in range(num_points):
            points.append([x_points[i], y_points[i]])
        vertices = points_to_vertices(points)
    
        points_at_inf, initial_hes, initial_faces = create_initial_triangulation(vertices, interactive=True)
        self.points_at_inf = points_at_inf
        vertices.extend(points_at_inf)
        self.TMESH = TriangularMesh(vertices, initial_hes, initial_faces, debug=False)

        self.ax.scatter(x_points, y_points, color='blue')
        #self.ax.set_title(f"Random Points (n={num_points})")
        self.ax.set_xlim(-0.5, 1.5)
        self.ax.set_ylim(-0.5, 1.5)
        plt.draw()

        return points
    def next_step(self, event):
        if not hasattr(self, 'TMESH') or self.TMESH is None or len(self.TMESH.vertices)==4:
            return  # Exit if TMESH does not exist or is None

        # Call the triangulation step function
        if event != 1:
            self.TMESH.triangulate_one_step()
    
        # Clear and redraw the plot with updated edges or faces
        self.ax.cla()
    
        # USEFUL FOR DEBUG
        #for v in self.TMESH.vertices:
            #self.ax.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')

        self.triangulation_lines = [] 
        # Plot faces and halfedges
        for face in self.TMESH.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            start_he = he

            while True:
                vertex = he.vertex
                n_vertex = he.next.vertex
                nn_vertex = he.next.next.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)

                if he.visited:
                    he = he.next
                    if he == start_he:
                        break
                    continue

                if he.opposite is None:
                    pass
                else:
                    he.opposite.visited = True

                he.visited = True
                
                he = he.next
                if he == start_he:
                    break

            # Close the triangle by adding the first point again
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])
            
            line, = self.ax.plot(triangle_x, triangle_y, color='black', alpha=0.35)
            self.triangulation_lines.append(line)


        x = [v.x for v in self.TMESH.vertices]
        y = [v.y for v in self.TMESH.vertices]


        self.ax.scatter(x, y, color='blue')

        self.TMESH.resethalfedges()
        self.ax.set_xlim(-0.5, 1.5)
        self.ax.set_ylim(-0.5, 1.5)
        plt.draw()