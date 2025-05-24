import os
import json

def process_file(filepath):
    """
    Process a single JSON file to compute and add 'Plausible' and 'Plausible_Reasoning' fields.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    plausible = None
    plausible_reasoning = None

    compilation = data.get('Compilation')
    
    # Rule: If Compilation is "Fail"
    if compilation == "Fail":
        plausible = False
        plausible_reasoning = False

    # Rule: If Compilation is "Success"
    elif compilation == "Success":
        # Determine 'Plausible'
        ts = data.get('TestSingle')
        ta = data.get('TestAll')
        if ts is not None and ta is not None:
            if (ts == "Pass" or ta == "Pass") and ts != "Fail" and ta != "Fail":
                plausible = True
            else:
                plausible = False

        # Determine 'Plausible_Reasoning'
        cos_sim = data.get('reasoning_cosine_similarity')
        rouge_l = data.get('reasoning_rouge_l')
        if cos_sim is not None and rouge_l is not None:
            if cos_sim >= 0.84 and rouge_l >= 0.34:
                plausible_reasoning = True
            else:
                plausible_reasoning = False

    # Add computed fields if they were determined
    if plausible is not None:
        data['Plausible'] = plausible
    if plausible_reasoning is not None:
        data['Plausible_Reasoning'] = plausible_reasoning

    # Write updates back to the JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    base_dir = "./knod_evaluation_results_llama"
    for dirpath, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                file_path = os.path.join(dirpath, filename)
                process_file(file_path)

if __name__ == "__main__":
    main()

