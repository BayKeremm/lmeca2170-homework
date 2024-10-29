import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
import sys
import numpy as np 
from matplotlib.widgets import Button, TextBox

def toggle_input(event):
    # Toggle visibility of the generate points button and text box
    if button_generate.ax.get_visible():
        button_generate.ax.set_visible(False)
        ax_text_box.set_visible(False)
    else:
        button_generate.ax.set_visible(True)
        ax_text_box.set_visible(True)
    
    plt.draw()


def on_click(event):
    if event.inaxes != ax:
        return
    
    v = Vertex(x=float(event.xdata),
                                 y=float(event.ydata),
                                 index=len(TMESH.vertices)) 
    
    # Re-plot with the new point
    ax.scatter(event.xdata, event.ydata, color='red')
    TMESH.triangulate_one_step(new_vertex=v)
    next_step(1)
    plt.draw()

def next_step(event):
    # Call the triangulation step function
    if event != 1:
        TMESH.triangulate_one_step()
    
    # Clear and redraw the plot with updated edges or faces
    ax.cla()
    
    x = [v.x for v in TMESH.vertices]
    y = [v.y for v in TMESH.vertices]

    #for v in TMESH.vertices:
        #ax.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')
    ax.scatter(x, y, color='blue')
        
    # Plot faces and halfedges
    for face in TMESH.faces:
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
        ax.plot(triangle_x, triangle_y, color='black')

    TMESH.resethalfedges()
    
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    plt.draw()

def get_points(event):
    try:
        num_points = int(text_box.text)  # Get the integer number of points from the text box
    except ValueError:
        num_points = 3
    
    # Clear the current plot
    ax.cla()

    # Generate random points between 0 and 1 as floats
    x_points = np.random.rand(num_points) 
    y_points = np.random.rand(num_points) 

    points = []
    for i in range(num_points):
        points.append([x_points[i], y_points[i]])
    vertices = points_to_vertices(points)
    
    points_at_inf, initial_hes, initial_faces = create_initial_triangulation(vertices)
    vertices.extend(points_at_inf)
    global TMESH
    TMESH = TriangularMesh(vertices, initial_hes, initial_faces, debug=False)

    #for v in TMESH.vertices:
        #ax.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')
    # Scatter plot with separated x and y arrays
    ax.scatter(x_points, y_points, color='red')
    ax.set_title(f"Random Points (n={num_points})")
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    plt.draw()

    # Stack x and y points vertically to return as a single array
    return points

def create_initial_triangulation(vertices):
    x_min = y_min = float('inf')
    x_max = y_max = float('-inf')

    for vertex in vertices:
        x_min = min(x_min, vertex.x)
        y_min = min(y_min, vertex.y)
        x_max = max(x_max, vertex.x)
        y_max = max(y_max, vertex.y)

    dx = (x_max - x_min)
    dy = (y_max - y_min)

    scale_factor = 2000

    j = len(vertices)
    x_n = Vertex(x_min - dx * scale_factor, y_min - dy * scale_factor, j, None)
    x_n1 = Vertex(x_max + dx * scale_factor, y_min - dy * scale_factor, j+1, None)
    x_n2 = Vertex(x_max + dx * scale_factor, y_max + dy * scale_factor, j+2, None)
    x_n3 = Vertex(x_min - dx * scale_factor, y_max + dy * scale_factor, j+3, None)


    he1 = Halfedge(vertex=x_n, index=1)
    he2 = Halfedge(vertex=x_n2, index=2)
    he3 = Halfedge(vertex=x_n1, index=3)
    he4 = Halfedge(vertex=x_n2, index=4)
    he5 = Halfedge(vertex=x_n, index=5)
    he6 = Halfedge(vertex=x_n3, index=6)

    he1.opposite = he4
    he4.opposite = he1
    he1.next = he2
    he2.next = he3
    he3.next = he1
    he4.next = he5 
    he5.next = he6
    he6.next = he4

    points_at_inf = [x_n, x_n1, x_n2, x_n3]
    initial_hes = [he1, he2, he3, he4, he5, he6]
    faces = [[he1,he2,he3],[he4,he5,he6]]
    return points_at_inf, initial_hes, faces


