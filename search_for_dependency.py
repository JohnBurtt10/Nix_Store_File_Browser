from cache_directories import *
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path

def search_for_dependency(hydra, package, target):
    """
    Search for a dependency in the given hydra package.

    Args:
    - hydra (Hydra): The hydra information.
    - package (str): The package to search for dependencies.
    - target (str): The target dependency to search.

    Returns:
    - bool: True if the target dependency is found, False otherwise.

    Note:
    The function retrieves references and file size information for the given package and searches for the target
    dependency among the references. It uses caching to improve performance.

    Example:
    ```
    hydra =
    package = "example_package"
    target = "example_target"
    result = search_for_dependency(hydra, package, target)
    print(result)
    # Output: True or False
    ```

    """
    # if (package, target) in search_for_dependency_cache:
    #     return search_for_dependency_cache[(package, target)]
    (references, _) = get_references_and_file_size_from_store_path(hydra, package)
    for reference in references:
        if reference == target or _search_for_dependency(
                hydra, reference, target):
            search_for_dependency_cache[(package, target)] = True
            return True
    search_for_dependency_cache[(package, target)] = False
    return False


def _search_for_dependency(hydra, package, target):
    if package is None:
        return False

    if (package, target) in search_for_dependency_cache:
        return search_for_dependency_cache[(package, target)]

    (references, _) = get_references_and_file_size_from_store_path(hydra, package)

    # TODO: change this to be breadth first probably
    for child in references:
        if child != package:
            if child == target:
                # search_for_dependency_cache[(child, target)] = True
                return True
    for child in references:
        if child != package:
            if _search_for_dependency(
                    hydra, child, target):
                return True
    # search_for_dependency_cache[(package, target)] = False
    return False
