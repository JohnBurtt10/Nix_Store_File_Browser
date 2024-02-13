from cache_directories import *
def group_items(references, dependency_store_path_dict):
    #TODO: testing performance
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