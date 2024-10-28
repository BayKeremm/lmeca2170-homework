#!/bin/bash

# Get the input file from the command-line argument
FILE=$1

# Run the Python scripts with the input file
python ./src/delaunay.py -i "$FILE" -o triangles.Calc -DEBUG 1  -REMOVEINF 1 -EXPORT 0 &


# Run the test script
python tests/del_test.py -i "$FILE" -o triangles.True -DEBUG 1 -REMOVEINF 1 -EXPORT 0 &

# Wait for both background processes to finish
wait
