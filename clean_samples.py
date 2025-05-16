import argparse
import os
import re
import subprocess
import json
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process SNx samples: create/update samples, strip comments, or clean directories."
    )
    parser.add_argument(
        'create_sample', nargs='?', type=int, choices=[0, 1], default=1,
        help='1 to create/update samples, 0 to skip creating samples'
    )
    parser.add_argument(
        'remove_comments', nargs='?', type=int, choices=[0, 1], default=0,
        help='1 to strip comments and update JSON, 0 to skip comment removal'
    )
    parser.add_argument(
        'x', nargs='?', type=int, default=1,
        help='SN index (1-50), or 0 for all when both flags are 0'
    )
    return parser.parse_args()


def replace_workdir(script_path, new_workdir):
    """
    Replace the -w argument in a defects4j checkout line to new_workdir.
    """
    pattern = re.compile(r"(-w\s+)(\S+)")
    lines = []
    with open(script_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('defects4j checkout'):
                line = pattern.sub(rf"\1{new_workdir}", line)
            lines.append(line)
    with open(script_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def process_sample(sn):
    base = f"SN{sn}"
    input_dir = os.path.join(base, 'manual_inputs')

    for subname, script_name in [(f"SN{sn}_buggy", 'downloadBuggy.sh'),
                                 (f"SN{sn}_fixed", 'downloadFixed.sh')]:
        target_dir = os.path.join(base, subname)
        script_path = os.path.join(input_dir, script_name)
        if not os.path.isfile(script_path):
            continue

        # Determine if target_dir already contains projects
        has_contents = os.path.isdir(target_dir) and bool(os.listdir(target_dir))

        if not has_contents:
            # ensure target directory exists and is empty
            if os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)

            # point workdir to ../subname, run script
            replace_workdir(script_path, os.path.join('..', subname))
            os.chmod(script_path, 0o755)

            orig_cwd = os.getcwd()
            os.chdir(input_dir)
            subprocess.run([script_name], check=True)
            os.chdir(orig_cwd)

        # In all cases, reset checkout to ./projects (do not run)
        replace_workdir(script_path, './projects')


def remove_comments_from_file(path):
    """
    Remove Java comments from file at path. Returns set of 1-based line numbers removed entirely.
    """
    removed = set()
    new_lines = []
    in_block = False
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if in_block:
            if '*/' in stripped:
                in_block = False
                line = re.sub(r".*?\*/", '', line)
                if not line.strip():
                    removed.add(idx+1)
                    continue
            else:
                removed.add(idx+1)
                continue

        if '/*' in line:
            before, _, after = line.partition('/*')
            if '*/' in after:
                after = after.split('*/', 1)[1]
                line = before + after
            else:
                in_block = True
                line = before
                if not before.strip():
                    removed.add(idx+1)
                    continue

        if '//' in line:
            code, _ = line.split('//', 1)
            if not code.strip():
                removed.add(idx+1)
                continue
            line = code + '\n'

        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    return removed


def adjust_line(original, removed_set):
    return original - sum(1 for r in removed_set if r < original)


def update_json(input_json_path, removed_buggy, removed_fixed):
    data = json.load(open(input_json_path, 'r', encoding='utf-8'))
    buggy_fields = [
        'vul_code_func_start_line', 'vul_code_func_end_line',
        'vul_code_block_start_line', 'vul_code_block_end_line',
        'vul_code_initial_block_start', 'vul_code_initial_block_end',
        'vul_code_line', 'rem_start', 'rem_end', 'add_start', 'add_end'
    ]
    for fld in buggy_fields:
        if fld in data:
            data[fld] = adjust_line(data[fld], removed_buggy)
    fixed_fields = [
        'vul_code_func_fixed_start_line', 'vul_code_func_fixed_end_line',
        'vul_code_block_fixed_start_line', 'vul_code_block_fixed_end_line'
    ]
    for fld in fixed_fields:
        if fld in data:
            data[fld] = adjust_line(data[fld], removed_fixed)

    if 'vul_code_lines' in data:
        data['vul_code_lines'] = [
            str(adjust_line(int(x), removed_buggy)) for x in data['vul_code_lines']
        ]
    if 'vul_code_context_lines' in data:
        data['vul_code_context_lines'] = [
            f"{adjust_line(int(s), removed_buggy)}-{adjust_line(int(e), removed_buggy)}"
            for s_e in data['vul_code_context_lines']
            for s, e in [s_e.split('-')]
        ]
    if 'context_lines' in data:
        new_ctx = []
        for entry in data['context_lines']:
            for k, ranges in entry.items():
                new_ranges = []
                for rng in ranges:
                    start, end = map(int, rng.split('-'))
                    new_ranges.append(
                        f"{adjust_line(start, removed_buggy)}-{adjust_line(end, removed_buggy)}"
                    )
                new_ctx.append({k: new_ranges})
        data['context_lines'] = new_ctx

    if 'vul_description' in data:
        data['vul_description'] = 'memory corruption vulnerability'

    with open(input_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def remove_comments_and_update(sn):
    base = f"SN{sn}"
    input_dir = os.path.join(base, 'manual_inputs')
    input_json = os.path.join(input_dir, 'inputConfig.json')
    rel_path = json.load(open(input_json, 'r', encoding='utf-8'))['vul_code_file_rel_path']
    buggy_file = os.path.join(base, f"SN{sn}_buggy", rel_path)
    fixed_file = os.path.join(base, f"SN{sn}_fixed", rel_path)
    removed_buggy = remove_comments_from_file(buggy_file)
    removed_fixed = remove_comments_from_file(fixed_file)
    update_json(input_json, removed_buggy, removed_fixed)


def clean_sample(sn):
    base = f"SN{sn}"
    for sub in [f"SN{sn}_buggy", f"SN{sn}_fixed"]:
        target = os.path.join(base, sub)
        if os.path.isdir(target):
            for item in os.listdir(target):
                path = os.path.join(target, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)


def main():
    args = parse_args()
    # Clean mode: if both flags are 0
    if args.create_sample == 0 and args.remove_comments == 0:
        if args.x == 0:
            # clean all SN1-SN50
            for i in range(1, 51):
                clean_sample(i)
        else:
            # clean only specified SNx
            clean_sample(args.x)
        return

    # Otherwise, per-SNx operations
    if args.create_sample == 1:
        process_sample = globals().get('process_sample')
        if process_sample:
            process_sample(args.x)
    if args.remove_comments == 1:
        remove_comments_and_update(args.x)

if __name__ == '__main__':
    main()

