#!/bin/bash

# Ask the user for a number
read -p "Enter a number: " number

# Run the first Python script with the user-provided number
python ./src/genpts.py "$number" pts.dat

# Run the Delaunay triangulation Python script
python ./src/del.py -i pts.dat -o triangles.dat &

# Run the test script
python3 tests/del_test.py &

wait
