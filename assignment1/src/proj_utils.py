import matplotlib.pyplot as plt
import numpy as np
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class Printer:
    def __init__(self,tmesh):
        self.tmesh = tmesh
    def plot_convexhull(self):
        if len(self.tmesh.convexhullvertices) == 0:
            return 
        # Plotting the original points and the convex hull
        plt.figure()
        # Original points
        plt.plot([v.x for v in self.tmesh.vertices], [v.y for v in self.tmesh.vertices], 'o', label='Points')

        # Convex hull
        hull_x = [v.x for v in self.tmesh.convexhullvertices] + [self.tmesh.convexhullvertices[0].x]  # closing the polygon
        hull_y = [v.y for v in self.tmesh.convexhullvertices] + [self.tmesh.convexhullvertices[0].y]  # closing the polygon
        plt.plot(hull_x, hull_y, 'r-', label='Convex Hull')

        plt.title("Convex Hull")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.legend()
        plt.show()
    def print_mesh(self, title="Fig"):
        x = [v.x for v in self.tmesh.vertices]
        y = [v.y for v in self.tmesh.vertices]
        
        # Plot vertices
        plt.scatter(x, y, color='blue')
        for v in self.tmesh.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')

        # Plot faces and halfedges
        for face in self.tmesh.faces:
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
                            #fontsize=8, color='purple', ha='center')
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
        self.tmesh.resethalfedges()



def print_help():
    print(color.RED + "Error: Incorrect usage of arguments" + color.END)
    print("\t- Example usage: "+ color.YELLOW + "python del.py -i <INPUT_FILE> -o <OUTPUT_FILE>" + color.END)
    exit()


def print_num_pts_error():
    print(color.RED + "Error :Number of points does not correspond to number of lines retrieved from the file" + color.END)
    exit()


