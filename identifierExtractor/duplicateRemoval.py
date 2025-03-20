import json
import hashlib


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
    Loads the JSON file, processes it to remove duplicates, and saves the cleaned file.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Process each file's identifier data
        cleaned_data = {file_id: merge_duplicate_entries(entries) for file_id, entries in data.items()}

        # Save the cleaned JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

        print(f"Successfully cleaned duplicates in '{json_path}'")

    except Exception as e:
        print(f"Error processing JSON file: {e}")


if __name__ == "__main__":
    json_file = "identifiers.json"  # Modify if using a different filename
    process_json_file(json_file)
