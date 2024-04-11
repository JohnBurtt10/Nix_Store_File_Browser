import subprocess
import json
from datetime import datetime
from write_to_file import write_dict_to_file
from cache_directories import *


def git_ls_remote(url, pattern):
    command = ['git', 'ls-remote', url, pattern]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return []


def extract_tag_name(line):
    # Split the line by tabs and get the second part
    tag_part = line.split('\t')[1]
    # Get the part after the last '/'
    tag_name = tag_part.split('/')[-1]
    return tag_name


def extract_hash_from_path(path):
    # Find the start and end index of the hash part
    start_index = path.rfind('/') + 1
    end_index = path.find('-')
    # Extract the hash substring
    hash_part = path[start_index:end_index]
    return hash_part


def extract_hash_from_path(path):
    # Find the start and end index of the hash part
    start_index = path.rfind('/') + 1
    end_index = path.find('-')
    # Extract the hash substring
    hash_part = path[start_index:end_index]
    return hash_part


def extract_filename_from_path(path):
    # Find the start index of the filename
    start_index = path.rfind('/') + 1
    # Find the index of the first '-' after the hash
    end_index = path.find('-', start_index)
    # Extract the filename substring
    filename = path[end_index + 1:]
    return filename


def merge_lists(dict1, dict2):
    merged_dict = {}

    # Iterate through keys of both dictionaries
    for key in set(dict1.keys()) | set(dict2.keys()):
        # Merge lists if key exists in both dictionaries
        if key in dict1 and key in dict2:
            merged_dict[key] = dict1[key] + dict2[key]
        # Otherwise, add the list from the dictionary where key exists
        elif key in dict1:
            merged_dict[key] = dict1[key]
        else:
            merged_dict[key] = dict2[key]

    return merged_dict


def feth_and_compare_nix_paths(start_date, end_date):
    url = "https://gitlab.clearpathrobotics.com/sweng-infra/nix.git"
    pattern = "refs/tags/2.32*"
    lines = git_ls_remote(url, pattern)

    my_dict = {}

    for line in lines:
        tag_name = extract_tag_name(line)
        # Extract timestamp from the tag name
        timestamp_str = tag_name.split('-')[1]
        tag_date = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        print(f"tag_name={tag_name}")
        if start_date <= tag_date <= end_date:
            if tag_name in fetch_and_compare_nix_paths_cache:
                _my_dict = fetch_and_compare_nix_paths_cache[tag_name]
            else:
                _my_dict = {}
                command = f"nix path-info clearpath/{tag_name}#sdk.setup-dev --recursive --derivation --json"
                # Execute the commands
                try:
                    result = subprocess.run(
                        command, capture_output=True, text=True, check=True, shell=True)
                    # Parse JSON results
                    data = json.loads(result.stdout)

                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")

                # Compare paths and hashes
                for item in data:
                    path = item["path"]
                    hash = extract_hash_from_path(path)
                    filename = extract_filename_from_path(path)

                    if filename not in _my_dict:
                        _my_dict[filename] = [hash]
                    else:
                        if hash not in _my_dict[filename]:
                            _my_dict[filename].append(hash)

                fetch_and_compare_nix_paths_cache[tag_name] = _my_dict

                my_dict = merge_lists(my_dict, _my_dict)

    return my_dict


def main():
    start_date = datetime.strptime("2022-08-15", '%Y-%m-%d')
    # end_date = datetime.strptime("2025-08-15", '%Y-%m-%d')
    end_date = datetime.strptime("2023-08-16 14:49:33", '%Y-%m-%d %H:%M:%S')
    # end_date = datetime.now()  # You can specify an end date as well
    my_dict = feth_and_compare_nix_paths(start_date, end_date)

    my_other_dict = {}

    for key in my_dict:
        my_other_dict[key.replace(".drv", "")] = len(my_dict[key])

    write_dict_to_file(my_other_dict, "hoeog", "gowfko", "0")


if __name__ == "__main__":
    main()
