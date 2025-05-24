#!/usr/bin/env python3
import os
import json
import argparse

def collect_flags(base_dir):
    """
    Walk the base_dir, find JSONs under each vul_id subfolder,
    and build a mapping:
      vul_id -> {
        "Plausible": [rel paths where Plausible is True],
        "Plausible_Reasoning": [rel paths where Plausible is not True AND Plausible_Reasoning is True]
      }
    """
    results = {}

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith('.json'):
                continue

            full_path = os.path.join(root, fname)
            # path relative to base_dir, e.g. "A1/subdir/foo.json"
            relpath = os.path.relpath(full_path, base_dir)
            parts = relpath.split(os.sep)
            if len(parts) < 2:
                continue

            vul_id = parts[0]
            rel_to_vul = os.path.join(*parts[1:])

            # load JSON
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            # init buckets
            if vul_id not in results:
                results[vul_id] = {
                    "Plausible": [],
                    "Plausible_Reasoning": []
                }

            plausible_flag = data.get('Plausible')
            reasoning_flag = data.get('Plausible_Reasoning')

            # collect if Plausible is True
            if plausible_flag is True:
                results[vul_id]["Plausible"].append(rel_to_vul)

            # collect for Plausible_Reasoning only if Plausible is not True
            if reasoning_flag is True and plausible_flag is not True:
                results[vul_id]["Plausible_Reasoning"].append(rel_to_vul)

    return results

def main():
    parser = argparse.ArgumentParser(
        description="Summarize which JSONs per-vulnerability had Plausible and Plausible_Reasoning flags."
    )
    parser.add_argument('base_dir',
        help="Root folder containing per-vulnerability subdirs (e.g. A1, A2, …)")
    parser.add_argument('output_file',
        help="Path for the summary JSON (e.g. summary.json)")
    args = parser.parse_args()

    summary = collect_flags(args.base_dir)

    # sort each list of paths
    for vid, buckets in summary.items():
        buckets["Plausible"].sort()
        buckets["Plausible_Reasoning"].sort()


    # sort vul_ids alphabetically
    ordered = {vid: summary[vid] for vid in sorted(summary)}

    with open(args.output_file, 'w', encoding='utf-8') as out:
        json.dump(ordered, out, indent=2)

    print(f"Wrote summary for {len(ordered)} vulnerabilities to {args.output_file}")

if __name__ == '__main__':
    main()
