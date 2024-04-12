from .cache_directories import *
from . import cache_utils
from .raw_data_utilities import extract_section
from .sum_dicts import sum_dicts



async def _count_ancestors(hydra, package, current_depth, max_depth, references_dict, file_size_dict):

    count = {}
    count_key = {}
    total_nodes = 0  # New variable to keep track of total nodes
    total_file_size = 0  # New variable to keep track of total file size
    count_file_size = {}  # New variable to keep track of count file size
    target_count = {}
    t = {}
    target_file_size = {}

    parts = package.split('-', 1)
    hash_value = parts[0]
    key = parts[1]

    try:
        references = references_dict[package]
    except:
        print(f"references array miss: {package}")
        raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
        references = extract_section(raw_data=raw_data, keyword="References")

    try:
        file_size = file_size_dict[package]
    except:
        print(f"file size array miss: {package}")
        raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
        file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])



    # raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
    # references = extract_section(raw_data=raw_data, keyword="References")
    # file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])

    total_nodes += 1
    total_file_size += file_size

    if package is not None:
        if package not in count:
            count[package] = 0
        count[package] += 1
        if key not in count_key:
            count_key[key] = 0
        count_key[key] += 1
        # TODO: I changed this to be key for now
        if key not in count_file_size:
            count_file_size[key] = 0
        count_file_size[key] += file_size
        if package not in target_count:
            target_count[package] = 0
        target_count[package] += 1
        if package not in target_file_size:
            target_file_size[package] = 0
        target_file_size[package] += file_size

        for child in references:
            if child != package:
                if child in count_ancestor_cache:
                    c, ck, nodes, t, size, count_size, t_file_size = count_ancestor_cache[child]
                else:
                    c, ck, nodes, t, size, count_size, t_file_size = await _count_ancestors(hydra, child, current_depth+1, max_depth, references_dict, file_size_dict)
                    count_ancestor_cache[child] = (
                        c, ck, nodes, t, size, count_size, t_file_size)
                count = sum_dicts(count, c)
                count_key = sum_dicts(count_key, ck)
                total_nodes += nodes
                total_file_size += file_size
                target_file_size = sum_dicts(target_file_size, t_file_size)
                count_file_size = sum_dicts(count_file_size, count_size)
                target_count = sum_dicts(target_count, t)

        for x in count:
            # TODO: change that to ==
            if count[x] > 0 and x not in package:
                # Increment count for the current node (ancestor)
                count[x] += 1
                count_key[key] += 1
                count_file_size[key] += file_size

    # Return count of ancestors, total node count, total file size, and count file size
    return count, count_key, total_nodes, target_count, total_file_size, count_file_size, target_file_size
