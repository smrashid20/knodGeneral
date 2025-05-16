#!/usr/bin/env bash
#
# run_all.sh – preprocess, prepare, and generate outputs for a set of vulnerability IDs

set -euo pipefail

# Define the list of IDs: SB1–SB19, SA4–SA7, SA10–SA12
vul_ids=( SB{15..19} SA{4..7} SA{10..12} )

for vul_id in "${vul_ids[@]}"; do
  echo "=== Processing $vul_id ==="

  # turn off 'exit on error' for these steps
  set +e

  python3 preprocess_inputs.py "$vul_id"
  ret1=$?
  python3 prepare_general_input.py
  ret2=$?
  python3 generate_general_output.py \
    ../data/models/general_v2/5.pt \
    ../data/models/insert_v2/5.pt
  ret3=$?

  # turn 'exit on error' back on
  set -e

  # report any failures, but don’t exit
  if [ $ret1 -ne 0 ] || [ $ret2 -ne 0 ] || [ $ret3 -ne 0 ]; then
    echo "One or more steps failed for $vul_id (codes: preprocess=$ret1 prepare=$ret2 generate=$ret3)"
  else
    echo "All steps succeeded for $vul_id"
  fi

  echo "=== Done $vul_id ==="
  echo
done

echo "All done!"

