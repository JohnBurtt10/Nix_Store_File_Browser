from hydra_client import Hydra
from cache_directories import *
from has_timestamp import has_timestamp
from raw_data_utilities import extract_section
import cache_utils
import asyncio
import concurrent.futures
from traverse_jobset import traverse_jobset
from count_descendants import count_descendants
from calculate_dependency_weight import calculate_dependency_weight

# TODO: break this up into multiple caches

# TODO: remove dependency_weight_dict from this


def compute_top_n_information(store_path_entropy_dict,
                              store_path_file_size_dict,
                              reverse_dependencies_dict,
                              dependency_store_path_dict,
                              dependency_all_store_path_dict,
                              store_path_jobsets_dict,
                              hydra,
                              project_name,
                              latest_jobset,
                              n=100,
                              print_file_size=True,
                              print_entropy=True,
                              print_dependency_weight=True,
                              sort_key1='entropy',
                              sort_key2='entropy',
                              sort_order='desc',
                              filters=[],
                              #   minimum_file_size=0,
                              #   minimum_entropy=0,
                              print_to_console=False):
    """
    Prints the top N values from dictionaries.

    Parameters:
    - store_path_entropy_dict (dict): Dictionary with entropy values.
    - store_path_file_size_dict (dict): Dictionary with file size values.
    - dependency_weight_dict (dict): Dictionary with dependency weights.
    - n (int): The number of top values to print. Default is 100.
    - print_file_size (bool): Whether to print file size. Default is True.
    - print_entropy (bool): Whether to print entropy. Default is True.
    - print_dependency_weight (bool): Whether to print dependency weight. Default is True.
    - sort_index (int): The index to use for sorting. 0 for file size, 1 for entropy, 2 for dependency weight. Default is 0.
    """

    # Define a mapping of sort indices to corresponding keys in the combined dictionary
    sort_mapping = {
        'file_size': 0,  # Sort by file size
        'entropy': 1,  # Sort by entropy
        'dependency_weight': 2,   # Sort by dependency weight
        'reverse_dependency_weight': 3
    }

    total_weight, weight_key, nodes, count_file_size, total_file_size = cache_utils.get_cached_or_compute_dependency_weight(
        project_name, latest_jobset, dependency_weight_cache, hydra, calculate_dependency_weight)

    # print(f"finished get_cached_or_compute_dependency_weight()")

    reverse_dependency_weight_dict = {}
    file_size_reverse_dependency_weight_dict = {}

    (reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict) = cache_utils.get_cached_or_compute_reverse_dependency_weight(project_name,
                                                                                                                                             latest_jobset,
                                                                                                                                             reverse_dependency_weight_cache,
                                                                                                                                             traverse_jobset,
                                                                                                                                             hydra,
                                                                                                                                             count_descendants)

    # return
    # print(f"finished get_cached_or_compute_reverse_dependency_weight(): {reverse_dependency_weight_dict}")
    # print(f"reverse_dependency_weight_dict: {reverse_dependency_weight_dict}")
    # Combine all dictionaries into a single dictionary with keys from file size dict
    combined_dict = {
        key: (store_path_file_size_dict.get(key, 0),
              store_path_entropy_dict.get(key, 0),
              weight_key.get(key, 0),
              reverse_dependency_weight_dict.get(key, 0))
        for key in store_path_file_size_dict
    }

    filtered_dict = combined_dict

    for filter in filters:
        extremum_select = filter.get('extremum_select')
        filter_key_select = filter.get('filter_key_select')
        filter_value = int(filter.get('filter_value'))

        print(f"extremum_select: {extremum_select}, filter_key_select: {filter_key_select}, filter_value: {filter_value}")

        # Filter out items based on conditions

        filtered_dict = {
            key: (file_size, entropy, dependency_weight, reverse_dependency_weight) for key, (file_size, entropy, dependency_weight, reverse_dependency_weight) in filtered_dict.items()
            if (extremum_select == 'minimum' and filter_key_select == 'entropy' and entropy >= filter_value) or
                (extremum_select == 'minimum' and filter_key_select == 'file_size' and file_size >= filter_value) or
                (extremum_select == 'minimum' and filter_key_select == 'dependency_weight' and dependency_weight >= filter_value) or
                (extremum_select == 'minimum' and filter_key_select == 'reverse_dependency_weight' and reverse_dependency_weight >= filter_value) or
                (extremum_select == 'maximum' and filter_key_select == 'entropy' and entropy <= filter_value) or
                (extremum_select == 'maximum' and filter_key_select == 'file_size' and file_size <= filter_value) or
                (extremum_select == 'maximum' and filter_key_select == 'dependency_weight' and dependency_weight <= filter_value) or
                (extremum_select == 'maximum' and filter_key_select == 'reverse_dependency_weight' and reverse_dependency_weight <= filter_value)
        }

    # Choose the sorting order based on user input
    reverse_order = sort_order.lower() == 'desc'

    # with this caching scheme, compute_top_n_information() is O(1) when there is a cache hit (vs. O(n) where n is the number of packages in the project)
    if False and (filtered_dict, sort_key1) in first_sort_cache:
        # cache hit!
        sorted_items = first_sort_cache[(filtered_dict, sort_key1)]
    else:

        # Sort the combined dictionary items based on the specified sort index
        sorted_items = sorted(filtered_dict.items(
        ), key=lambda x: x[1][sort_mapping.get(sort_key1, 0)], reverse=True)
        first_sort_cache[(filtered_dict, sort_key1)] = sorted_items

    # Extract the top N values
    top_n_values = sorted_items[:int(n)]

    top_n_values = sorted(top_n_values, key=lambda x: x[1][sort_mapping.get(
        sort_key2, 0)], reverse=True)

    top_n_values_dynamic = []
    for iteration, (key, (file_size, entropy, dependency_weight, reverse_dependency_weight)) in enumerate(top_n_values):
        if (print_to_console):
            output = f"{key}:"
            if print_file_size:
                output += f" File Size - {file_size},"
            if print_entropy:
                output += f" Entropy - {entropy},"
            if print_dependency_weight:
                output += f" Dependency Weight - {dependency_weight},"

        details = {
            "file_size": f"{file_size} MB",
            "entropy": entropy,
            "node_dependency_weight": f"{weight_key.get(key, 0)}",
            "file_size_dependency_weight": f"{count_file_size.get(key, 0)}",
            "reverse_dependency_weight": f"{reverse_dependency_weight}",
            "file_size_reverse_dependency_weight": f"{file_size_reverse_dependency_weight_dict.get(key, 0)}",
            "reverse_dependencies": reverse_dependencies_dict[key],
            "last_instance_hash": dependency_store_path_dict.get(key, ""),
            "store_paths": dependency_all_store_path_dict[key],
            "store_path_jobsets": store_path_jobsets_dict[key],
        }
        if (print_to_console):
            print(output.rstrip(','))
        top_n_values_dynamic.append((key, details))

    return top_n_values_dynamic


