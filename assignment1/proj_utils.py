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

def print_help():
    print(color.RED + "Error: Incorrect usage of arguments" + color.END)
    print("\t- Example usage: "+ color.YELLOW + "python del.py -i <INPUT_FILE> -o <OUTPUT_FILE>" + color.END)
    exit()


def print_num_pts_error():
    print(color.RED + "Error :Number of points does not correspond to number of lines retrieved from the file" + color.END)
    exit()