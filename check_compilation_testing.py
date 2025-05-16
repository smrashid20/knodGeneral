import os
import json
import shutil
from pathlib import Path
import sys
import subprocess

def analyze_test_log(test_output, vul_id):
    """
    Analyze the test log to determine if the tests passed or failed.
    """
    if ((': FAIL' in test_output) or ('ERROR' in test_output) or
            ('Failing tests: ' in test_output and 'Failing tests: 0' not in test_output) \
            or ('tests failed out of' in test_output and '0 tests failed out of' not in test_output)
            or ('R:dlzexternal:FAIL'in test_output)
            or('Error ' in test_output)):
        return 'Fail'

    return 'Pass'


def run_script(script_path, cwd):
    try:
        print(f"Running script: {script_path} in {cwd}")
        os.chmod(script_path, 0o755)
        result = subprocess.run([str(script_path)], cwd=cwd, capture_output=True, text=True, shell=True)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return str(e)

def read_output_if_exists(path):
    if path.exists():
        print(f"Reading output from {path}")
        return path.read_text()
    return ""



def check_validity(vul_id):
    cwd = Path.cwd()
    base_path = cwd / 'llm_outputs' / vul_id
    project_dir = cwd / 'projects'

    print(f"\n[+] Running validity checks for vulnerability: {vul_id}")

    # Step 1: Download project
    try:
        script_path = base_path / 'downloadFixed.sh'
        print(f"Running {script_path}")
        os.chmod(script_path, 0o755)
        subprocess.run(["bash", str(script_path)], cwd=cwd, check=True)
    except Exception as e:
        print(f"[!] Failed to run downloadFixed.sh: {e}")
        exit(1)

    # Step 2: Load project config
    try:
        with open(base_path / 'config.json') as f:
            config = json.load(f)
        print("Loaded config.json")
    except Exception as e:
        print(f"[!] Error loading config.json: {e}")
        exit(1)

    rel_path = config['vul_code_file_rel_path']
    source_file_path = project_dir / rel_path

    # Step 3: Compile original (fixed) project
    for script in ['compile.sh']:
        shutil.copy(base_path / script, project_dir / script)
        os.chmod(project_dir / script, 0o755)

    os.chdir(project_dir)
    print("Running compile.sh on fixed version...")
    compile_log = run_script('./compile.sh', project_dir)
    make_output = read_output_if_exists(project_dir / 'make_output.txt') or compile_log
    os.chdir(cwd)

    if 'error:' in make_output or 'Error :' in make_output:
        print("[!] Compilation failed on fixed version")
        # print(make_output)
        exit(1)
    print("[+] Fixed version compiled successfully")

    # Step 4: Run tests on fixed version
    def run_test_if_exists(test_script_name):
        test_script = project_dir / test_script_name
        if not test_script.exists():
            return 'Pass'
        os.chmod(test_script, 0o755)
        os.chdir(project_dir)
        test_log = run_script(f'./{test_script_name}', project_dir)
        os.chdir(cwd)
        test_output = read_output_if_exists(project_dir / 'make_test_output.txt') or test_log
        if analyze_test_log(test_output, vul_id) == 'Fail':
            print(f"[!] Test failed: {test_script_name}")
            # print(test_output)
            exit(1)
        return 'Pass'

    test_scripts = list(base_path.glob('*testRun*.sh')) + list(base_path.glob('*TestRun*.sh'))
    test_results = {'TestSingle': 'NA', 'TestAll': 'NA'}

    for test_script in test_scripts:
        shutil.copy(test_script, project_dir / test_script.name)
        os.chmod(project_dir / test_script.name, 0o755)
        print(f"Copied test script: {test_script.name}")

    run_test_if_exists('testRunSingle.sh')
    run_test_if_exists('testRunAll.sh')
    print("[+] Tests passed on fixed version")

    # Step 5: Replace only buggy block in the fixed file
    buggy_path = base_path / 'buggy_source_code_file.txt'
    if not buggy_path.exists():
        print(f"[!] Buggy source file not found: {buggy_path}")
        exit(1)

    print("Compilation try using block")

    buggy_lines = buggy_path.read_text().splitlines()
    full_source_lines = source_file_path.read_text().splitlines()

    block_start = config['vul_code_block_fixed_start_line'] - 1
    block_end = config['vul_code_block_fixed_end_line']
    buggy_block_start = config['vul_code_block_start_line'] - 1
    buggy_block_end = config['vul_code_block_end_line']

    buggy_block = buggy_lines[buggy_block_start:buggy_block_end]
    new_source_lines = full_source_lines[:block_start] + buggy_block + full_source_lines[block_end:]

    source_file_path.write_text('\n'.join(new_source_lines) + '\n')
    print("[+] Replaced fixed block with buggy block in source file")

    # Step 6: Compile buggy version
    os.chdir(project_dir)
    print("Running compile.sh on buggy version...")
    compile_log = run_script('./compile.sh', project_dir)
    make_output = read_output_if_exists(project_dir / 'make_output.txt') or compile_log
    os.chdir(cwd)

    if 'error:' in make_output or 'Error ' in make_output:
        print("[-] Compilation failed on buggy version with block change")

        buggy_lines = buggy_path.read_text().splitlines()

        func_start = config['vul_code_func_fixed_start_line'] - 1
        func_end = config['vul_code_func_fixed_end_line']
        buggy_func_start = config['vul_code_func_start_line'] - 1
        buggy_func_end = config['vul_code_func_end_line']

        buggy_func = buggy_lines[buggy_func_start:buggy_func_end]
        new_source_lines = full_source_lines[:func_start] + buggy_func + full_source_lines[func_end:]

        source_file_path.write_text('\n'.join(new_source_lines) + '\n')
        print("[+] Replaced fixed function with buggy in source file")

        # Step 6: Compile buggy version
        os.chdir(project_dir)
        print("Running compile.sh on buggy version...")
        compile_log = run_script('./compile.sh', project_dir)
        make_output = read_output_if_exists(project_dir / 'make_output.txt') or compile_log
        os.chdir(cwd)

        if 'error:' in make_output or 'Error ' in make_output:
            print("[-] Compilation failed on buggy version with function change")
            # print(make_output)
            exit(1)

    print("[+] Buggy version compiled successfully")

    # Step 7: Run tests on buggy version (should fail)
    def test_should_fail(test_script_name):
        test_script = project_dir / test_script_name
        if not test_script.exists():
            return 'Pass'
        os.chmod(test_script, 0o755)
        os.chdir(project_dir)
        test_log = run_script(f'./{test_script_name}', project_dir)
        os.chdir(cwd)
        test_output = read_output_if_exists(project_dir / 'make_test_output.txt') or test_log
        if analyze_test_log(test_output, vul_id) != 'Fail':
            print(f"[!] Buggy version unexpectedly passed: {test_script_name}")
            # print(test_output)
            exit(1)
        return 'Fail'

    test_should_fail('testRunSingle.sh')
    test_should_fail('testRunAll.sh')
    print("[+] Validity check passed: Buggy version compiles but fails tests")



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_patch.py <vul_id>")
        sys.exit(1)

    vul_id = sys.argv[1]
    check_validity(vul_id)