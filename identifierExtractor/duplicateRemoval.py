import json
import hashlib
from pprint import pprint


def hash_entry(entry):
    """
    Generate a hash for an entry excluding the 'cnt' field.
    This ensures that identical entries (except count) are merged.
    """
    entry_copy = entry.copy()
    entry_copy.pop('cnt', None)  # Remove 'cnt' for hashing
    return hashlib.md5(json.dumps(entry_copy, sort_keys=True).encode()).hexdigest()


def merge_duplicate_entries(data):
    """
    Merges duplicate entries by summing up their 'cnt' values while keeping unique properties intact.
    """
    cleaned_data = {}

    for identifier, entries in data.items():
        unique_entries = {}

        for entry in entries:
            entry_hash = hash_entry(entry)
            if entry_hash in unique_entries:
                unique_entries[entry_hash]['cnt'] += entry.get('cnt', 1)  # Merge count
            else:
                unique_entries[entry_hash] = entry.copy()

        cleaned_data[identifier] = list(unique_entries.values())

    return cleaned_data


def process_json_file(json_path):
    """
    Loads the JSON file, extracts key '1', removes duplicates, and saves only the cleaned key '1' block.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "1" not in data:
            print("Key '1' not found in JSON.")
            return

        print("[DEBUG] Original data under key '1':")
        pprint(data["1"])

        cleaned_inner = merge_duplicate_entries(data["1"])

        # Save only the cleaned '1' key content
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_inner, f, indent=4, ensure_ascii=False)

        print(f"Successfully cleaned duplicates under key '1' in '{json_path}'")

    except Exception as e:
        print(f"Error processing JSON file: {e}")


if __name__ == "__main__":
    json_file = "identifiers.json"  # Modify if using a different filename
    process_json_file(json_file)
