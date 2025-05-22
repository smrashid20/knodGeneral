#!/bin/bash
# A wrapper script to run the tiffcrop tool under AddressSanitizer and
# instrumented to print PASS/FAIL results before each exit.

# Ensure EXPERIMENT_DIR has a default
if [ -z "$EXPERIMENT_DIR" ]; then
  echo "EXPERIMENT_DIR NOT SET, TAKING DEFAULT VALUE TO BE ~"
fi
EXPERIMENT_DIR=${EXPERIMENT_DIR:-"~"}

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
benchmark_name=$(echo "$script_dir" | rev | cut -d "/" -f 3 | rev)
project_name=$(echo "$script_dir" | rev | cut -d "/" -f 2 | rev)
bug_id=$(echo "$script_dir" | rev | cut -d "/" -f 1 | rev)
dir_name="/experiment/$benchmark_name/$project_name/$bug_id"

TEST_ID='1.tif'
BINARY_PATH="$dir_name/src/tools/tiffcrop"

# Allow override of binary path
if [ -n "$2" ]; then
  BINARY_PATH=$2
fi

echo "Running tiffcrop tool: $BINARY_PATH on POC $TEST_ID"

POC="$script_dir/tests/$TEST_ID"
ASAN_OPTIONS=halt_on_error=0 timeout 10 "$BINARY_PATH" "$POC" out.tif > "$BINARY_PATH.out" 2>&1

ret=$?
echo "Tool exited with return code: $ret"

if [[ $ret -eq 0 ]]; then
  # Count ASan errors; suppress grep errors
  err_count=$(grep -c 'AddressSanitizer' "$BINARY_PATH.out" 2>/dev/null)
  echo "AddressSanitizer errors found: $err_count"
  if [[ $err_count -eq 0 ]]; then
    echo "Result: PASS"
    exit 0
  else
    echo "Result: FAIL"
    exit 128
  fi
else
  echo "Result: FAIL"
  exit $ret
fi
