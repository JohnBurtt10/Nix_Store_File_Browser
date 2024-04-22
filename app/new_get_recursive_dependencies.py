from .raw_data_utilities import extract_section
from .cache_directories import *
from .merge_dicts_with_preference import merge_dicts_with_preference
from tqdm import tqdm
from .job_whitelist import job_whitelist
from collections import deque


def get_recursive_dependencies(hydra, update_progress, report_error, project_name, jobset, traverse_jobset, references_dict, file_size_dict,
                               only_visit_once_enabled=True, progress_bar_enabled=False, progress_bar_desc="Default progress bar desc", jobs=job_whitelist,
                               unique_packages_enabled=False, stripped_references_visited=set(), references_visited=set(), maximum_recursive_file_size=None):

    recursive_dependencies_dict = {}

    with tqdm(total=len(jobs), disable=not progress_bar_enabled, desc=progress_bar_desc, unit="builds") as pbar:
        for job in jobs:
            if (jobset, job, unique_packages_enabled, maximum_recursive_file_size) in get_recursive_dependencies_cache:
                recursive_dependencies_dict = merge_dicts_with_preference(
                    get_recursive_dependencies_cache[(jobset, job, unique_packages_enabled, maximum_recursive_file_size)], recursive_dependencies_dict)
            else:
                _recursive_dependencies_dict = {}
                traverse_jobset(hydra, update_progress, report_error, project_name, jobset,
                                lambda job, raw_data: _get_recursive_dependencies(raw_data, _recursive_dependencies_dict, maximum_recursive_file_size,
                                                                                  references_dict, file_size_dict), recursive_mode_enabled=True, only_visit_once_enabled=True,
                                progress_bar_enabled=True, whitelist_enabled=True, progress_bar_desc="Getting recursive dependencies", jobs=[job], cancellable=True,
                                unique_packages_enabled=unique_packages_enabled, stripped_references_visited=stripped_references_visited, references_visited=references_visited)

                get_recursive_dependencies_cache[(
                    jobset, job, unique_packages_enabled, maximum_recursive_file_size)] = _recursive_dependencies_dict
                recursive_dependencies_dict = merge_dicts_with_preference(
                    recursive_dependencies_dict, _recursive_dependencies_dict)
            pbar.update(1)
        return recursive_dependencies_dict


def _get_recursive_dependencies(raw_data, recursive_dependencies_dict, maximum_recursive_file_size, references_dict, file_size_dict):
    store_path = extract_section(raw_data=raw_data, keyword="StorePath")[0]
    result = store_path.split("/nix/store/")[1]

    if (result, maximum_recursive_file_size) in _get_recursive_dependencies_cache:
        recursive_dependencies_dict[result] = _get_recursive_dependencies_cache[(
            result, maximum_recursive_file_size)]
    else:
        recursive_dependencies = []
        recursive_dependencies = __get_recursive_dependencies(
            result, references_dict, file_size_dict, maximum_recursive_file_size)
        recursive_dependencies_dict[result] = recursive_dependencies
        _get_recursive_dependencies_cache[(
            result, maximum_recursive_file_size)] = recursive_dependencies

# def __get_recursive_dependencies(hydra, package, depth=0, recursive_dependencies=[], flag=False, path=()):
#     if package is None:
#         return (None)

#     # if package in _get_recursive_dependencies_cache:

#     #     return _get_recursive_dependencies_cache[package]
#     (references, _) = get_references_and_file_size_from_store_path(hydra, package)
#     count = 0
#     for child in references:
#         count = count + 1
#         if child != package:
#             if child not in recursive_dependencies:
#                 recursive_dependencies.append(child)
#                 __get_recursive_dependencies(
#                     hydra, child, depth+1, recursive_dependencies, flag=flag, path=path + (child,))

#     # used to keep track of which ones are done
#     return None if recursive_dependencies == [] else recursive_dependencies

# # Sample graph representation using a dictionary
# graph = {
#     'A': ['B', 'C'],
#     'B': ['D', 'E'],
#     'C': ['F'],
#     'D': [],
#     'E': ['F'],
#     'F': []
# }

# # Function to simulate getting references and file size from store path
# def get_references_and_file_size_from_store_path(hydra, node):
#     references = graph.get(node, [])
#     # Assuming file size is 1 for each node for simplicity
#     file_size = 1
#     return references, file_size


def __get_recursive_dependencies(package, references_dict, file_size_dict, maximum_recursive_file_size=None, recursive_file_size=0):
    if package is None:
        return None

    recursive_dependencies = []

    queue = deque([package])  # Initialize the queue with the starting node

    file_size = file_size_dict[package]

    recursive_file_size += file_size

    while queue:
        node = queue.popleft()  # Dequeue the first node from the queue

        # if node in recursive_dependencies:
        #     continue

        # Process the node here (e.g., get references and file size)
        references = references_dict[node]

        # Add child nodes to the queue
        for child in references:
            if child != package and child not in recursive_dependencies:
                child_file_size = file_size_dict[child]
                if maximum_recursive_file_size:
                    if child_file_size + recursive_file_size >= maximum_recursive_file_size:
                        continue
                recursive_file_size += child_file_size
                recursive_dependencies.append(child)
                queue.append(child)

    return recursive_dependencies


def main():
    pass


if __name__ == "__main__":
    main()
