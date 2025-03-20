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


def build_and_run_docker(working_repo_dir, project_name, project_id, task):
    # Ensure the directory exists
    if not os.path.exists(working_repo_dir):
        raise FileNotFoundError(f"Directory '{working_repo_dir}' does not exist.")

    dockerfile_path = os.path.join(working_repo_dir, "Dockerfile")

    # Ensure the Dockerfile exists
    if not os.path.exists(dockerfile_path):
        raise FileNotFoundError(f"Dockerfile not found in '{working_repo_dir}'.")

    # Read and modify the Dockerfile
    dockerfile_content = ""
    with open(dockerfile_path, "r") as file:
        dockerfile_content = file.read()

    # Replace placeholders with the task string
    dockerfile_content = dockerfile_content.replace("autoCompile", task)
    dockerfile_content = dockerfile_content.replace("autoTestRunAll", task)
    dockerfile_content = dockerfile_content.replace("autoTestRunSingle", task)

    # Write the modified Dockerfile back
    with open(dockerfile_path, "w") as file:
        file.write(dockerfile_content)

    # Define the Docker image name
    image_name = f"{project_name}_{project_id}".lower()

    # Step 1: Build the Docker image
    build_cmd = ["docker", "build", "-t", image_name, "."]
    print(f"Building Docker image: {image_name}")
    build_process = subprocess.run(build_cmd, cwd=working_repo_dir, capture_output=True, text=True)
    if build_process.returncode != 0:
        raise RuntimeError(f"Docker build failed: {build_process.stderr}")
    print("Docker image built successfully.")
    # Step 2: Run the Docker container
    run_cmd = ["docker", "run", "--rm", image_name]
    print("Running Docker container...")
    run_process = subprocess.run(run_cmd, cwd=working_repo_dir, capture_output=True, text=True)

    if run_process.returncode != 0:
        raise RuntimeError(f"Docker container execution failed: {run_process.stderr}")
    print("Docker container executed successfully.")
    return run_process.stdout


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
    if_success = False
    project_name, project_id = extract_project_info(project_dir)
    working_dir = os.getcwd()
    os.chdir(project_dir)
    build_log = build_and_run_docker(project_dir, project_name, project_id, "autoCompile")
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

    working_dir = os.getcwd()
    os.chdir(project_dir)
    project_name, project_id = extract_project_info(project_dir)

    build_log = build_and_run_docker(project_dir, project_name, project_id, "autoTestRunAll")

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


