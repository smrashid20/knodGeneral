import os
import json
from glob import glob
from statistics import mean


def safe_mean(values):
    return mean(values) if values else -1


def process_directory(base_dir="knod_evaluation_results_llama", output_file="knod_vulnerability_analysis.json"):
    result = []
    overall = {
        "vul_id": "Overall",
        "total_vul_ids": 0,
        "vul_ids_with_compilable_patch": 0,
        "vul_ids_with_plausible_patch": 0,
        "compilation_success": 0,
        "Plausible": 0,
        "plausible_ids": [],
        "reasoning_cosine_similarity_all": [],
        "reasoning_cosine_similarity_success": [],
        "reasoning_cosine_similarity_fail": [],
        "reasoning_cosine_similarity_plausible_success": [],
        "reasoning_cosine_similarity_plausible_fail": [],
        "reasoning_rouge_l_all": [],
        "reasoning_rouge_l_success": [],
        "reasoning_rouge_l_fail": [],
        "reasoning_rouge_l_plausible_success": [],
        "reasoning_rouge_l_plausible_fail": [],
        "patch_cosine_similarity_all": [],
        "patch_cosine_similarity_success": [],
        "patch_cosine_similarity_fail": [],
        "patch_cosine_similarity_plausible_success": [],
        "patch_cosine_similarity_plausible_fail": [],
        "patch_rouge_l_all": [],
        "patch_rouge_l_success": [],
        "patch_rouge_l_fail": [],
        "patch_rouge_l_plausible_success": [],
        "patch_rouge_l_plausible_fail": [],
        "gpt_total": 0,
        "total_patches": 0,
        "gpt_success": 0,
        "gpt_fail": 0,
        "gpt_plausible_success": 0,
        "gpt_plausible_fail": 0
    }

    for vul_id in os.listdir(base_dir):
        vul_path = os.path.join(base_dir, vul_id, "1")
        if not os.path.isdir(vul_path):
            continue

        json_files = glob(os.path.join(vul_path, "*.json"))
        if not json_files:
            continue

        stats = {
            "vul_id": vul_id,
            "compilation_success": 0,
            "Plausible": 0,
            "plausible_ids": [],
            "reasoning_cosine_similarity_all": [],
            "reasoning_cosine_similarity_success": [],
            "reasoning_cosine_similarity_fail": [],
            "reasoning_cosine_similarity_plausible_success": [],
            "reasoning_cosine_similarity_plausible_fail": [],
            "reasoning_rouge_l_all": [],
            "reasoning_rouge_l_success": [],
            "reasoning_rouge_l_fail": [],
            "reasoning_rouge_l_plausible_success": [],
            "reasoning_rouge_l_plausible_fail": [],
            "patch_cosine_similarity_all": [],
            "patch_cosine_similarity_success": [],
            "patch_cosine_similarity_fail": [],
            "patch_cosine_similarity_plausible_success": [],
            "patch_cosine_similarity_plausible_fail": [],
            "patch_rouge_l_all": [],
            "patch_rouge_l_success": [],
            "patch_rouge_l_fail": [],
            "patch_rouge_l_plausible_success": [],
            "patch_rouge_l_plausible_fail": [],
            "gpt_total": 0,
            "total_patches": 0,
            "gpt_success": 0,
            "gpt_fail": 0,
            "gpt_plausible_success": 0,
            "gpt_plausible_fail": 0
        }

        has_any_valid_file = False

        for file_path in json_files:
            with open(file_path) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

            prompt_id = os.path.basename(file_path).replace(".json", "")
            stats["total_patches"] += 1
            overall["total_patches"] += 1

            # Initialize default values for optional metrics
            compiles = False
            plausible = False
            gpt = False
            rcos = 0
            rrl = 0
            pcos = 0
            prl = 0

            # Process required fields
            if "Compilation" in data:
                compiles = data["Compilation"] == "Success"
            if "Plausible" in data:
                plausible = data["Plausible"]
            if "reasoning_gpt" in data:
                gpt = data["reasoning_gpt"]

            # Process optional metrics only if they exist
            if "reasoning_cosine_similarity" in data:
                rcos = data["reasoning_cosine_similarity"]
                stats["reasoning_cosine_similarity_all"].append(rcos)
                overall["reasoning_cosine_similarity_all"].append(rcos)

            if "reasoning_rouge_l" in data:
                rrl = data["reasoning_rouge_l"]
                stats["reasoning_rouge_l_all"].append(rrl)
                overall["reasoning_rouge_l_all"].append(rrl)

            if "patch_cosine_similarity" in data:
                pcos = data["patch_cosine_similarity"]
                stats["patch_cosine_similarity_all"].append(pcos)
                overall["patch_cosine_similarity_all"].append(pcos)

            if "patch_rouge_l" in data:
                prl = data["patch_rouge_l"]
                stats["patch_rouge_l_all"].append(prl)
                overall["patch_rouge_l_all"].append(prl)

            if compiles:
                stats["compilation_success"] += 1
                overall["compilation_success"] += 1

                if "reasoning_cosine_similarity" in data:
                    stats["reasoning_cosine_similarity_success"].append(rcos)
                    overall["reasoning_cosine_similarity_success"].append(rcos)
                if "reasoning_rouge_l" in data:
                    stats["reasoning_rouge_l_success"].append(rrl)
                    overall["reasoning_rouge_l_success"].append(rrl)
                if "patch_cosine_similarity" in data:
                    stats["patch_cosine_similarity_success"].append(pcos)
                    overall["patch_cosine_similarity_success"].append(pcos)
                if "patch_rouge_l" in data:
                    stats["patch_rouge_l_success"].append(prl)
                    overall["patch_rouge_l_success"].append(prl)

                if gpt:
                    stats["gpt_success"] += 1
                    overall["gpt_success"] += 1
            else:
                if "reasoning_cosine_similarity" in data:
                    stats["reasoning_cosine_similarity_fail"].append(rcos)
                    overall["reasoning_cosine_similarity_fail"].append(rcos)
                if "reasoning_rouge_l" in data:
                    stats["reasoning_rouge_l_fail"].append(rrl)
                    overall["reasoning_rouge_l_fail"].append(rrl)
                if "patch_cosine_similarity" in data:
                    stats["patch_cosine_similarity_fail"].append(pcos)
                    overall["patch_cosine_similarity_fail"].append(pcos)
                if "patch_rouge_l" in data:
                    stats["patch_rouge_l_fail"].append(prl)
                    overall["patch_rouge_l_fail"].append(prl)

                if gpt:
                    stats["gpt_fail"] += 1
                    overall["gpt_fail"] += 1

            if plausible:
                stats["Plausible"] += 1
                stats["plausible_ids"].append(prompt_id)
                overall["Plausible"] += 1
                overall["plausible_ids"].append(f"{vul_id}/{prompt_id}")

                if "reasoning_cosine_similarity" in data:
                    stats["reasoning_cosine_similarity_plausible_success"].append(rcos)
                    overall["reasoning_cosine_similarity_plausible_success"].append(rcos)
                if "reasoning_rouge_l" in data:
                    stats["reasoning_rouge_l_plausible_success"].append(rrl)
                    overall["reasoning_rouge_l_plausible_success"].append(rrl)
                if "patch_cosine_similarity" in data:
                    stats["patch_cosine_similarity_plausible_success"].append(pcos)
                    overall["patch_cosine_similarity_plausible_success"].append(pcos)
                if "patch_rouge_l" in data:
                    stats["patch_rouge_l_plausible_success"].append(prl)
                    overall["patch_rouge_l_plausible_success"].append(prl)

                if gpt:
                    stats["gpt_plausible_success"] += 1
                    overall["gpt_plausible_success"] += 1
            else:
                if "reasoning_cosine_similarity" in data:
                    stats["reasoning_cosine_similarity_plausible_fail"].append(rcos)
                    overall["reasoning_cosine_similarity_plausible_fail"].append(rcos)
                if "reasoning_rouge_l" in data:
                    stats["reasoning_rouge_l_plausible_fail"].append(rrl)
                    overall["reasoning_rouge_l_plausible_fail"].append(rrl)
                if "patch_cosine_similarity" in data:
                    stats["patch_cosine_similarity_plausible_fail"].append(pcos)
                    overall["patch_cosine_similarity_plausible_fail"].append(pcos)
                if "patch_rouge_l" in data:
                    stats["patch_rouge_l_plausible_fail"].append(prl)
                    overall["patch_rouge_l_plausible_fail"].append(prl)

                if gpt:
                    stats["gpt_plausible_fail"] += 1
                    overall["gpt_plausible_fail"] += 1

            if gpt:
                stats["gpt_total"] += 1
                overall["gpt_total"] += 1

            has_any_valid_file = True

        if not has_any_valid_file:
            continue

        overall["total_vul_ids"] += 1
        if stats["compilation_success"] > 0:
            overall["vul_ids_with_compilable_patch"] += 1
        if stats["Plausible"] > 0:
            overall["vul_ids_with_plausible_patch"] += 1

        result.append({
            "vul_id": vul_id,
            "compilation_success": stats["compilation_success"],
            "Plausible": stats["Plausible"],
            "plausible_ids": stats["plausible_ids"],
            "avg_reasoning_cosine_all": safe_mean(stats["reasoning_cosine_similarity_all"]),
            "avg_reasoning_cosine_success": safe_mean(stats["reasoning_cosine_similarity_success"]),
            "avg_reasoning_cosine_fail": safe_mean(stats["reasoning_cosine_similarity_fail"]),
            "avg_reasoning_cosine_plausible_success": safe_mean(stats["reasoning_cosine_similarity_plausible_success"]),
            "avg_reasoning_cosine_plausible_fail": safe_mean(stats["reasoning_cosine_similarity_plausible_fail"]),
            "avg_reasoning_rouge_l_all": safe_mean(stats["reasoning_rouge_l_all"]),
            "avg_reasoning_rouge_l_success": safe_mean(stats["reasoning_rouge_l_success"]),
            "avg_reasoning_rouge_l_fail": safe_mean(stats["reasoning_rouge_l_fail"]),
            "avg_reasoning_rouge_l_plausible_success": safe_mean(stats["reasoning_rouge_l_plausible_success"]),
            "avg_reasoning_rouge_l_plausible_fail": safe_mean(stats["reasoning_rouge_l_plausible_fail"]),
            "avg_patch_cosine_all": safe_mean(stats["patch_cosine_similarity_all"]),
            "avg_patch_cosine_success": safe_mean(stats["patch_cosine_similarity_success"]),
            "avg_patch_cosine_fail": safe_mean(stats["patch_cosine_similarity_fail"]),
            "avg_patch_cosine_plausible_success": safe_mean(stats["patch_cosine_similarity_plausible_success"]),
            "avg_patch_cosine_plausible_fail": safe_mean(stats["patch_cosine_similarity_plausible_fail"]),
            "avg_patch_rouge_l_all": safe_mean(stats["patch_rouge_l_all"]),
            "avg_patch_rouge_l_success": safe_mean(stats["patch_rouge_l_success"]),
            "avg_patch_rouge_l_fail": safe_mean(stats["patch_rouge_l_fail"]),
            "avg_patch_rouge_l_plausible_success": safe_mean(stats["patch_rouge_l_plausible_success"]),
            "avg_patch_rouge_l_plausible_fail": safe_mean(stats["patch_rouge_l_plausible_fail"]),
            "reasoning_gpt_total": f"{stats['gpt_total']}/{stats['total_patches']}",
            "reasoning_gpt_compilation_success": f"{stats['gpt_success']}/{stats['compilation_success']}",
            "reasoning_gpt_compilation_fail": f"{stats['gpt_fail']}/{stats['total_patches'] - stats['compilation_success']}",
            "reasoning_gpt_plausible_success": f"{stats['gpt_plausible_success']}/{stats['Plausible']}",
            "reasoning_gpt_plausible_fail": f"{stats['gpt_plausible_fail']}/{stats['total_patches'] - stats['Plausible']}"
        })

    result.append({
        "vul_id": "Overall",
        "total_vul_ids": overall["total_vul_ids"],
        "vul_ids_with_compilable_patch": overall["vul_ids_with_compilable_patch"],
        "vul_ids_with_plausible_patch": overall["vul_ids_with_plausible_patch"],
        "compilation_success": overall["compilation_success"],
        "Plausible": overall["Plausible"],
        "plausible_ids": overall["plausible_ids"],
        "avg_reasoning_cosine_all": safe_mean(overall["reasoning_cosine_similarity_all"]),
        "avg_reasoning_cosine_success": safe_mean(overall["reasoning_cosine_similarity_success"]),
        "avg_reasoning_cosine_fail": safe_mean(overall["reasoning_cosine_similarity_fail"]),
        "avg_reasoning_cosine_plausible_success": safe_mean(overall["reasoning_cosine_similarity_plausible_success"]),
        "avg_reasoning_cosine_plausible_fail": safe_mean(overall["reasoning_cosine_similarity_plausible_fail"]),
        "avg_reasoning_rouge_l_all": safe_mean(overall["reasoning_rouge_l_all"]),
        "avg_reasoning_rouge_l_success": safe_mean(overall["reasoning_rouge_l_success"]),
        "avg_reasoning_rouge_l_fail": safe_mean(overall["reasoning_rouge_l_fail"]),
        "avg_reasoning_rouge_l_plausible_success": safe_mean(overall["reasoning_rouge_l_plausible_success"]),
        "avg_reasoning_rouge_l_plausible_fail": safe_mean(overall["reasoning_rouge_l_plausible_fail"]),
        "avg_patch_cosine_all": safe_mean(overall["patch_cosine_similarity_all"]),
        "avg_patch_cosine_success": safe_mean(overall["patch_cosine_similarity_success"]),
        "avg_patch_cosine_fail": safe_mean(overall["patch_cosine_similarity_fail"]),
        "avg_patch_cosine_plausible_success": safe_mean(overall["patch_cosine_similarity_plausible_success"]),
        "avg_patch_cosine_plausible_fail": safe_mean(overall["patch_cosine_similarity_plausible_fail"]),
        "avg_patch_rouge_l_all": safe_mean(overall["patch_rouge_l_all"]),
        "avg_patch_rouge_l_success": safe_mean(overall["patch_rouge_l_success"]),
        "avg_patch_rouge_l_fail": safe_mean(overall["patch_rouge_l_fail"]),
        "avg_patch_rouge_l_plausible_success": safe_mean(overall["patch_rouge_l_plausible_success"]),
        "avg_patch_rouge_l_plausible_fail": safe_mean(overall["patch_rouge_l_plausible_fail"]),
        "reasoning_gpt_total": f"{overall['gpt_total']}/{overall['total_patches']}",
        "reasoning_gpt_compilation_success": f"{overall['gpt_success']}/{overall['compilation_success']}",
        "reasoning_gpt_compilation_fail": f"{overall['gpt_fail']}/{overall['total_patches'] - overall['compilation_success']}",
        "reasoning_gpt_plausible_success": f"{overall['gpt_plausible_success']}/{overall['Plausible']}",
        "reasoning_gpt_plausible_fail": f"{overall['gpt_plausible_fail']}/{overall['total_patches'] - overall['Plausible']}"
    })

    with open(output_file, "w") as out:
        json.dump(result, out, indent=2)


process_directory()