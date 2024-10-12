import matplotlib.pyplot as plt
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
        self.vertices = tmesh.vertices
        self.faces = tmesh.faces
        self.halfedges = tmesh.halfedges
    def print_mesh(self):
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        plt.scatter(x, y, color='blue')
        for v in self.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')
 
        for face in self.faces:
            he = face.halfedge

            triangle_x = []
            triangle_y = []
            start_he = he
            while True:
                vertex = he.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)

                he = he.next
                if he == start_he:
                    break
        
            # Close the triangle 
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])

            plt.plot(triangle_x, triangle_y, color='black')

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Triangular Mesh')
        plt.grid(True)
        plt.show()



def print_help():
    print(color.RED + "Error: Incorrect usage of arguments" + color.END)
    print("\t- Example usage: "+ color.YELLOW + "python del.py -i <INPUT_FILE> -o <OUTPUT_FILE>" + color.END)
    exit()


def print_num_pts_error():
    print(color.RED + "Error :Number of points does not correspond to number of lines retrieved from the file" + color.END)
    exit()


