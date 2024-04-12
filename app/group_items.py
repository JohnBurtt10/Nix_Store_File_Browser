from .cache_directories import *


def group_items(references, dependency_store_path_dict):
    """
    Groups items based on the equality of the second part after splitting each item in 'references' by '-'.

    Args:
    - references (list): A list of items to be grouped.
    - dependency_store_path_dict (dict): A dictionary to store the hash values corresponding to the grouped items.

    Returns:
    - dict: A dictionary containing grouped items where the grouping criterion is the second part after splitting by '-'.

    Note:
    The function uses a cache ('group_items_cache') to improve performance by avoiding redundant computations.

    Example:
    ```
    references = ['hash1-item1', 'hash2-item2', 'hash1-item3']
    dependency_store = {}
    result = group_items(references, dependency_store)
    print(result)
    # Output: {'item1': ['hash1-item1'], 'item2': ['hash2-item2'], 'item3': ['hash1-item3']}
    ```

    """
    # TODO: testing performance
    if references in group_items_cache:
        return group_items_cache[references]
    grouped_items = {}
    for dependency in references:
        # Group items based on the equality of the second part after splitting by '-'
        parts = dependency.split('-', 1)
        hash = parts[0]
        # Using the second part as the grouping criterion
        key = parts[1] if len(parts) > 1 else dependency
        grouped_items.setdefault(key, []).append(dependency)
        dependency_store_path_dict[key] = hash
    group_items_cache[references] = grouped_items
    return grouped_items
