#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "Script directory: $script_dir"

benchmark_name=$(echo $script_dir | rev | cut -d "/" -f 3 | rev)
echo "Benchmark name: $benchmark_name"
project_name=$(echo $script_dir | rev | cut -d "/" -f 2 | rev)
echo "Project name: $project_name"
bug_id=$(echo $script_dir | rev | cut -d "/" -f 1 | rev)
echo "Bug ID: $bug_id"

dir_name="/experiment/$benchmark_name/$project_name/$bug_id"
echo "Experiment directory: $dir_name"

TEST_ID='1.gif'
echo "Test ID: $TEST_ID"
BINARY_PATH="$dir_name/src/tools/gif2tiff"
echo "Default binary path: $BINARY_PATH"

# Allow override of binary path as $1
if [ -n "$1" ]; then
  BINARY_PATH="$1"
  echo "Overriding binary path with: $BINARY_PATH"
fi

echo "POC file: $script_dir/tests/$TEST_ID"
POC="$script_dir/tests/$TEST_ID"

echo "Running: timeout 10 $BINARY_PATH $POC out.tif"
timeout 10 $BINARY_PATH $POC out.tif > $BINARY_PATH.out 2>&1

ret=$?
echo "Exit status: $ret"

if [[ $ret -eq 0 ]] || [[ $ret -eq 1 ]]; then
  err=$(grep -c 'AddressSanitizer' "$BINARY_PATH.out")
  echo "AddressSanitizer occurrences: $err"
  if [[ $err -eq 0 ]]; then
    echo "Result: PASS"
    exit 0
  else
    echo "Result: FAIL"
    exit 128
  fi
else
  echo "Result: FAIL (unexpected exit code)"
  exit $ret
fi
