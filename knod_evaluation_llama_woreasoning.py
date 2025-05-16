import json
import os
import re
import sys

from evaluation_metric import cosine_similarity_between_texts, rouge_l_score_between_texts


# def generate_gt_reasoning(vul_id: str):
#     print(f"[DEBUG] Starting GT reasoning generation for: {vul_id}")
#     base_path = os.path.join("llm_outputs", vul_id)
#
#     description_path = os.path.join(base_path, "vulnerability_description.txt")
#     buggy_path = os.path.join(base_path, "buggy_block.txt")
#     fixed_path = os.path.join(base_path, "fixed_block.txt")
#     output_file = os.path.join(base_path, f"gt_reasoning_llama.txt")
#
#     print(f"[DEBUG] Checking if GT reasoning file exists: {output_file}")
#     if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
#         print(f"[SKIP] Ground truth reasoning already exists for {vul_id} using llama.")
#         return
#
#     try:
#         with open(description_path, 'r') as f:
#             vulnerability_description = f.read()
#         print(f"[DEBUG] Loaded vulnerability_description from {description_path}")
#         with open(buggy_path, 'r') as f:
#             buggy_block = f.read()
#         print(f"[DEBUG] Loaded buggy_block from {buggy_path}")
#         with open(fixed_path, 'r') as f:
#             fixed_block = f.read()
#         print(f"[DEBUG] Loaded fixed_block from {fixed_path}")
#     except FileNotFoundError as e:
#         print(f"[ERROR] Missing input file: {e.filename}")
#         return
#
#     print(f"[INFO] Generating ground truth reasoning for {vul_id} using llama...")
#     generate_gt_reasoning_llama(vulnerability_description, buggy_block, fixed_block, output_file)
#     print(f"[SUCCESS] Reasoning saved to {output_file}")


def extract_patch_from_text(text: str) -> str:
    match = re.search(r"//start of generated patch(.*?)//end of generated patch", text, re.DOTALL)
    print("[DEBUG] Extracted Patch: {}".format(match.group(1).strip()))
    return match.group(1).strip() if match else ""


def evaluate_llm(vul_id: str, target_model_name: str):
    print(f"[DEBUG] Starting KNOD evaluation for: {vul_id}")
    llm_outputs_path = os.path.join("llm_outputs", vul_id)
    gt_reasoning_path = os.path.join(llm_outputs_path, "gt_reasoning_llama.txt")
    evaluation_results_base = os.path.join("knod_evaluation_results_llama", vul_id)
    patch_base = os.path.join("knod_patches", vul_id)

    print(f"[DEBUG] Checking for GT reasoning at {gt_reasoning_path}")
    if not os.path.exists(gt_reasoning_path):
        print(f"[ERROR] Ground truth reasoning not found: {gt_reasoning_path}")
        return

    with open(gt_reasoning_path, 'r') as f:
        gt_reasoning = f.read()

    print(f"[DEBUG] Loaded GT reasoning")

    for expt_id in os.listdir(patch_base):
        expt_dir = os.path.join(patch_base, expt_id) # <vul_id>/1/
        results_dir = os.path.join(evaluation_results_base, expt_id)
        os.makedirs(results_dir, exist_ok=True)

        for file in os.listdir(expt_dir):
            if file.endswith(".json"):
                continue

            prompt_id = file.replace(".txt", "")
            reasoning_file_path = os.path.join(results_dir, file.replace(".txt", "_reasoning.txt"))

            patch_file_path = os.path.join(patch_base, expt_id, f"{prompt_id}.txt")
            results_path = os.path.join(results_dir, f"{prompt_id}.json")

            if os.path.exists(os.path.join(expt_dir, prompt_id + ".json")):
                original_json = json.load(open(os.path.join(expt_dir, prompt_id + ".json"), 'r'))

            print(f"[DEBUG] Evaluating prompt: {prompt_id}")
            print(f"[DEBUG] Reasoning path: {reasoning_file_path}")
            print(f"[DEBUG] Patch path: {patch_file_path}")

            patch_content = ""
            with open(patch_file_path, 'r') as f:
                patch_content = f.read()

            patch_content = extract_patch_from_text(patch_content)

            print(f"[DEBUG] Extracted patch : {patch_content}")

            result_data = {}

            gt_patch_path = os.path.join(llm_outputs_path, f"fixed_block.txt")
            print(f"[DEBUG] GT patch path: {gt_patch_path}")

            try:
                with open(gt_patch_path, 'r') as f:
                    gt_patch = f.read()
                print(f"[DEBUG] Loaded GT patch")

                with open(patch_file_path, 'r') as f:
                    patch_text = f.read()
                extracted_patch = extract_patch_from_text(patch_text)
                print(f"[DEBUG] Extracted patch from LLM response")

                patch_cosine = cosine_similarity_between_texts(gt_patch, extracted_patch)
                print(f"[DEBUG] Patch cosine similarity: {patch_cosine:.4f}")
                patch_rouge = rouge_l_score_between_texts(gt_patch, extracted_patch)
                print(f"[DEBUG] Patch ROUGE-L: {patch_rouge:.4f}")

                result_data["patch_cosine_similarity"] = float(patch_cosine)
                result_data["patch_rouge_l"] = float(patch_rouge)


            except Exception as e:
                print(f"[WARNING] Failed to evaluate patch for {prompt_id}: {e}")

            if original_json:
                original_json.update(result_data)
            else:
                original_json = result_data


            if original_json["TestSingle"] == "Pass" and original_json["TestAll"] == "NA":
                original_json["Plausible"] = True
            elif original_json["TestAll"] == "Pass":
                original_json["Plausible"] = True
            # elif original_json["TestSingle"] == "NA" and original_json["TestAll"] == "NA":
            #     if (original_json["Compilation"] == "Success"
            #             and original_json["reasoning_cosine_similarity"] >= 0.84
            #             and original_json["reasoning_rouge_l"] >= 0.34
            #             and original_json["reasoning_gpt"] == True):
            #         original_json["Plausible"] = True
            else:
                original_json["Plausible"] = False

            if os.path.exists(results_path):
                with open(results_path, 'r') as f:
                    existing_json = json.load(f)
                existing_json.update(original_json)
                original_json = existing_json

            with open(results_path, 'w') as f:
                json.dump(original_json, f, indent=2)
            print(f"[DONE] Saved evaluation for {prompt_id} in {expt_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reasoning_evaluator_llama.py <vul_id>")
        sys.exit(1)

    vul_id = sys.argv[1]
    target_model_name = "llama"
    # print(f"[START] Processing vulnerability: {vul_id}")
    # generate_gt_reasoning(vul_id)
    evaluate_llm(vul_id, target_model_name)
    print(f"[COMPLETE] Evaluation finished for: {vul_id}")
