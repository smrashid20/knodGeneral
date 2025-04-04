import os
import codecs
import subprocess
import json
import re
import sys

SRC_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
JAVA_DIR = SRC_DIR + '../javaparser/'

sys.path.append(SRC_DIR + 'parser/')
sys.path.append(SRC_DIR + '../')
sys.path.append(SRC_DIR + 'validation/')

from ast_parser import dfs
import general_command
from reconstruct import extract_identifiers, combine_super_methods
from general_validate import read_meta
import javalang.tokenizer
import javalang.parse
from javalang.ast import Node
from javalang.tree import BlockStatement, SwitchStatementCase


import subprocess

import subprocess

def command(cmd):
    print("Executing command:", ' '.join(cmd))
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output_log = ""
    error_log = ""

    while True:
        stdout_line = process.stdout.readline()
        stderr_line = process.stderr.readline()

        if stdout_line:
            print(stdout_line, end='')
            output_log += stdout_line

        if stderr_line:
            print(f"[stderr] {stderr_line}", end='')
            error_log += stderr_line

        if stdout_line == '' and stderr_line == '' and process.poll() is not None:
            break

    return output_log, error_log



def prepare_localize_data(data_dir):
    def insert_pad_statement(rem_file, insert_loc):
        fp = codecs.open(rem_file, 'r', 'utf-8')
        rems = fp.readlines()
        fp.close()
        wp = codecs.open(rem_file, 'w', 'utf-8')
        for line in rems[: insert_loc]:
            wp.write(line)
        wp.write('PAD_STATEMENT;\n')
        for line in rems[insert_loc:]:
            wp.write(line)
        wp.close()

    tmp_dir = '/tmp/'

    meta_fp = codecs.open(data_dir + '/meta.txt', 'r', 'utf-8')
    rem_general_wp = codecs.open(data_dir + '/rem_general_localize.txt', 'w', 'utf-8')
    ctx_general_wp = codecs.open(data_dir + '/ctx_general_localize.txt', 'w', 'utf-8')
    rem_insert_wp = codecs.open(data_dir + '/rem_insert_localize.txt', 'w', 'utf-8')
    # add_insert_wp = codecs.open(data_dir + '/add_insert_localize.txt', 'w', 'utf-8')
    ctx_insert_wp = codecs.open(data_dir + '/ctx_insert_localize.txt', 'w', 'utf-8')
    meta_wp = codecs.open(data_dir + '/meta_localize.txt', 'w', 'utf-8')

    discard_cnt, success_cnt = 0, 0
    for line in meta_fp.readlines():
        proj, bug_id, path, rem_start, rem_end, add_start, add_end = line.strip().split()
        print('\n' + proj, bug_id)

        try:
            if os.path.exists(tmp_dir + proj + "_" + bug_id):
                command(['rm', '-rf', tmp_dir + proj + "_" + bug_id])
            general_command.checkout_general_project(proj, bug_id, tmp_dir)
            print("TMP DIR: ", tmp_dir)
            # Strip leading slashes from path to avoid os.path.join resets
            clean_path = path.lstrip('/')

            # Join paths safely
            full_path = os.path.join(tmp_dir, f"{proj}_{bug_id}", clean_path)

            print("PATH:", full_path)
            assert os.path.exists(full_path), f"File does not exist: {full_path}"

            bugs = [{'rem_loc': (int(rem_start), int(rem_end)), 'add_loc': (int(add_start), int(add_end))}]
            print(bugs)
        except Exception as e:
            print("Failed at line 72")
            discard_cnt += 1
            print(e)
            continue

        general_rem, general_ctx = '', ''
        insert_rem, insert_ctx = '', ''
        meta_line, tag = '', ''
        other = 'fail'

        bug = bugs[0]
        if bug['rem_loc'][0] == bug['rem_loc'][1]:
            tag = 'insert'
            # bug['rem_loc'] = (bug['rem_loc'][0] + 1, bug['rem_loc'][0] + 1)
            print(len(codecs.open(os.path.join(tmp_dir, proj + "_" + bug_id, path), 'r', 'utf-8').readlines()))
            if codecs.open(os.path.join(tmp_dir, proj + "_" + bug_id, path), 'r', 'utf-8').readlines()[bug['rem_loc'][0] - 1].strip():
                curr_path = os.getcwd()
                os.chdir(JAVA_DIR)

                command(['mvn', 'clean', 'compile'])
                print("executing 109")
                args = f"defects4j {tmp_dir} {os.path.join(tmp_dir, f'{proj}_{bug_id}', path)} {bug['rem_loc'][0]} {bug['rem_loc'][1] + 1}"

                cmd = [
                    'mvn',
                    'exec:java',
                    '-Dexec.mainClass=jiang719.BuggyASTExtractor',
                    f'-Dexec.args={args}'
                ]

                out, err = command(cmd)

                os.chdir(curr_path)
                try:
                    result = json.load(open(tmp_dir + 'tmp.json', 'r'))
                    rem_range = result['rem_range']
                    rem_index = result['rem_index']
                    rem_code = re.sub('\\s+', ' ', result['rem_code']).strip()
                    rem_context = re.sub('\\s+', ' ', result['rem_context']).strip()
                    if rem_context != '' and rem_code != '' and rem_range != '' and rem_index != '':
                        general_rem = rem_range + '\t' + rem_index + '\t' + rem_code
                        # general_add = ''
                        general_ctx = rem_context + '\t'
                        command(['rm', '-rf', tmp_dir + 'tmp.json', tmp_dir + 'tmp_add.java',
                                 tmp_dir + 'tmp_rem_.java', tmp_dir + 'tmp_add_.java'])
                        other = 'success'
                except Exception as e:
                    print("Failed at line 129")
                    print(out, err)
                    pass

            insert_pad_statement(
                os.path.join(tmp_dir, proj + "_" + bug_id, path), bug['rem_loc'][0] - 1
            )
            curr_path = os.getcwd()
            os.chdir(JAVA_DIR)

            command(['mvn', 'clean', 'compile'])
            print("executing 139")
            args = f"training {tmp_dir} {os.path.join(tmp_dir, f'{proj}_{bug_id}', path)} {bug['rem_loc'][0]} {bug['rem_loc'][1] + 1}"

            cmd = [
                'mvn',
                'exec:java',
                '-Dexec.mainClass=jiang719.BuggyASTExtractor',
                f'-Dexec.args={args}'
            ]

            out, err = command(cmd)

            os.chdir(curr_path)
            try:
                result = json.load(open(tmp_dir + 'tmp.json', 'r'))
            except Exception as e:
                print("Failed at line 148")
                discard_cnt += 1
                print(out, err)
                print('no tmp.json')
                continue
            rem_range = result['rem_range']
            rem_index = result['rem_index']
            rem_code = re.sub('\\s+', ' ', result['rem_code']).strip()
            rem_context = re.sub('\\s+', ' ', result['rem_context']).strip()
            # add_indexs = result['add_index']
            # add_codes = result['add_code']
            # add_context = re.sub('\\s+', ' ', result['add_context']).strip()

            if rem_context == '' or rem_code == '' or rem_range == '' or rem_index == '':
                discard_cnt += 1
                print('empty')
                continue

            insert_rem = rem_range + '\t' + rem_index + '\t' + rem_code
            # add_line = ''
            # for (add_index, add_code) in zip(add_indexs, add_codes):
            #     add_code = re.sub('\\s+', ' ', add_code).strip()
            #     add_line += add_index + '\t' + add_code + '\t'
            # insert_add = ''
            insert_ctx = rem_context  # + '\t' + add_context
            meta_line = proj + '\t' + bug_id + '\t' + path + '\t' + \
                        str(bug['rem_loc'][0]) + '\t' + str(bug['rem_loc'][1] + 1) + '\t' + tag
            # str(bug['add_loc'][0]) + '\t' + str(bug['add_loc'][1]) + '\t' + tag
            command(['rm', '-rf', tmp_dir + 'tmp.json', tmp_dir + 'tmp_add.java',
                     tmp_dir + 'tmp_rem_.java', tmp_dir + 'tmp_add_.java'])
            success_cnt += 1

        else:
            tag = 'general'
            curr_path = os.getcwd()
            os.chdir(JAVA_DIR)

            command(['mvn', 'clean', 'compile'])
            print("executing 185")
            args = f"defects4j {tmp_dir} {os.path.join(tmp_dir, proj + '_' + str(bug_id), path)} {bug['rem_loc'][0]} {bug['rem_loc'][1]}"
            cmd = [
                "mvn",
                "exec:java",
                "-Dexec.mainClass=jiang719.BuggyASTExtractor",
                f"-Dexec.args={args}"
            ]
            out, err = command(cmd)

            os.chdir(curr_path)
            try:
                result = json.load(open(tmp_dir + 'tmp.json', 'r'))
            except Exception as e:
                print("Failed at line 192")
                print(out, err)
                discard_cnt += 1
                print(e)
                continue
            rem_range = result['rem_range']
            rem_index = result['rem_index']
            rem_code = re.sub('\\s+', ' ', result['rem_code']).strip()
            rem_context = re.sub('\\s+', ' ', result['rem_context']).strip()
            # add_indexs = result['add_index']
            # add_codes = result['add_code']
            # add_context = re.sub('\\s+', ' ', result['add_context']).strip()

            if rem_context == '' or rem_code == '' or rem_range == '' or rem_index == '':
                discard_cnt += 1
                continue

            general_rem = rem_range + '\t' + rem_index + '\t' + rem_code
            # add_line = ''
            # for (add_index, add_code) in zip(add_indexs, add_codes):
            #     add_code = re.sub('\\s+', ' ', add_code).strip()
            #     add_line += add_index + '\t' + add_code + '\t'
            # general_add = add_line[:-1]
            general_ctx = rem_context  # + '\t' + add_context
            meta_line = proj + '\t' + bug_id + '\t' + path + '\t' + \
                        str(bug['rem_loc'][0]) + '\t' + str(bug['rem_loc'][1]) + '\t' + tag
            # str(bug['add_loc'][0]) + '\t' + str(bug['add_loc'][1]) + '\t' + tag
            command(['rm', '-rf', tmp_dir + 'tmp.json', tmp_dir + 'tmp_add.java',
                     tmp_dir + 'tmp_rem_.java', tmp_dir + 'tmp_add_.java'])
            success_cnt += 1

            if bugs[0]['rem_loc'][1] - bugs[0]['rem_loc'][0] == 1:
                insert_pad_statement(
                    os.path.join(tmp_dir, proj + "_" + bug_id, path), bug['rem_loc'][0] - 1
                )
                curr_path = os.getcwd()
                os.chdir(JAVA_DIR)

                command(['mvn', 'clean', 'compile'])
                print("executing 231")
                args = f"defects4j {tmp_dir} {os.path.join(tmp_dir, f'{proj}_{bug_id}', path)} {bug['rem_loc'][0]} {bug['rem_loc'][1]}"

                cmd = [
                    'mvn',
                    'exec:java',
                    '-Dexec.mainClass=jiang719.BuggyASTExtractor',
                    f'-Dexec.args={args}'
                ]

                out, err = command(cmd)

                os.chdir(curr_path)
                try:
                    result = json.load(open(tmp_dir + 'tmp.json', 'r'))
                    rem_range = result['rem_range']
                    rem_index = result['rem_index']
                    rem_code = re.sub('\\s+', ' ', result['rem_code']).strip()
                    rem_context = re.sub('\\s+', ' ', result['rem_context']).strip()
                    if rem_context != '' and rem_code != '' and rem_range != '' and rem_index != '':
                        insert_rem = rem_range + '\t' + rem_index + '\t' + rem_code
                        # insert_add = ''
                        insert_ctx = rem_context + '\t'
                        command(['rm', '-rf', tmp_dir + 'tmp.json', tmp_dir + 'tmp_add.java',
                                 tmp_dir + 'tmp_rem_.java', tmp_dir + 'tmp_add_.java'])
                        other = 'success'
                except Exception as e:
                    print("Failed at line 250")
                    print(out, err)
                    pass

        rem_general_wp.write(general_rem + '\n')
        # add_general_wp.write(general_add + '\n')
        ctx_general_wp.write(general_ctx + '\n')
        rem_insert_wp.write(insert_rem + '\n')
        # add_insert_wp.write(insert_add + '\n')
        ctx_insert_wp.write(insert_ctx + '\n')
        meta_wp.write(meta_line + '\n')
        print('succeed', tag, other)
    print(discard_cnt, success_cnt)


