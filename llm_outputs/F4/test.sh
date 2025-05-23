#!/bin/bash


script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
benchmark_name=$(echo $script_dir | rev | cut -d "/" -f 3 | rev)
project_name=$(echo $script_dir | rev | cut -d "/" -f 2 | rev)
bug_id=$(echo $script_dir | rev | cut -d "/" -f 1 | rev)
dir_name=/experiment/$benchmark_name/$project_name/$bug_id

TEST_ID='1.tif'
BINARY_PATH="$dir_name/src/tools/rgb2ycbcr"


if [ -n "$2" ];
then
  BINARY_PATH=$2
fi


POC=$script_dir/tests/$TEST_ID
ASAN_OPTIONS=halt_on_error=0   timeout 10 $BINARY_PATH $POC out.tif  > $BINARY_PATH.out 2>&1


ret=$?
if [[ ret -eq 0 ]]
then
   err=$(cat $BINARY_PATH.out | grep 'Decoding error'  | wc -l)
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