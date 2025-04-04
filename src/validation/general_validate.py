import codecs
import json
import os
import pprint
import shutil
import sys
import time

import general_command
from reconstruct import reconstruct_ctx_wrap_ast, combine_super_methods, reconstruct_wrap_ast
from reconstruct import reconstruct_patched_ctx_wrap_ast, semantic_reconstruct, remove_patch_wrap_ast, reconstruct_ast

VALIDATION_DIR = os.path.abspath(__file__)
VALIDATION_DIR = VALIDATION_DIR[: VALIDATION_DIR.rfind('/') + 1]


def read_rem(rem_path):
    fp = codecs.open(rem_path, 'r', 'utf-8')
    rem = []
    for line in fp.readlines():
        if line.strip() == '':
            rem.append([None, None, None, None, None])
        else:
            loc, index, rem_line = line.split('\t')
            start, end = loc.split('-')
            start_row, start_col = start.split(',')
            end_row, end_col = end.split(',')
            start_row, start_col = int(start_row), int(start_col)
            end_row, end_col = int(end_row), int(end_col)
            rem.append([
                start_row, start_col, end_row, end_col, rem_line.strip()
            ])
    fp.close()
    return rem


def read_meta(meta_path):
    fp = codecs.open(meta_path, 'r', 'utf-8')
    meta = []
    for line in fp.readlines():
        if len(line.strip().split()) == 8:
            proj, bug_id, path, rem_start, rem_end, add_start, add_end, tag = line.strip().split()
            meta.append([proj, bug_id, path, rem_start, rem_end, tag])
        elif len(line.strip().split()) == 6:
            proj, bug_id, path, rem_start, rem_end, tag = line.strip().split()
            meta.append([proj, bug_id, path, rem_start, rem_end, tag])
        elif len(line.strip().split()) == 5:
            proj, bug_id, path, line, index = line.strip().split()
            meta.append([proj, bug_id, path, line, str(int(line) + 1), 'general'])
        elif len(line.strip().split()) == 4:
            proj, bug_id, path, loc = line.strip().split()
            if ',' in loc:
                rem_start, rem_len = loc.split(',')
                rem_end = str(int(rem_start) + int(rem_len))
            else:
                rem_start = loc
                rem_end = str(int(rem_start) + 1)
            meta.append([proj, bug_id, path, rem_start, rem_end, 'general'])
    fp.close()
    return meta


def insert_fix_general(file_path, start_row, start_col, end_row, end_col, patch, project_dir, fix_type='general',
                         key=None):
    file_path = os.path.join(project_dir, file_path)
    shutil.copyfile(file_path, file_path + '.bak')

    with open(file_path, 'r') as file:
        data = file.readlines()

    if fix_type == 'general':
        with open(file_path, 'w') as file:
            for i in range(start_row - 1):
                file.write(data[i])
            file.write(data[start_row - 1][: start_col - 1] + '\n')
            file.write("//start of generated patch\n")
            file.write(patch)
            if not patch.endswith('\n'):
                file.write('\n')
            file.write("//end of generated patch\n")
            file.write(data[end_row - 1][end_col:])
            for i in range(end_row, len(data)):
                file.write(data[i])
    else:
        with open(file_path, 'w') as file:
            for i in range(start_row - 1):
                file.write(data[i])
            file.write("//start of generated patch\n")
            file.write(patch)
            if not patch.endswith('\n'):
                file.write('\n')
            file.write("//end of generated patch\n")
            file.write(data[end_row - 1])
            for i in range(end_row, len(data)):
                file.write(data[i])

    return file_path + '.bak'



# cnt, right = 0, 0

