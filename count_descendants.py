from raw_data_utilities import extract_section
from cache_directories import *
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path

def count_descendants(hydra, raw_data, reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict):
    references = extract_section(raw_data=raw_data, keyword="References")
    for reference in references:
        if "logic_strategy_editor" in reference:
            print(f"reference: {reference}")
        parts = reference.split('-', 1)
        key = parts[1]
        (reverse_dependency_weight_dict[key], file_size_reverse_dependency_weight_dict[key]) = _count_descendants(hydra, reference)
        # print(f"count_descendants: {reverse_dependency_weight_dict}")

    return reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict


def _count_descendants(hydra, package):
    if "logic_strategy_editor" in package:
        print(f"reference: {package}")
    if package is None:
        return (0, 0)
    
    if package in count_descentdants_cache:
        return count_descentdants_cache[package]
    
    (references, _) = get_references_and_file_size_from_store_path(hydra, package)

    descent_count = 0
    descent_file_size = 0
    references_file_size = 0
    for child in references:
        # print(f"package: {child}")
        (_, child_file_size) = get_references_and_file_size_from_store_path(hydra, package)
        references_file_size += child_file_size
        #TODO: decide whether or not this is needed
        if child != package:
            (child_descent_count, child_descent_file_size) = _count_descendants(hydra, child)
            count_descentdants_cache[child] = (child_descent_count, child_descent_file_size)
            descent_count += child_descent_count
            descent_file_size += child_descent_file_size

    return (descent_count + len(references), descent_file_size + references_file_size)


