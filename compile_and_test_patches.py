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
    if ': FAIL' in test_output or ('Failing tests: ' in test_output and 'Failing tests: 0' not in test_output) \
            or ('tests failed out of' in test_output and '0 tests failed out of' not in test_output):
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


def analyze_patch(vul_id, model_name):
    cwd = Path.cwd()
    base_path = cwd / 'llm_outputs' / vul_id
    patch_base = cwd / f'llm_prompts_patch_{model_name}' / vul_id
    result_base = cwd / f'llm_evaluation_results_{model_name}' / vul_id
    project_dir = cwd / 'projects'

    print(f"Analyzing patches for vulnerability: {vul_id}, model: {model_name}")

    # Step 1: Run downloadFixed.sh
    try:
        script_path = base_path / 'downloadFixed.sh'
        print(f"Preparing to run {script_path}")
        os.chmod(script_path, 0o755)
        subprocess.run(["bash", str(script_path)], cwd=cwd)
    except Exception as e:
        print(f"Failed to run downloadFixed.sh: {e}")
        return

    # Step 2: Load project config
    try:
        with open(base_path / 'config.json') as f:
            config = json.load(f)
        print("Loaded config.json")
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return

    rel_path = config['vul_code_file_rel_path']
    source_file_path = project_dir / rel_path

    # Step 3: Iterate over patches
    for expt_dir in patch_base.glob('expt*'):
        print(f"Processing experiment: {expt_dir.name}")
        for patch_file in expt_dir.glob('*.txt'):
            prompt_id = patch_file.stem
            print(f"\nEvaluating patch: {patch_file}")
            results = {}

            try:
                original_cwd = os.getcwd()

                # Replace file content with patch
                patch_text = patch_file.read_text()
                source_file_path.write_text(patch_text)
                print(f"Replaced content of {source_file_path} with patch")

                # Copy compile scripts
                for script_name in ['autoCompile.sh', 'Dockerfile', 'compile.sh']:
                    src_script = base_path / script_name
                    dest_script = project_dir / script_name
                    shutil.copy(src_script, dest_script)
                    os.chmod(dest_script, 0o755)
                    print(f"Copied and chmod'd {script_name} to projects")

                # Run compilation
                os.chdir(project_dir)
                print("Running autoCompile.sh...")

                # Clear the make output file if it exists
                make_output_path = project_dir / 'make_output.txt'
                if make_output_path.exists():
                    make_output_path.write_text("")

                compile_log = run_script('./autoCompile.sh', project_dir)
                os.chdir(original_cwd)

                make_output = read_output_if_exists(project_dir / 'make_output.txt') or compile_log
                make_output.replace("\r\n","\n")
                if 'error:' in make_output:
                    results['Compilation'] = 'Fail'
                    ## print the line in the make_output that contains the error.
                    error_lines = [line for line in make_output.splitlines() if 'error:' in line]
                    print("Compilation failed due to errors in the output:\n {}.".format(error_lines))
                else:
                    results['Compilation'] = 'Success'
                print(f"Compilation result: {results['Compilation']}")

                # Check for test scripts
                test_scripts = list(base_path.glob('*testRun*.sh')) + list(base_path.glob('*TestRun*.sh'))
                test_results = {'TestSingle': 'NA', 'TestAll': 'NA'}

                if results['Compilation'] == 'Success':
                    for test_script in test_scripts:
                        shutil.copy(test_script, project_dir / test_script.name)
                        os.chmod(project_dir / test_script.name, 0o755)
                        print(f"Copied test script: {test_script.name}")

                    test_single = project_dir / 'autoTestRunSingle.sh'
                    test_all = project_dir / 'autoTestRunAll.sh'

                    if test_single.exists():
                        os.chdir(project_dir)
                        print("Running autoTestRunSingle.sh...")
                        test_log = run_script('./autoTestRunSingle.sh', project_dir)
                        os.chdir(original_cwd)
                        test_output = read_output_if_exists(project_dir / 'make_test_output.txt') or test_log
                        test_output.replace("\r\n","\n")
                        if ': FAIL' in test_output or ('Failing tests: ' in test_output and 'Failing tests: 0' not in test_output)\
                                or ('tests failed out of' in test_output and '0 tests failed out of' not in test_output):
                            test_results['TestSingle'] = 'Fail'
                        else:
                            test_results['TestSingle'] = 'Pass'
                    else:
                        test_results['TestSingle'] = 'NA'
                    print(f"TestSingle result: {test_results['TestSingle']}")

                    if test_results['TestSingle'] != 'Fail' and test_all.exists():
                        os.chdir(project_dir)
                        print("Running autoTestRunAll.sh...")
                        test_log = run_script('./autoTestRunAll.sh', project_dir)
                        os.chdir(original_cwd)
                        test_output = read_output_if_exists(project_dir / 'make_test_output.txt') or test_log
                        if ': FAIL' in test_output or 'Failing tests: 0' not in test_output:
                            test_results['TestAll'] = 'Fail'
                        else:
                            test_results['TestAll'] = 'Pass'
                    else:
                        test_results['TestAll'] = 'NA'
                    print(f"TestAll result: {test_results['TestAll']}")

                results.update(test_results)

            except Exception as e:
                print(f"Error during evaluation of {patch_file}: {e}")
                results = {
                    'Compilation': 'Fail',
                    'TestSingle': 'NA',
                    'TestAll': 'NA',
                }

            # Save results
            result_path = result_base / expt_dir.name / f'{prompt_id}.json'
            result_path.parent.mkdir(parents=True, exist_ok=True)

            if result_path.exists():
                with open(result_path) as f:
                    existing = json.load(f)
            else:
                existing = {}

            existing.update(results)

            with open(result_path, 'w') as f:
                json.dump(existing, f, indent=2)
            print(f"Saved results to {result_path}")


'''
Main function, take model name and vulnerability id as system arg.
'''


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
    for script in ['autoCompile.sh', 'Dockerfile', 'compile.sh']:
        shutil.copy(base_path / script, project_dir / script)
        os.chmod(project_dir / script, 0o755)

    os.chdir(project_dir)
    print("Running autoCompile.sh on fixed version...")
    compile_log = run_script('./autoCompile.sh', project_dir)
    make_output = read_output_if_exists(project_dir / 'make_output.txt') or compile_log
    os.chdir(cwd)

    if 'error:' in make_output:
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

    run_test_if_exists('autoTestRunSingle.sh')
    run_test_if_exists('autoTestRunAll.sh')
    print("[+] Tests passed on fixed version")

    # Step 5: Replace only buggy block in the fixed file
    buggy_path = base_path / 'buggy_source_code_file.txt'
    if not buggy_path.exists():
        print(f"[!] Buggy source file not found: {buggy_path}")
        exit(1)

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
    print("Running autoCompile.sh on buggy version...")
    compile_log = run_script('./autoCompile.sh', project_dir)
    make_output = read_output_if_exists(project_dir / 'make_output.txt') or compile_log
    os.chdir(cwd)

    if 'error:' in make_output:
        print("[!] Compilation failed on buggy version")
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

    test_should_fail('autoTestRunSingle.sh')
    test_should_fail('autoTestRunAll.sh')
    print("[+] Validity check passed: Buggy version compiles but fails tests")



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze_patch.py <model_name> <vul_id>")
        sys.exit(1)

    vul_id = sys.argv[2]
    model_name = sys.argv[1]
    check_validity(vul_id)
    analyze_patch(vul_id, model_name)