def validate_general(hypo_path, meta_path, identifiers_path, output_path, tmp_dir, progress_range=None):
    # global cnt, right
    identifiers_dict = json.load(open(identifiers_path, 'r'))
    hypo = json.load(open(hypo_path, 'r'))

    cnt, right = 0, 0

    if not os.path.exists(tmp_dir):
        general_command.command_with_timeout(['mkdir', tmp_dir])

    meta = read_meta(meta_path)
    bugs_to_validate = list(hypo.keys())
    rem_general = read_rem(VALIDATION_DIR + '../../data/general_input/rem_general_localize.txt')
    rem_insert = read_rem(VALIDATION_DIR + '../../data/general_input/rem_insert_localize.txt')
    general_general = json.load(open(VALIDATION_DIR + '../../data/general_input/input_general_ast.json', 'r'))
    general_general = {data['id']: data for data in general_general}
    general_insert = json.load(open(VALIDATION_DIR + '../../data/general_input/input_insert_ast.json', 'r'))
    general_insert = {data['id']: data for data in general_insert}

    validated_result = {}
    test_cases_num = []
    for line_num in bugs_to_validate:
        if progress_range is not None and (cnt < progress_range[0] or cnt >= progress_range[1]):
            cnt += 1
            continue

        cnt += 1
        proj, bug_id, file_path, rem_start, rem_end, fix_type = meta[int(line_num) - 1]

        if proj + '_' + bug_id + '_/' + file_path in validated_result:
            continue

        start_row_g, start_col_g, end_row_g, end_col_g, rem_line_g = rem_general[int(line_num) - 1]
        start_row_i, start_col_i, end_row_i, end_col_i, rem_line_i = rem_insert[int(line_num) - 1]

        print(right, '/', cnt, proj, bug_id)

        general_command.clean_tmp_folder(tmp_dir)
        general_command.checkout_general_project(proj, bug_id, tmp_dir)

        project_dir = os.path.join(tmp_dir, proj + '_' + bug_id)
        general_command.compile_fix(project_dir)

        start_time = time.time()
        if_passed, num_failed = general_command.general_test_suite(project_dir)
        standard_time = time.time() - start_time

        init_fail_num = num_failed
        print(init_fail_num, str(standard_time) + 's')

        if int(line_num) in general_general:
            data = general_general[int(line_num)]
            src2abs_g = {k: v for k, v in data['mappings'].items() if '<UNK>' not in v}
            abs2src_g = {v: k for k, v in data['mappings'].items() if '<UNK>' not in v}
            ctx_ast_nodes_g, node_num_before_g, sibling_num_before_g = reconstruct_ctx_wrap_ast(
                data['nodes'], data['edges'], data['rem_roots'][0], abs2src_g
            )
        else:
            src2abs_g, abs2src_g = None, None
            ctx_ast_nodes_g, node_num_before_g, sibling_num_before_g = None, None, None
        if int(line_num) in general_insert:
            data = general_insert[int(line_num)]
            src2abs_i = {k: v for k, v in data['mappings'].items() if '<UNK>' not in v}
            abs2src_i = {v: k for k, v in data['mappings'].items() if '<UNK>' not in v}
            ctx_ast_nodes_i, node_num_before_i, sibling_num_before_i = reconstruct_ctx_wrap_ast(
                data['nodes'], data['edges'], data['rem_roots'][0], abs2src_i
            )
        else:
            src2abs_i, abs2src_i = None, None
            ctx_ast_nodes_i, node_num_before_i, sibling_num_before_i = None, None, None

        general_command.clean_tmp_folder(tmp_dir)
        general_command.checkout_general_project(proj, bug_id, tmp_dir)

        if str(line_num) not in identifiers_dict:
            identifiers = {}
        else:
            identifiers = identifiers_dict[str(line_num)]
        print('identifiers num:', len(identifiers))

        key = proj + '_' + bug_id + '_/' + file_path
        validated_result[key] = {'id': int(line_num), 'patches': []}

        current_is_plausible = False
        current_is_correct = False
        failed_num = None
        start_this_bug = time.time()

        idx = 1

        patch_output_dir = os.path.join('./patch', proj, bug_id)
        if os.path.exists(patch_output_dir):
            shutil.rmtree(patch_output_dir)
        os.makedirs(patch_output_dir, exist_ok=True)

        for rank, patch_ast in enumerate(hypo[line_num]['patches']):
            if time.time() - start_this_bug > 3600 * 5:
                break
            if len(validated_result[key]['patches']) > 2000:
                break
            if current_is_correct:
                break

            patched_file = os.path.join(tmp_dir, proj + '_' + bug_id, file_path)
            print("[DEBUG]: Line 192 patched_file:", patched_file)

            try:
                patch_fix_type = patch_ast['fix_type']
                print(f"[DEBUG] Patch fix type detected: {patch_fix_type}")

                if patch_fix_type == 'general':
                    print("[DEBUG] Using general fix context")
                    abs2src, src2abs = abs2src_g, src2abs_g
                    ctx_ast_nodes, node_num_before, sibling_num_before = ctx_ast_nodes_g, node_num_before_g, sibling_num_before_g
                    start_row, start_col, end_row, end_col = start_row_g, start_col_g, end_row_g, end_col_g
                else:
                    print("[DEBUG] Using insert fix context")
                    abs2src, src2abs = abs2src_i, src2abs_i
                    ctx_ast_nodes, node_num_before, sibling_num_before = ctx_ast_nodes_i, node_num_before_i, sibling_num_before_i
                    start_row, start_col, end_row, end_col = start_row_i, start_col_i, end_row_i, end_col_i

                if abs2src is None or ctx_ast_nodes is None:
                    print("[DEBUG] Skipping patch — missing AST or mappings")
                    continue

                if patch_ast['n'].strip() == '<EOS>':
                    print("[DEBUG] Patch is <EOS> — interpreted as empty patch")
                    code_patches = ['']
                elif '_<UNK>' in patch_ast['n']:
                    print("[DEBUG] Patch contains <UNK> — entering semantic reconstruction")
                    if identifiers is None:
                        print("[DEBUG] Skipping due to missing identifiers")
                        continue
                    fathers, edges, nodes = patch_ast['f'].split(), patch_ast['e'].split(), patch_ast['n'].split()
                    patch_ast_roots, patch_ast_nodes = reconstruct_wrap_ast(fathers, edges, nodes, abs2src)
                    ast_nodes = reconstruct_patched_ctx_wrap_ast(ctx_ast_nodes, node_num_before, sibling_num_before,
                                                                patch_ast_roots, patch_ast_nodes)
                    reconstructed_nodes = semantic_reconstruct(patch_ast_nodes, ast_nodes, file_path, src2abs, abs2src, identifiers)
                    print(f"[DEBUG] Semantic reconstruction returned {len(reconstructed_nodes) if reconstructed_nodes else 0} candidates")
                    if patch_fix_type == 'general':
                        ctx_ast_nodes_g = remove_patch_wrap_ast(ast_nodes, node_num_before, sibling_num_before,
                                                                patch_ast_roots, patch_ast_nodes)
                    else:
                        ctx_ast_nodes_i = remove_patch_wrap_ast(ast_nodes, node_num_before, sibling_num_before,
                                                                patch_ast_roots, patch_ast_nodes)
                    if not reconstructed_nodes:
                        print("[DEBUG] Reconstruction failed or returned empty list, skipping patch")
                        continue
                    reconstruct_max = 10
                    code_patches = [
                        reconstruct_ast(fathers, edges, node, abs2src)
                        for node in reconstructed_nodes[:reconstruct_max]
                    ]
                    print(f"[DEBUG] Generated {len(code_patches)} patch candidates after reconstruction")
                else:
                    print("[DEBUG] No <UNK> — reconstructing AST directly")
                    code_patches = [reconstruct_ast(
                        patch_ast['f'].split(),
                        patch_ast['e'].split(),
                        patch_ast['n'].split(),
                        abs2src
                    )]

                score = patch_ast['score']
                for patch in code_patches:
                    if current_is_correct:
                        print("[DEBUG] Correct patch already found — skipping remaining patches")
                        break

                    s_time = time.time()
                    patch = patch.strip()
                    print(f"[DEBUG] Applying patch idx {idx}, score: {score}")

                    patched_file = insert_fix_general(file_path, start_row, start_col, end_row, end_col,
                                                    patch, project_dir, fix_type=patch_fix_type, key=f"{proj}_{bug_id}")
                    print(f"[DEBUG] Patch inserted into file: {patched_file}")

                    compile = general_command.compile_fix(project_dir)
                    print(f"[DEBUG] Compilation result: {'Success' if compile else 'Fail'}")

                    correctness = 'uncompilable'
                    if compile:
                        print("[DEBUG] Running test suite...")
                        correctness, num_failed = general_command.general_test_suite(project_dir)
                        print(f"[DEBUG] Test suite completed. Result: {correctness}, Failed tests: {num_failed}")
                        if correctness == 'plausible':
                            right += 1
                            print(f"Correct patch found at rank {rank}, idx {idx} — {patch} (time: {int(time.time() - s_time)}s)")
                            current_is_correct = True
                        elif correctness == 'wrong':
                            print(f"Patch compiled but failed tests at rank {rank}, idx {idx}")
                    else:
                        print(f"Patch failed to compile at rank {rank}, idx {idx}")

                    validated_result[key]['patches'].append({
                        'patch': patch, 'score': score, 'correctness': correctness, 'fix_type': patch_fix_type
                    })

                    # Save compilation and test results
                    compile_status = "Success" if compile else "Fail"
                    test_single = "NA"
                    test_all = "Pass" if correctness == "plausible" else ("Fail" if correctness == "wrong" else "NA")

                    result_json = {
                        "Compilation": compile_status,
                        "TestSingle": test_single,
                        "TestAll": test_all
                    }

                    if os.path.exists(patched_file) and (idx < 100 or compile):
                        patch_txt_path = os.path.join(patch_output_dir, f'patch_{idx}.txt')
                        with open(patched_file.replace('.bak', ''), 'r') as pf_src, open(patch_txt_path, 'w') as pf_dst:
                            pf_dst.write(pf_src.read())
                        print(f"[DEBUG] Wrote patch source to {patch_txt_path}")

                        patch_json_path = os.path.join(patch_output_dir, f'patch_{idx}.json')
                        with open(patch_json_path, 'w') as pf_json:
                            json.dump(result_json, pf_json, indent=2)
                        print(f"[DEBUG] Wrote patch result to {patch_json_path}")

                    idx += 1

                    if os.path.exists(patched_file):
                        shutil.copyfile(patched_file, patched_file.replace('.bak', ''))
                        print(f"[DEBUG] Restored original file from backup")


            except Exception as e:
                print("###############ERR###############")
                print(e)
                if os.path.exists(patched_file + '.bak'):
                    shutil.copyfile(patched_file + '.bak', patched_file)

                if int(line_num) in general_general:
                    data = general_general[int(line_num)]
                    src2abs_g = {k: v for k, v in data['mappings'].items() if '<UNK>' not in v}
                    abs2src_g = {v: k for k, v in data['mappings'].items() if '<UNK>' not in v}
                    ctx_ast_nodes_g, node_num_before_g, sibling_num_before_g = reconstruct_ctx_wrap_ast(
                        data['nodes'], data['edges'], data['rem_roots'][0], abs2src_g
                    )
                else:
                    src2abs_g, abs2src_g = None, None
                    ctx_ast_nodes_g, node_num_before_g, sibling_num_before_g = None, None, None
                if int(line_num) in general_insert:
                    data = general_insert[int(line_num)]
                    src2abs_i = {k: v for k, v in data['mappings'].items() if '<UNK>' not in v}
                    abs2src_i = {v: k for k, v in data['mappings'].items() if '<UNK>' not in v}
                    ctx_ast_nodes_i, node_num_before_i, sibling_num_before_i = reconstruct_ctx_wrap_ast(
                        data['nodes'], data['edges'], data['rem_roots'][0], abs2src_i
                    )
                else:
                    src2abs_i, abs2src_i = None, None
                    ctx_ast_nodes_i, node_num_before_i, sibling_num_before_i = None, None, None
                # write after finish validating every bug, to avoid wasting time


            json.dump(validated_result, open(output_path, 'w'), indent=2)
            # write the last time after validating all
            json.dump(validated_result, open(output_path, 'w'), indent=2)


if __name__ == '__main__':
    batch_id = int(sys.argv[1])

    validate_general(
        hypo_path=VALIDATION_DIR + '../../data/general_output/reranked.json',
        meta_path=VALIDATION_DIR + '../../data/general_input/meta_localize.txt',
        identifiers_path=VALIDATION_DIR + '../../data/general_input/identifiers.json',
        output_path=VALIDATION_DIR + '../../data/general_output/validation_' + str(batch_id) + '.json',
        tmp_dir='/tmp/general_' + str(batch_id) + '/', progress_range=[20 * (batch_id - 1), 20 * batch_id]
    )
