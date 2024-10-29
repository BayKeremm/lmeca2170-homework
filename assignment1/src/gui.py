from matplotlib.widgets import Button, TextBox
import matplotlib.pyplot as plt
import numpy as np
from halfedge import Vertex
from proj_utils import *
from triangularmesh import TriangularMesh

class Delaunay_GUI:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.35)  
    
        self.ax_button_toggle = plt.axes([0.1, 0.05, 0.2, 0.075])  

        self.button_toggle = Button(self.ax_button_toggle, 'Generate Manually')
        self.button_toggle.on_clicked(self.toggle_input)

        self.ax_text_box = plt.axes([0.4, 0.15, 0.15, 0.075])  # Text box in the middle (adjusted for vertical layout)
        self.text_box = TextBox(self.ax_text_box, "Enter number", initial="3")

        self.ax_button_generate = plt.axes([0.4, 0.05, 0.15, 0.075])  # Generate Points button below text box
        self.button_generate = Button(self.ax_button_generate, 'Generate Points')
        self.button_generate.on_clicked(self.get_points)

        self.ax_button_next = plt.axes([0.6, 0.05, 0.2, 0.075])  # Next Step button on the right
        self.button_next = Button(self.ax_button_next, 'Next Step')
        self.button_next.on_clicked(self.next_step)
        
        self.ax.set_xlim(-0.5, 1.5)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_title("Homework 1 Interactive mode")

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
    
    def show(self):
        plt.show() 

    def toggle_input(self, event):
        if self.button_generate.ax.get_visible():
            self.button_generate.ax.set_visible(False)
            self.ax_text_box.set_visible(False)
            points_at_inf, initial_hes, initial_faces = create_initial_triangulation()
            self.TMESH = TriangularMesh(points_at_inf, initial_hes, initial_faces, debug=False)
            self.TMESH.triangulate_one_step()
            self.next_step(1)
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
         
        if self.button_generate.ax.get_visible() is False:
            # we are manually adding 
            v = Vertex(x=float(event.xdata),
                                        y=float(event.ydata),
                                        index=len(self.TMESH.vertices)) 
            self.TMESH.vertices.insert(-4, v)
            self.ax.scatter(event.xdata, event.ydata, color='red')
        else:
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
    
        points_at_inf, initial_hes, initial_faces = create_initial_triangulation(vertices)
        vertices.extend(points_at_inf)
        self.TMESH = TriangularMesh(vertices, initial_hes, initial_faces, debug=False)

        self.ax.scatter(x_points, y_points, color='red')
        self.ax.set_title(f"Random Points (n={num_points})")
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
    
        x = [v.x for v in self.TMESH.vertices]
        y = [v.y for v in self.TMESH.vertices]

        self.ax.scatter(x, y, color='blue')
        
        # Plot faces and halfedges
        for face in self.TMESH.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            start_he = he

            while True:
                vertex = he.vertex
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
            self.ax.plot(triangle_x, triangle_y, color='black')

        self.TMESH.resethalfedges()
        self.ax.set_xlim(-0.5, 1.5)
        self.ax.set_ylim(-0.5, 1.5)
        plt.draw()