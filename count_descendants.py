from raw_data_utilities import extract_section
from cache_directories import *
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path


def count_descendants(hydra, raw_data, reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict):
    """
    Count descendants for each reference in the given raw data.

    Args:
    - hydra (Hydra): The hydra information.
    - raw_data (str): Raw data containing information.
    - reverse_dependency_weight_dict (dict): Dictionary to store reverse dependency weights.
    - file_size_reverse_dependency_weight_dict (dict): Dictionary to store file size reverse dependency weights.

    Returns:
    - tuple: A tuple containing updated reverse_dependency_weight_dict and file_size_reverse_dependency_weight_dict.

    Note:
    The function extracts references from the raw data, splits them, and counts descendants for each reference.
    The results are stored in the provided dictionaries.

    Example:
    ```
    hydra =
    raw_data = "example raw data"
    reverse_dependency_weight_dict = {}
    file_size_reverse_dependency_weight_dict = {}
    result = count_descendants(hydra, raw_data, reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)
    print(result)
    # Output: ({'key1': 5, 'key2': 10}, {'key1': 100, 'key2': 200})
    ```

    """
    references = extract_section(raw_data=raw_data, keyword="References")
    for reference in references:
        parts = reference.split('-', 1)
        key = parts[1]
        (reverse_dependency_weight_dict[key], file_size_reverse_dependency_weight_dict[key]) = _count_descendants(
            hydra, reference)

    return reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict


def _count_descendants(hydra, package):
    if package is None:
        return (0, 0)

    if package in count_descentdants_cache:
        return count_descentdants_cache[package]

    (references, _) = get_references_and_file_size_from_store_path(hydra, package)

    descent_count = 0
    descent_file_size = 0
    references_file_size = 0
    for child in references:
        (_, child_file_size) = get_references_and_file_size_from_store_path(
            hydra, package)
        references_file_size += child_file_size
        # TODO: decide whether or not this is needed
        if child != package:
            (child_descent_count, child_descent_file_size) = _count_descendants(
                hydra, child)
            count_descentdants_cache[child] = (
                child_descent_count, child_descent_file_size)
            descent_count += child_descent_count
            descent_file_size += child_descent_file_size

    return (descent_count + len(references), descent_file_size + references_file_size)