def prepare_mapping_data(data_dir):
    curr_path = os.getcwd()
    os.chdir(JAVA_DIR)
    command(['mvn', 'clean', 'compile'])
    ctx_file = os.path.join(data_dir, "ctx_general_localize.txt")
    mapping_file = os.path.join(data_dir, "mapping_general_localize.txt")
    args = f"{ctx_file} {mapping_file}"

    command([
        'mvn',
        'exec:java',
        '-Dexec.mainClass=jiang719.Abstractor',
        f'-Dexec.args={args}'
    ])

    ctx_file = os.path.join(data_dir, "ctx_insert_localize.txt")
    mapping_file = os.path.join(data_dir, "mapping_insert_localize.txt")
    args = f"{ctx_file} {mapping_file}"

    command([
        'mvn',
        'exec:java',
        '-Dexec.mainClass=jiang719.Abstractor',
        f'-Dexec.args={args}'
    ])

    os.chdir(curr_path)


def get_ast_size(node):
    traverse, edges = dfs(node)
    return len(traverse)


def prepare_ast_data(data_dir, target_tag='general'):
    def remove_pad_statement_from_mapping(file_path):
        new_data = []
        data = json.load(open(file_path, 'r'))
        for i in range(len(data)):
            if 'PAD_STATEMENT' not in data[i]['mappings']:
                new_data.append(data[i])
                continue
            non_var = {k: v for k, v in data[i]['mappings'].items() if v[:3] != 'VAR' or 'UNK' in v}
            var = {k: int(v.split('_')[1]) for k, v in data[i]['mappings'].items() if v[:3] == 'VAR' and 'UNK' not in v}
            if 'PAD_STATEMENT' not in var:
                continue
            pad_index = var['PAD_STATEMENT']
            new_var = {}
            for k, v in var.items():
                if k == 'PAD_STATEMENT':
                    continue
                elif v < pad_index:
                    new_var[k] = 'VAR_' + str(v)
                elif v > pad_index:
                    new_var[k] = 'VAR_' + str(v - 1)
            non_var.update(new_var)
            data[i]['mappings'] = non_var
            new_data.append(data[i])
        json.dump(new_data, open(file_path, 'w'))

    rem_fp = codecs.open(data_dir + 'rem_' + target_tag + '_localize.txt', 'r', 'utf-8')
    # add_fp = codecs.open(data_dir + 'add_' + target_tag + '_localize.txt', 'r', 'utf-8')
    ctx_fp = codecs.open(data_dir + 'ctx_' + target_tag + '_localize.txt', 'r', 'utf-8')
    mapping_fp = codecs.open(data_dir + 'mapping_' + target_tag + '_localize.txt', 'r', 'utf-8')
    meta_fp = codecs.open(data_dir + 'meta_localize.txt', 'r', 'utf-8')

    cant_localize = 0
    cnt = 0
    input_ast = []
    for rem, ctx, mappings, meta in zip(rem_fp.readlines(), ctx_fp.readlines(), mapping_fp.readlines(),
                                        meta_fp.readlines()):
        proj, bug_id, path, rem_start, rem_end, tag = meta.strip().split()
        cnt += 1

        rem_ctx = ctx.strip()
        if rem_ctx == '':
            continue

        if tag == target_tag:
            rem = rem.split('\t')
            rem_ctx_split = []
            pre_index = 0
            loc, index, code = rem[0], int(rem[1]), rem[2]
            rem_match = {
                'location': loc,
                'index': index,
                'code': code.strip(),
                'match': None,
                'matched_cnt': 0
            }
            cur_index = [j for j in range(len(rem_ctx)) if rem_ctx.startswith(code.strip(), j)][index]
            rem_ctx_split.append(rem_ctx[pre_index: cur_index])
            pre_index = cur_index + len(code)
            rem_match['code'] = re.sub('\\s+|\\(|\\)|{|}|;|,', '', rem_match['code'])
            rem_ctx_split.append(rem_ctx[pre_index:])

            try:
                tokens = javalang.tokenizer.tokenize(rem_ctx)
                parser = javalang.parser.Parser(tokens)
                rem_ast = parser.parse_member_declaration()
            except Exception as e:
                print("Failed at line 326")
                print(cnt, "parse failed")
                continue
            traverse, rem_edges = dfs(rem_ast)
            nodes, rem_roots = [], []
            for _, node in enumerate(traverse):
                if isinstance(node, Node):
                    node_code = node.to_code()
                    nodes.append(node.__class__.__name__)
                elif type(node) in [list, set]:
                    node_code = ' '.join([s for s in list(node)])
                    nodes.append(node_code.strip())
                else:
                    node_code = str(node)
                    nodes.append(node_code.strip())

                node_code = re.sub('\\s+|\\(|\\)|{|}|;|,', '', node_code)

                is_rem_root = False
                if rem_match['code'] == node_code and \
                        not (isinstance(node, BlockStatement) and len(getattr(node, "statements")) == 1):
                    if rem_match['matched_cnt'] == rem_match['index']:
                        rem_match['match'] = node
                        is_rem_root = True
                    rem_match['matched_cnt'] += 1
                if is_rem_root:
                    rem_roots.append(_)
            rem_nodes = [rem_match['match']] if rem_match['match'] is not None else []
            if len(rem_roots) != 1 or len(rem_nodes) != 1:
                cant_localize += 1
                print(proj, bug_id, cnt, "match rem failed", rem)
                continue

            mapping_dict = {}
            mapping_rem, mapping_add = mappings.split('\t')
            mappings = mapping_rem.split(' <SEP> ')[:-1]

            nodes_set = set(nodes)
            temp = {k: [] for k in ('VAR', 'TYPE', 'METHOD', 'INT', 'STRING', 'FLOAT', 'CHAR')}
            for mapping in mappings:
                name, abstraction = mapping.strip().split('<MAP>')
                abs, _ = abstraction.split('_')
                if name in nodes_set:
                    temp[abs].append(name)
            for k, v in temp.items():
                for i, name in enumerate(v):
                    mapping_dict[name] = k + '_' + str(i + 1)

            mappings = mapping_add.split(' <SEP> ')[:-1]
            for mapping in mappings:
                name, abstraction = mapping.strip().split('<MAP>')
                if name not in mapping_dict:
                    abs, _ = abstraction.split('_')
                    mapping_dict[name] = abs + '_<UNK>'

            input_ast.append({
                'id': cnt,
                'mappings': mapping_dict,
                'nodes': nodes,
                'edges': rem_edges,
                'rem_roots': rem_roots,
                'add_roots': []
            })
        else:
            rem = rem.split('\t')
            rem_ctx_split = []
            pre_index = 0
            loc, index, code = rem[0], int(rem[1]), rem[2]
            rem_match = {
                'location': loc,
                'index': index,
                'code': code.strip(),
                'match': None,
                'matched_cnt': 0
            }
            cur_index = [j for j in range(len(rem_ctx)) if rem_ctx.startswith(code.strip(), j)][index]
            rem_ctx_split.append(rem_ctx[pre_index: cur_index])
            pre_index = cur_index + len(code)
            rem_match['code'] = re.sub('\\s+|\\(|\\)|{|}|;|,', '', rem_match['code'])
            rem_ctx_split.append(rem_ctx[pre_index:])

            try:
                tokens = javalang.tokenizer.tokenize(rem_ctx)
                parser = javalang.parser.Parser(tokens)
                rem_ast = parser.parse_member_declaration()
            except Exception as e:
                print("Failed at line 411")
                print(cnt, "parse failed")
                continue
            traverse, rem_edges = dfs(rem_ast)
            nodes, rem_roots = [], []
            for _, node in enumerate(traverse):
                if isinstance(node, Node):
                    node_code = node.to_code()
                    nodes.append(node.__class__.__name__)
                elif type(node) in [list, set]:
                    node_code = ' '.join([s for s in list(node)])
                    nodes.append(node_code.strip())
                else:
                    node_code = str(node)
                    nodes.append(node_code.strip())

                node_code = re.sub('\\s+|\\(|\\)|{|}|;|,', '', node_code)

                is_rem_root = False
                if rem_match['code'] == node_code and \
                        not (isinstance(node, BlockStatement) and len(getattr(node, "statements")) == 1):
                    if rem_match['matched_cnt'] == rem_match['index']:
                        rem_match['match'] = node
                        is_rem_root = True
                    rem_match['matched_cnt'] += 1
                if is_rem_root:
                    rem_roots.append(_)
            rem_nodes = [rem_match['match']] if rem_match['match'] is not None else []
            if len(rem_roots) != 1 or len(rem_nodes) != 1:
                cant_localize += 1
                print(cnt, "match rem failed", rem)
                continue

            mapping_dict = {}
            mapping_rem, mapping_add = mappings.split('\t')
            mappings = mapping_rem.split(' <SEP> ')[:-1]

            nodes_set = set(nodes)
            temp = {k: [] for k in ('VAR', 'TYPE', 'METHOD', 'INT', 'STRING', 'FLOAT', 'CHAR')}
            for mapping in mappings:
                name, abstraction = mapping.strip().split('<MAP>')
                abs, _ = abstraction.split('_')
                if name in nodes_set:
                    temp[abs].append(name)
            for k, v in temp.items():
                for i, name in enumerate(v):
                    mapping_dict[name] = k + '_' + str(i + 1)

            mappings = mapping_add.split(' <SEP> ')[:-1]
            for mapping in mappings:
                name, abstraction = mapping.strip().split('<MAP>')
                if name not in mapping_dict:
                    abs, _ = abstraction.split('_')
                    mapping_dict[name] = abs + '_<UNK>'

            input_ast.append({
                'id': cnt,
                'mappings': mapping_dict,
                'nodes': nodes,
                'edges': rem_edges,
                'rem_roots': rem_roots,
                'add_roots': [],
            })
    json.dump(input_ast, open(data_dir + 'input_' + target_tag + '_ast.json', 'w'))

    print("can't localize", cant_localize)
    print("localize succeed", len(input_ast))

    if target_tag == 'insert':
        remove_pad_statement_from_mapping(data_dir + 'input_insert_ast.json')


