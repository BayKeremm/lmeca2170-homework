#!/bin/bash
i=0
while true; do
  # Remove the previous pts.dat file
  rm -f pts.dat

  # Generate a new pts.dat file with 1000 points
  python3 ./src/genpts.py 1000 pts.dat

  # Run the test and capture the output
  output=$(sh run_test.sh pts.dat 1)

  # Check if the output contains the desired string
  if [[ "$output" != *"The same triangulation. Good!"* ]]; then
    echo "Condition met, exiting loop."
    echo "$output"  # Print the final output if you want to see it
    break
  fi

  # Print the iteration count and increment
  echo "Iteration: $i"
  i=$((i + 1))
done