if __name__== "__main__":
    DEBUG = False 
    REMOVEINF = False
    EXP = False

    INTERACTIVE = False
    try:
        idx_int = sys.argv.index("-INTER")
        interactive_flag = sys.argv[idx_int + 1]
        if int(interactive_flag) == 1:
            INTERACTIVE = True
    except ValueError:
        print("Argument '-INTER' not found.")
    except IndexError:
        print("Expected value after '-INTER' argument.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print(INTERACTIVE)

    if not INTERACTIVE:
        if len(sys.argv) < 5:
            print_usage()
        else:
            try:
                idx_input = sys.argv.index("-i")
                idx_output = sys.argv.index("-o")
            except:
                print_help()

            input_file = sys.argv[idx_input+1]
            output_file = sys.argv[idx_output+1]
    
        try:
            idx_deb = sys.argv.index("-DEBUG")
            deb = sys.argv[idx_deb+1]
            if int(deb)==1:
                DEBUG = True
        except:
            print("DAFUQ")
        try:
            idx_inf = sys.argv.index("-REMOVEINF")
            inf = sys.argv[idx_inf+1]
            if int(inf)==1:
                REMOVEINF = True
        except:
            print("DAFUQ")
        try:
            idx_exp = sys.argv.index("-EXPORT")
            exp = sys.argv[idx_exp+1]
            if int(exp)==1:
                EXP = True
        except:
            print("DAFUQ")

        #print("------------")
        #print(DEBUG)
        #print(EXP)
        #print(REMOVEINF)
        #print(INTERACTIVE)
        #print("------------")

        fi = open(input_file,"r")
        fo = open(output_file,"w")

        lines = [i.strip("\n") for i in fi.readlines()]
        num_pts = lines[0]
        pts = lines[1:]

        assert len(pts) == int(num_pts) , print_num_pts_error()


        vertices = []
        j = 0
        for pt in pts:
            l = pt.split()
            vertices.append(Vertex(float(l[0]),float(l[1]),j,None))
            j +=1

        points_at_inf, inital_hes, initial_faces = create_initial_triangulation(vertices)
        vertices.extend(points_at_inf)

        T = TriangularMesh(vertices,inital_hes,initial_faces,DEBUG)

        T.triangulate()

        if EXP and not REMOVEINF:
            T.export(fo)

        if DEBUG and not REMOVEINF:
            T.print_mesh("Triangulation with points at infinity")

        boundary_hes = [inital_hes[1],inital_hes[2],inital_hes[4],inital_hes[5]]
        boundary_vs = points_at_inf

        if REMOVEINF:
            print("Removing points at infinity")
            T.handle_boundaries(boundary_hes, boundary_vs)
    
        if EXP and REMOVEINF:
            T.export(fo)
    
        if DEBUG and REMOVEINF:
            T.print_mesh("RESULT after removal of points at infinity")
    

        fi.close()
        fo.close()
    else:
        # Interactive mode
        # Create a figure and axis

        ## Add a button widget
        #ax_button = plt.axes([0.4, 0.05, 0.2, 0.075])  # Position of the button
        #button = Button(ax_button, 'Generate Points')

        ## Add a text box widget for inputting the number of points
        #ax_text_box = plt.axes([0.4, 0.15, 0.2, 0.05])  # Position of the text box
        #text_box = TextBox(ax_text_box, "Number of Points", initial="3")

        #ax_button_next = plt.axes([0.6, 0.05, 0.2, 0.075])
        #button_next = Button(ax_button_next, 'Next Step')
        #button_next.on_clicked(next_step)


        ## Set the button to call the function on click
        #button.on_clicked(get_points)

        ## Initial plot setup

        # Create figure with a larger size
        fig, ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.35)  # Leave space for button and input

        # Positioning the buttons and text box
        ax_button_toggle = plt.axes([0.1, 0.05, 0.2, 0.075])  # Manual button on the left
        button_toggle = Button(ax_button_toggle, 'Manual')
        button_toggle.on_clicked(toggle_input)

        ax_text_box = plt.axes([0.4, 0.15, 0.15, 0.075])  # Text box in the middle (adjusted for vertical layout)
        text_box = TextBox(ax_text_box, "Enter number", initial="3")

        ax_button_generate = plt.axes([0.4, 0.05, 0.15, 0.075])  # Generate Points button below text box
        button_generate = Button(ax_button_generate, 'Generate Points')
        button_generate.on_clicked(get_points)

        ax_button_next = plt.axes([0.6, 0.05, 0.2, 0.075])  # Next Step button on the right
        button_next = Button(ax_button_next, 'Next Step')
        button_next.on_clicked(next_step)
        
        ax.set_xlim(-0.5, 1.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_title("Homework 1 Interactive mode")
        
        
        

        fig.canvas.mpl_connect('button_press_event', on_click)

        # Display the plot window
        plt.show()

        pass

    