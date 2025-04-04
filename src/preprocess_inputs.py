import os
import shutil
import json
import subprocess
import sys

def process_vulnerability(vulnerability_id):
    print(f"[INFO] Processing vulnerability: {vulnerability_id}")

    base_dir = os.path.abspath(os.path.join('..'))
    syn_dataset_dir = os.path.join(base_dir, 'SyntheticDataset', vulnerability_id)
    buggy_dir = os.path.join(syn_dataset_dir, f"{vulnerability_id}_buggy")
    manual_inputs_dir = os.path.join(syn_dataset_dir, 'manual_inputs')

    general_data_dir = os.path.join(base_dir, 'general_data', f"{vulnerability_id}_1")
    meta_file_path = os.path.join(base_dir, 'data', 'general_input', 'meta.txt')
    general_input_dir = os.path.join(base_dir, 'data', 'general_input')
    general_output_dir = os.path.join(base_dir, 'data', 'general_output')

    # Step 0: Clear contents of general_input and general_output
    print(f"[INFO] Clearing contents of {general_input_dir} and {general_output_dir}")
    for dir_path in [general_input_dir, general_output_dir]:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

    # Step 1: Copy buggy folder contents
    print(f"[INFO] Copying buggy files from {buggy_dir} to {general_data_dir}")
    if not os.path.exists(general_data_dir):
        os.makedirs(general_data_dir)

    for item in os.listdir(buggy_dir):
        s = os.path.join(buggy_dir, item)
        d = os.path.join(general_data_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    # Step 2: Copy required .sh files and Dockerfile
    print("[INFO] Copying .sh files and Dockerfile")
    for file in os.listdir(syn_dataset_dir):
        if file.endswith('.sh') and file not in ['downloadBuggy.sh', 'downloadFixed.sh']:
            shutil.copy2(os.path.join(syn_dataset_dir, file), general_data_dir)
        elif file == 'Dockerfile':
            shutil.copy2(os.path.join(syn_dataset_dir, file), general_data_dir)

    # Step 3: Run compile.sh and testRunAll.sh
    current_dir = os.getcwd()
    print(f"[INFO] Changing directory to {general_data_dir} to run scripts")
    os.chdir(general_data_dir)
    try:
        subprocess.run(['bash', 'compile.sh'], check=True)
        subprocess.run(['bash', 'testRunAll.sh'], check=True)
    finally:
        os.chdir(current_dir)
        print(f"[INFO] Changed directory back to {current_dir}")

    # Step 4: Read inputConfig.json
    config_path = os.path.join(manual_inputs_dir, 'inputConfig.json')
    print(f"[INFO] Reading config from {config_path}")
    with open(config_path, 'r') as f:
        config = json.load(f)

    start_line = config['rem_start']
    end_line = config['rem_end']
    fixed_start = config['add_start']
    fixed_end = config['add_end']
    rel_path = config['vul_code_file_rel_path'].lstrip('/')  # ensure it does not start with /

    # Step 5: Write to meta.txt
    print(f"[INFO] Writing metadata to {meta_file_path}")
    os.makedirs(os.path.dirname(meta_file_path), exist_ok=True)
    with open(meta_file_path, 'w') as f:
        f.write(f"{vulnerability_id}\t1\t{rel_path}\t{start_line}\t{end_line}\t{fixed_start}\t{fixed_end}\n")

    print("[INFO] Process completed successfully.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <vulnerability_id>")
        sys.exit(1)
    vulnerability_id = sys.argv[1]
    process_vulnerability(vulnerability_id)
