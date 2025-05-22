#!/usr/bin/env bash

set -euo pipefail

vul_ids=( SB{1..20} SA{4..7} SA{10..12} SC{1..5} SD{1..3} SE{2..7})

for vul_id in "${vul_ids[@]}"; do
  echo "=== Processing $vul_id ==="

  # turn off 'exit on error' for these steps
  set +e

  python3 knod_evaluation_llama_woreasoning.py "$vul_id"
  ret1=$?
  set -e

  # report any failures, but don’t exit
  if [ $ret1 -ne 0 ]; then
    echo "One or more steps failed for $vul_id (codes: eval=$ret1)"
  else
    echo "All steps succeeded for $vul_id"
  fi

  echo "=== Done $vul_id ==="
  echo
done

echo "All done!"

