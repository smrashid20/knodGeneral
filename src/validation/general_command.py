import os
import shutil
import subprocess
import time


defects4j_path = "defects4j"
general_data_path = "/home/KNOD/general_data/"

def extract_project_info(directory_path):
    last_folder = os.path.basename(os.path.normpath(directory_path))
    parts = last_folder.split("_")

    if len(parts) == 2:
        project_name, project_id = parts
        return project_name, project_id
    else:
        return "project", "1"

def copy_folder(source_folder, destination_dir):
    if not os.path.exists(source_folder):
        return

    folder_name = os.path.basename(os.path.normpath(source_folder))
    destination_path = os.path.join(destination_dir, folder_name)

    try:
        shutil.copytree(source_folder, str(destination_path))
        print(f"Successfully copied '{source_folder}' to '{destination_path}'")
    except FileExistsError:
        print(f"Error: Destination folder '{destination_path}' already exists.")
    except Exception as e:
        print(f"Error while copying: {e}")


def clean_tmp_folder(tmp_dir):
    if os.path.isdir(tmp_dir):
        for files in os.listdir(tmp_dir):
            file_p = os.path.join(tmp_dir, files)
            try:
                if os.path.isfile(file_p):
                    os.unlink(file_p)
                elif os.path.isdir(file_p):
                    shutil.rmtree(file_p)
            except Exception as e:
                print(e)
    else:
        os.makedirs(tmp_dir)


def checkout_general_project(project, bug_id, tmp_dir):
    project_name = project + "_" + bug_id
    copy_folder(os.path.join(general_data_path, project_name), tmp_dir)


def compile_fix(project_dir):
    if not os.path.exists(os.path.join(project_dir, "autoCompile.sh")):
        print(f"Error: 'autoCompile.sh' not found in {project_dir}.")
        return False

    if_success = False
    working_dir = os.getcwd()
    os.chdir(project_dir)
    build_log = subprocess.run(["bash" , "autoCompile.sh"], text=True, capture_output=True, check=True).stdout
    if " error:" not in build_log:
        if_success = True
    os.chdir(working_dir)
    return if_success


def command_with_timeout(cmd, timeout=300):
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    t_beginning = time.time()
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            return 'TIMEOUT', 'TIMEOUT'
        time.sleep(1)
    out, err = p.communicate()
    return out, err


def general_test_suite(project_dir, timeout=300):
    num_passed = 0
    num_failed = 0

    if not os.path.exists(os.path.join(project_dir, "autoTestRunAll.sh")):
        print(f"Error: 'autoTestRunAll.sh' not found in {project_dir}.")
        return False

    working_dir = os.getcwd()
    os.chdir(project_dir)
    build_log = subprocess.run(["bash", "autoTestRunAll.sh"], text=True, capture_output=True, check=True).stdout

    num_fail_lines = 0
    num_pass_lines = 0

    for line in (build_log.split('\n')):

        if " FAIL " in line or ":FAIL " in line:
            num_fail_lines += 1
        if " PASS " in line or ":PASS " in line:
            num_pass_lines += 1

        if "Failing tests:" in line:
            num_failed = int(line.split(":")[-1].strip())
        if "Passing tests:" in line:
            num_passed = int(line.split(":")[-1].strip())

    if num_failed == 0 and num_passed == 0:
        num_failed = num_fail_lines

    if_passed = False
    if num_failed == 0:
        if_passed = True
    os.chdir(working_dir)

    if if_passed:
        return 'plausible', num_failed
    else:
        return 'wrong', num_failed


