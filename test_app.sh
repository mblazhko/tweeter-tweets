#!/bin/bash

# Function to perform the benchmark
benchmark() {
  local start_time
  start_time=$(date +%s.%N)
  # Perform the actual curl command
  curl -X 'POST' \
    'http://127.0.0.1:8000/search' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '[
      {
        "q": "python",
        "since": "2023-11-12",
        "until": "2023-12-12"
      }
    ]'
  local end_time
  end_time=$(date +%s.%N)

  local execution_time
  execution_time=$(echo "$end_time - $start_time" | bc)
  echo "Execution Time: $execution_time seconds"
}

# Run the benchmark function
benchmark
