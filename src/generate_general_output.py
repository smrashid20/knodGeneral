import json
import sys
import os

SRC_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]

sys.path.append(SRC_DIR + '/tester/')
sys.path.append(SRC_DIR + '/validation/')

from generator import generate_knod, read_general_meta
from general_rerank import rerank_patches_by_rank
from general_validate import validate_general


def generate_general_ast_patches(input_dir, output_dir, model_file):
    meta = read_general_meta(input_dir + 'meta_localize.txt')
    identifier_file = input_dir + 'identifiers.json'
    class_name_list = [filename.split('/')[-1][:-5] for (bug, filename) in meta]

    input_file = input_dir + 'input_general_ast.json'
    output_file = output_dir + 'general.txt'

    if not os.path.exists(input_file):
        print(f"[WARN] Input file not found: {input_file}")
        return

    if os.path.getsize(input_file) == 0:
        print(f"[INFO] Skipping general AST generation: file is empty ({input_file})")
        return

    with open(input_file, 'r') as f:
        input_data = json.load(f)

    if not input_data:
        print(f"[INFO] Skipping general AST generation: no content in JSON ({input_file})")
        return

    print("[INFO] Generating general AST patches...")
    generate_knod(model_file, input_file, identifier_file, class_name_list, devices, beam_size, output_file)



def generate_insert_ast_patches(input_dir, output_dir, model_file):
    meta = read_general_meta(input_dir + 'meta_localize.txt')
    identifier_file = input_dir + 'identifiers.json'
    class_name_list = [filename.split('/')[-1][:-5] for (bug, filename) in meta]

    input_file = input_dir + 'input_insert_ast.json'
    output_file = output_dir + 'insert.txt'

    if not os.path.exists(input_file):
        print(f"[WARN] Input file not found: {input_file}")
        return

    if os.path.getsize(input_file) == 0:
        print(f"[INFO] Skipping insert AST generation: file is empty ({input_file})")
        return

    with open(input_file, 'r') as f:
        input_data = json.load(f)

    if not input_data:
        print(f"[INFO] Skipping insert AST generation: no content in JSON ({input_file})")
        return

    print("[INFO] Generating insert AST patches...")
    generate_knod(model_file, input_file, identifier_file, class_name_list, devices, beam_size, output_file)



def rerank_ast_patches(meta_file, hypo_file_list, fix_type_list, output_file, dump=True):
    # Filter out non-existent or empty hypothesis files
    refined_hypo_file_list = []
    refined_fix_type_list = []

    for hypo_file, fix_type in zip(hypo_file_list, fix_type_list):
        if not os.path.exists(hypo_file):
            print(f"[WARN] Skipping missing hypo file: {hypo_file}")
            continue
        if os.path.getsize(hypo_file) == 0:
            print(f"[INFO] Skipping empty hypo file: {hypo_file}")
            continue
        refined_hypo_file_list.append(hypo_file)
        refined_fix_type_list.append(fix_type)

    if not refined_hypo_file_list:
        print("[ERROR] No valid hypo files found. Aborting reranking.")
        return

    # Step 2: rerank the AST of patches
    reranked = rerank_patches_by_rank(
        meta_file,
        refined_hypo_file_list,
        refined_fix_type_list,
        dump=dump,
        output_file=output_file
    )



def validate_ast_patches(reranked_file, meta_file, identifiers_file, output_file, tmp_dir='/tmp/'):
    # step 3: convert AST of patches to source code patches and run test cases, will take a long time
    validate_general(
        hypo_path=reranked_file,
        meta_path=meta_file,
        identifiers_path=identifiers_file,
        output_path=output_file,
        tmp_dir=tmp_dir, progress_range=None
    )


if __name__ == '__main__':
    devices = [0, 0]  # require two devices, but could be the same one
    beam_size = 200

    model_general, model_insert = sys.argv[1], sys.argv[2]

    generate_general_ast_patches(
        SRC_DIR + '../data/general_input/',
        SRC_DIR + '../data/general_output/',
        model_general
    )
    generate_insert_ast_patches(
        SRC_DIR + '../data/general_input/',
        SRC_DIR + '../data/general_output/',
        model_insert
    )

    rerank_ast_patches(
        SRC_DIR + '../data/general_input/meta_localize.txt',
        [SRC_DIR + '../data/general_output/general.txt', SRC_DIR + '../data/general_output/insert.txt'],
        ['general', 'insert'],
        SRC_DIR + '../data/general_output/reranked.json', True
    )
    validate_ast_patches(
        SRC_DIR + '../data/general_output/reranked.json',
        SRC_DIR + '../data/general_input/meta_localize.txt',
        SRC_DIR + '../data/general_input/identifiers.json',
        SRC_DIR + '../data/general_output/validation.json'
    )
