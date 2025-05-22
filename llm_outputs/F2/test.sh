#!/bin/bash
# A wrapper script to run the thumbnail tool under AddressSanitizer and
# instrumented to print PASS/FAIL results before each exit.

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
benchmark_name=$(echo "$script_dir" | rev | cut -d "/" -f 3 | rev)
project_name=$(echo "$script_dir" | rev | cut -d "/" -f 2 | rev)
bug_id=$(echo "$script_dir" | rev | cut -d "/" -f 1 | rev)
dir_name="/experiment/$benchmark_name/$project_name/$bug_id"

# Always use TEST_ID 1.tif
TEST_ID="1.tif"
BINARY_PATH="$dir_name/src/tools/thumbnail"

# Allow override of binary path as $1
if [ -n "$1" ]; then
  BINARY_PATH="$1"
fi

echo "Running thumbnail tool: $BINARY_PATH on POC $TEST_ID"

POC="$script_dir/tests/$TEST_ID"
ASAN_OPTIONS=detect_leaks=0 timeout 10 \
  "$BINARY_PATH" "$POC" out.tif \
  > "$BINARY_PATH.out" 2>&1

ret=$?

ret=$?
if [[ ret -eq 0 ]] || [[ ret -eq 1 ]]
then
   err=$(cat $BINARY_PATH.out | grep 'AddressSanitizer'  | wc -l)
    if [[ err -eq 0 ]]
    then
      echo "Result: PASS"
      exit 0
    else
      echo "Result: FAIL"
      exit 128
    fi;
else
  echo "Result: FAIL"
   exit $ret
fi