def prepare_identifier_data(meta_file, output_file, tmp_dir):
    meta = read_meta(meta_file)
    identifiers_list = {}
    current_bug = None
    for i, meta_line in enumerate(meta):
        if len(meta_line) == 6:
            proj, bug_id, file_path, rem_start, rem_end, tag = meta_line
        elif len(meta_line) == 5:
            proj, bug_id, file_path, rem_start, rem_end = meta_line
        if proj + '_' + bug_id != current_bug:
            current_bug = proj + '_' + bug_id
            print(proj, bug_id)
            general_command.clean_tmp_folder(tmp_dir)
            general_command.checkout_general_project(proj, bug_id, tmp_dir)
        extract_identifiers(proj, file_path, rem_start, rem_end,
                            SRC_DIR + '../data/jdk.json')
        if os.path.exists(output_file):
            identifiers = json.load(open(output_file, 'r'))
        else:
            identifiers = {}
        identifiers = combine_super_methods(identifiers)
        print('identifiers num:', len(identifiers))
        identifiers_list[i + 1] = identifiers
    json.dump(identifiers_list, open(output_file, 'w'))


if __name__ == '__main__':
    prepare_localize_data(data_dir=SRC_DIR + '../data/general_input/')
    prepare_mapping_data(data_dir=SRC_DIR + '../data/general_input/')
    for tag in ('general', 'insert'):
        prepare_ast_data(data_dir=SRC_DIR + '../data/general_input/', target_tag=tag)
    prepare_identifier_data(
        meta_file=SRC_DIR + '../data/general_input/meta_localize.txt',
        output_file=SRC_DIR + '../data/general_input/identifiers.json',
        tmp_dir='/tmp/'
    )