def get_children(hydra, hash):

    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash, False)
    store_path = extract_section(raw_data=raw_data, keyword="StorePath")[0]
    store_name = store_path.split("/nix/store/")[1]
    references = extract_section(raw_data=raw_data, keyword="References")
    if store_name in references:
        references.remove(store_name)
    return references


async def get_children_recursive(hydra, hash, visited=None):
    if visited is None:
        visited = set()

    # TODO: review this?
    if hash in visited:
        return set()

    visited.add(hash)

    raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash)
    try:
        references = extract_section(raw_data=raw_data, keyword="References")
    except AttributeError as e:
        print(f"raw data: {raw_data}")

    children = set(references)
    for child in references:
        parts = child.split('-', 1)
        hash_value = parts[0]
        if hash == hash_value:
            continue
        children.update(await get_children_recursive(hydra, hash_value, visited))

    return children


def sort_chunk(chunk, project_name, hydra, jobset):
    print(f"sort_chunk!")
    return sorted(chunk, key=lambda item: temp(project_name, hydra, jobset, item), reverse=True)


def parallel_sort(input_list, project_name, hydra, jobset, chunk_size=100):
    chunks = [input_list[i:i + chunk_size]
              for i in range(0, len(input_list), chunk_size)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda chunk: sort_chunk(
            chunk, project_name, hydra, jobset), chunks))

    return [item for sublist in results for item in sublist]


def overlap_and_disjoint(set1, set2):
    # Calculate the overlap (intersection) of the two sets
    overlap_set = set1.intersection(set2)

    # Calculate the disjoint elements of the two sets
    disjoint_set = set1.symmetric_difference(set2)

    return overlap_set, disjoint_set


def combine(project_name, hydra, list1, list2, jobsets=["v2.32.0-20240129033831-0"
                                                        ]):

    # Combine the lists based on the top 100 items
    combined_list = []

    total_weight = {}

    total_nodes = {}

    for jobset in jobsets:
        t_w, t_n = temp(project_name, hydra, jobset)
        total_weight = {key: total_weight.get(
            key, 0) + t_w.get(key, 0) for key in set(total_weight.keys()).union(set(t_w.keys()))}
        total_nodes = {key: total_nodes.get(
            key, 0) + t_n.get(key, 0) for key in set(total_nodes.keys()).union(set(t_n.keys()))}

    combined_list = list1 + list2

    # Combine lists and sort by values in descending order
    sorted_combined_list = sorted(
        combined_list, key=lambda x: total_weight.get(x, 0), reverse=False)

    # Take the top 100 pairs and append a string based on the source list
    top_100_pairs = sorted_combined_list[:100]

    result_list = []
    for item in top_100_pairs:
        if item in list1:
            result_list.append((item, "overlap"))
        else:
            result_list.append((item, "disjoint"))

    return result_list


def compare(hydra, base_node, compare_node):
    base_node_children = asyncio.run(get_children_recursive(hydra, base_node))
    compare_node_children = asyncio.run(
        get_children_recursive(hydra, compare_node))
    overlap_set, disjoint_set = overlap_and_disjoint(
        base_node_children, compare_node_children)
    overlap_list = list(overlap_set)
    disjoint_list = list(disjoint_set)
    return (overlap_list, disjoint_list)


def temp(project_name, hydra, jobset):
    total_weight, total_nodes, _, _, _ = cache_utils.get_cached_or_compute_dependency_weight(
        project_name, jobset, dependency_weight_cache, hydra, calculate_dependency_weight)
    return total_weight, total_nodes

# BUG: I think that when there is a new jobset at least the reverse dependencies gets messed up bc of update_dicts_cache


def main():

    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    # Example: Pushing a jobset
    project_name = "v2-32-devel"


if __name__ == "__main__":
    main()
