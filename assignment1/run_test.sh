#!/bin/bash

# Get the input file from the command-line argument
FILE=$1

# Remove triangles.Calc and triangles.True if they exist
if [ -f triangles.Calc ]; then
    rm triangles.Calc
fi

if [ -f triangles.True ]; then
    rm triangles.True
fi

# Run the Python scripts with the input file
python ./src/delaunay.py -i "$FILE" -o triangles.Calc -DEBUG 0 -REMOVEINF 1 -EXPORT 1&

# Run the test script
python tests/del_test.py -i "$FILE" -o triangles.True -DEBUG 0 -REMOVEINF 1 -EXPORT 1&

# Wait for both background processes to finish
wait

# Compare the results
python tests/compare_files.py triangles.Calc triangles.True