from hydra_client import Hydra
from hydra_client import HydraResponseException
from diskcache import Cache
from datetime import datetime
from has_timestamp import has_timestamp
from raw_data_utilities import extract_section
import utils
import cache_utils
import string
import asyncio
import concurrent.futures

#TODO: break this up into multiple caches
my_cache_directory = "cache/my_cache_directory"
my_out_path_cache_directory = "cache/my_out_path_cache_directory"
job_cache_directory = "cache/job_cache_directory"
jobset_cache_directory = "cache/jobset_cache_directory"
builds_cache_directory = "cache/builds_cache_directory"
evals_info_cache_directory = "cache/evals_info_cache_directory"
first_sort_cache_directory = "cache/first_sort_cache_directory"
jobset_evals_cache_directory = "cache/jobset_evals_cache_directory"
build_info_cache_directory = "cache/build_info_cache_directory"
nar_info_cache_directory = "cache/nar_info_cache_directory"
count_ancestor_cache_directory = "cache/count_ancestor_cache_directory"
dependency_weight_cache_directory = "cache/dependency_weight_cache_directory"
#TODO: name?
update_dicts_cache_directory = "cache/update_dicts_cache_directory"
cache = Cache(my_cache_directory)
dependency_weight_cache = Cache(dependency_weight_cache_directory)
first_sort_cache = Cache(first_sort_cache_directory)
count_ancestor_cache = Cache(count_ancestor_cache_directory)
jobset_evals_cache = Cache(jobset_evals_cache_directory)
build_info_cache = Cache(build_info_cache_directory)
nar_info_cache = Cache(nar_info_cache_directory, threaded=True)
out_path_cache = Cache(my_out_path_cache_directory)
job_cache = Cache(job_cache_directory)
jobset_cache = Cache(jobset_cache_directory)
evals_info_cache = Cache(evals_info_cache_directory)
builds_cache = Cache(builds_cache_directory)
update_dicts_cache = Cache(update_dicts_cache_directory)

#TODO: break this into multiple methods    
#TODO: same name?
#TODO: dependency tree for packages
def update_hash_tables(job,
                    jobset,
                    dependency,
                    group,
                    store_path_hash_dict,
                    store_path_entropy_dict,
                    store_path_file_size_dict,
                    reverse_dependencies_dict,
                    dependency_all_store_path_dict,
                    store_path_jobsets_dict,
                    file_size):
    input_string = dependency
    # Removing "/nix/store" from the beginning of the string
    input_string = input_string[len("/nix/store"):]

    store_path_file_size_dict[dependency] = int(file_size[0])

    if dependency in store_path_jobsets_dict:
        for store_path in group:
            if store_path in store_path_jobsets_dict[dependency]:
                if jobset not in store_path_jobsets_dict[dependency][store_path]:
                    store_path_jobsets_dict[dependency][store_path].append(jobset)
            else:
                # If store_path is not in the dictionary, create a new entry
                store_path_jobsets_dict[dependency][store_path] = [jobset]
    else:
        # If dependency is not in the dictionary, create a new entry
        store_path_jobsets_dict[dependency] = {}
        for store_path in group:
            if store_path in store_path_jobsets_dict[dependency]:
                if jobset not in store_path_jobsets_dict[dependency][store_path]:
                    store_path_jobsets_dict[dependency][store_path].append(jobset)
            else:
                # If store_path is not in the dictionary, create a new entry
                store_path_jobsets_dict[dependency][store_path] = [jobset]


    if dependency in dependency_all_store_path_dict:
        dependency_all_store_path_dict[dependency] = list(set(dependency_all_store_path_dict[dependency]) | set(group))
    else:
        dependency_all_store_path_dict[dependency] = group

    # TODO: change this so that it also has the versions of the job
    if dependency in reverse_dependencies_dict:
        if job in reverse_dependencies_dict[dependency]:
            reverse_dependencies_dict[dependency][job].append(jobset)
        else:
            reverse_dependencies_dict[dependency][job] = [jobset]

    else:
        reverse_dependencies_dict[dependency] = {}
        reverse_dependencies_dict[dependency][job] = [jobset]

    if job in store_path_hash_dict:
        if dependency in store_path_hash_dict[job]:
            if store_path_hash_dict[job][dependency] != group:
                if dependency not in store_path_entropy_dict:
                    store_path_entropy_dict[dependency] = 0
                store_path_entropy_dict[dependency] = store_path_entropy_dict[dependency] + 1                
                store_path_hash_dict[job][dependency] = group
        else:
            # init dicts
            store_path_hash_dict[job][dependency] = group
    else: 
        store_path_hash_dict[job] = {}
        store_path_hash_dict[job][dependency] = group

#TODO: remove dependency_weight_dict from this
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
                              minimum_file_size=0,
                              minimum_entropy=0,
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
    test = 0
    total_weight, weight_key, nodes, count_file_size, total_file_size = asyncio.run(calculate_dependency_weight(project_name, hydra, "v2.32.0-20240124144957-0"))


    # Define a mapping of sort indices to corresponding keys in the combined dictionary
    sort_mapping = {
            'file_size': 0,  # Sort by file size
            'entropy': 1,  # Sort by entropy
            'dependency_weight': 2   # Sort by dependency weight
    }

         # Combine all dictionaries into a single dictionary with keys from file size dict
    combined_dict = {
        key: (store_path_file_size_dict.get(key, 0), store_path_entropy_dict.get(key, 0), weight_key.get(key, 0))
        for key in store_path_file_size_dict
    }
    print(f"minimum_entropy: {minimum_entropy}, minimum_file_size: {minimum_file_size}")

    # Filter out items based on conditions
    filtered_dict = {
        key: (file_size, entropy, dependency_weight) for key, (file_size, entropy, dependency_weight) in combined_dict.items()
        if file_size >= minimum_file_size and entropy >= minimum_entropy
    }

    # with this caching scheme, compute_top_n_information() is O(1) when there is a cache hit (vs. O(n) where n is the number of packages in the project)
    if (filtered_dict, sort_key1) in first_sort_cache:
        # cache hit!
        sorted_items = first_sort_cache[(filtered_dict, sort_key1)]
    else:

        # Sort the combined dictionary items based on the specified sort index
        sorted_items = sorted(filtered_dict.items(), key=lambda x: x[1][sort_mapping.get(sort_key1, 0)], reverse=True)
        first_sort_cache[(filtered_dict, sort_key1)] = sorted_items

     # Choose the sorting order based on user input
    reverse_order = sort_order.lower() == 'desc'

    # Extract the top N values
    top_n_values = sorted_items[:int(n)]

    top_n_values = sorted(top_n_values, key=lambda x: x[1][sort_mapping.get(sort_key2, 0)], reverse=reverse_order)

    top_n_values_dynamic = []

    for iteration, (key, (file_size, entropy, dependency_weight)) in enumerate(top_n_values):
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
            "node_dependency_weight": f"{weight_key.get(key, 0)/nodes}",
            "file_size_dependency_weight": f"{count_file_size.get(key, 0)/nodes}",
            # "file_size_dependency_weight": f"{dependent_nodes_file_size/total_nodes_file_size}",
            "reverse_dependencies": reverse_dependencies_dict[key],
            "last_instance_hash": dependency_store_path_dict[key],
            "store_paths": dependency_all_store_path_dict[key],
            "store_path_jobsets": store_path_jobsets_dict[key],
        }
        if (print_to_console):
            print(output.rstrip (','))
        top_n_values_dynamic.append((key, details))

    return top_n_values_dynamic
                
async def count_ancestors(hydra, node):

    # A
    #   B
    #     D
    #     E
    #   F
    #     G
    #     E
    #   H
    #     I
    #     E

    # if indentation represents the depth, node == A == root and target_value == E, then [A, B, F, H] are the ancestors of the target, and the total_nodes
    # would be [A, B, D, F, G, H, I] (does not include the targets themselves), and the same applies for the file size of the ancestors of the target and
    # the total file size of the nodes

    # **NOTE**: if for whatever reason you wanted to include the target in the numerator and denominator of these fractions, simply remove the -target_count
    # and -target_value_size from the return statements

    if node in count_ancestor_cache:
        # already adjusted
        count, count_key, total_nodes, target_count, total_file_size, count_file_size, target_file_size = count_ancestor_cache[node]
        # count = {key: count.get(key, 0) - target_count[key] for key in target_count}
        count_file_size = {key: count_file_size.get(key, 0) - target_file_size[key] for key in target_file_size}
        return count, count_key, total_nodes, total_file_size, count_file_size
    # not adjusted
    count, count_key, total_nodes, target_count, total_file_size, count_file_size, target_file_size = await _count_ancestors(hydra, node, 0, 0)
    count_ancestor_cache[node] = (count, count_key, total_nodes, target_count, total_file_size, count_file_size, target_file_size)
    # not adjusted, hence adjustments made
    # count = {key: count.get(key, 0) - target_count.get(key, 0) for key in set(target_count.keys()).union(set(count.keys()))}
    count_file_size = {key: count_file_size.get(key, 0) - target_file_size.get(key, 0) for key in set(count_file_size.keys()).union(set(target_file_size.keys()))}
    return count, count_key, total_nodes, total_file_size, count_file_size

def get_children(hydra, hash):

    raw_data = cache_utils.get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash)
    references = extract_section(raw_data=raw_data, keyword="References")
    return references


async def get_children_recursive(hydra, hash, visited=None):
    if visited is None:
        visited = set()

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


import concurrent.futures

def sort_chunk(chunk, project_name, hydra, jobset):
    print(f"sort_chunk!")
    return sorted(chunk, key=lambda item: temp(project_name, hydra, jobset, item), reverse=True)

def parallel_sort(input_list, project_name, hydra, jobset, chunk_size=100):
    chunks = [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda chunk: sort_chunk(chunk, project_name, hydra, jobset), chunks))

    return [item for sublist in results for item in sublist]

def overlap_and_disjoint(set1, set2):
    # Calculate the overlap (intersection) of the two sets
    overlap_set = set1.intersection(set2)

    # Calculate the disjoint elements of the two sets
    disjoint_set = set1.symmetric_difference(set2)

    return overlap_set, disjoint_set

def combine(project_name, hydra, list1, list2, jobsets=["v2.32.0-20240124144957-0"]):

    # Combine the lists based on the top 100 items
    combined_list = []

    total_weight = {}

    total_nodes = {}

    print(f"list1 length: {len(list1)}, list2 length: {len(list2)}")

    for jobset in jobsets:
        t_w, t_n = temp(project_name, hydra, jobset)
        total_weight = {key: total_weight.get(key, 0) + t_w.get(key, 0) for key in set(total_weight.keys()).union(set(t_w.keys()))}
        total_nodes = {key: total_nodes.get(key, 0) + t_n.get(key, 0) for key in set(total_nodes.keys()).union(set(t_n.keys()))}

    # Perform parallel sorting
    # list1_sorted = sorted(list1, key=lambda item: total_weight.get(item, 0)/total_nodes.get(item, 0), reverse=True)
    # list2_sorted = sorted(list2, key=lambda item: total_weight.get(item, 0)/total_nodes.get(item, 0), reverse=True)
    # list1_sorted = sorted(list1, key=lambda item: total_weight.get(item, 0), reverse=True)
    # list2_sorted = sorted(list2, key=lambda item: total_weight.get(item, 0), reverse=True)
        
    combined_list = list1 + list2

    # Combine lists and sort by values in descending order
    sorted_combined_list = sorted(combined_list, key=lambda x: total_weight.get(x, 0), reverse=False)

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
    compare_node_children = asyncio.run(get_children_recursive(hydra, compare_node))
    overlap_set, disjoint_set = overlap_and_disjoint(base_node_children, compare_node_children)
    overlap_list = list(overlap_set)
    disjoint_list = list(disjoint_set)
    return (overlap_list, disjoint_list)
    
async def _count_ancestors(hydra, package, current_depth, max_depth):

    count = {}
    count_key = {}
    total_nodes = 0  # New variable to keep track of total nodes
    total_file_size = {}  # New variable to keep track of total file size
    count_file_size = {}  # New variable to keep track of count file size
    target_count = {}
    t = {}
    target_file_size = {}

    parts = package.split('-', 1)
    hash_value = parts[0]
    key = parts[1]

    raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
    references = extract_section(raw_data=raw_data, keyword="References")
    file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])
   
    total_nodes += 1 
    if package not in total_file_size:
        total_file_size[package] = 0   
    total_file_size[package] += file_size

    if package is not None:
        if package not in count:
            count[package] = 0
        count[package]+= 1
        if key not in count_key:
            count_key[key] = 0
        count_key[key]+= 1
        if package not in count_file_size:
            count_file_size[package] = 0
        count_file_size[package] += file_size
        if package not in target_count:
            target_count[package] = 0
        target_count[package] += 1
        if package not in target_file_size:
            target_file_size[package] = 0
        target_file_size[package] += file_size

        for child in references:
            if child != package:
                print(f"depth: {current_depth}, child: {child}, package: {package}")
                if child in count_ancestor_cache:
                    c, ck, nodes, t, size, count_size, t_file_size = count_ancestor_cache[child]
                else:
                    c, ck, nodes, t, size, count_size, t_file_size = await _count_ancestors(hydra, child, current_depth+1, max_depth)
                    count_ancestor_cache[child] = (c, ck, nodes, t, size, count_size, t_file_size)
                count = {key: count.get(key, 0) + c.get(key, 0) for key in set(count.keys()).union(set(c.keys()))}
                count_key = {key: count_key.get(key, 0) + ck.get(key, 0) for key in set(count_key.keys()).union(set(ck.keys()))}
                total_nodes += nodes
                total_file_size = {key: total_file_size.get(key, 0) + size.get(key, 0) for key in set(total_file_size.keys()).union(set(size.keys()))}
                target_file_size = {key: target_file_size.get(key, 0) + t_file_size.get(key, 0) for key in set(target_file_size.keys()).union(set(t_file_size.keys()))}
                count_file_size = {key: count_file_size.get(key, 0) + count_size.get(key, 0) for key in set(count_file_size.keys()).union(set(count_size.keys()))}
                target_count = {key: target_count.get(key, 0) + t.get(key, 0) for key in set(target_count.keys()).union(set(target_count.keys()))}

        for x in count:
            #TODO: change that to ==
            if count[x] > 0 and x not in package:
                count[x] += 1  # Increment count for the current node (ancestor)
                count_key[key] += 1
                count_file_size[x] += file_size

    return count, count_key, total_nodes, target_count, total_file_size, count_file_size, target_file_size  # Return count of ancestors, total node count, total file size, and count file size

# async def _count_ancestors(hydra, package, target, current_depth, max_depth):

#     if current_depth > max_depth:
#         # Reached maximum recursion depth, return appropriate values
#         return 0, 0, 0, 0, 0, 0
#     count = 0
#     total_nodes = 0  # New variable to keep track of total nodes
#     total_file_size = 0  # New variable to keep track of total file size
#     count_file_size = 0  # New variable to keep track of count file size
#     target_count = 0
#     t = 0
#     target_file_size = 0

#     parts = package.split('-', 1)
#     hash_value = parts[0]

#     raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
#     references = extract_section(raw_data=raw_data, keyword="References")
#     file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])

#     total_nodes += 1
#     total_file_size += file_size

#     if package is not None:
#         if target in package:
#             count += 1
#             count_file_size += file_size
#             target_count += 1
#             target_file_size += file_size
#             return count, total_nodes, target_count, total_file_size, count_file_size, target_file_size

#         for child in references:
#             if child != package:
#                 print(f"depth: {current_depth}, child: {child}, package: {package}")
#                 if (child, target) in count_ancestor_cache:
#                     c, nodes, t, size, count_size, t_file_size = count_ancestor_cache[(child, target)]
#                 else:
#                     c, nodes, t, size, count_size, t_file_size = await _count_ancestors(hydra, child, target, current_depth+1, max_depth)
#                     count_ancestor_cache[(child, target)] = (c, nodes, t, size, count_size, t_file_size)
#                 count += c
#                 total_nodes += nodes  # Move this line inside the loop but outside the condition
#                 total_file_size += size
#                 count_file_size += count_size
#                 target_count += t
#                 target_file_size += t_file_size

#         if count > 0 and target not in package:
#             count += 1  # Increment count for the current node (ancestor)
#             count_file_size += file_size

#     return count, total_nodes, target_count, total_file_size, count_file_size, target_file_size  # Return count of ancestors, total node count, total file size, and count file size

async def calculate_dependency_weight(project_name, hydra, jobset):
    if jobset in dependency_weight_cache:
        # cache hit!
        return dependency_weight_cache[jobset]

    weight = {}
    weight_key = {}
    nodes = {}
    total_weight = {}
    total_weight_key = {}
    total_nodes = 0
    total_file_size = {}
    count_file_size = {}
    total_total_file_size = {}
    total_count_file_size = {}
    missed_hash = False

    data = cache_utils.get_cached_or_fetch_jobset_evals(hydra, jobset_evals_cache, project_name, jobset)

    evals_info = data.get('evals', [])

    for eval_info in evals_info:
        builds = eval_info.get('builds', [])

        for build in builds:
            references = []
            build_info = cache_utils.get_cached_or_fetch_build_info(hydra, build_info_cache, build)
            out_path = build_info.get('outPath', [])
            try:
                input_string = out_path
                input_string = input_string[len("/nix/store/"):]
                parts = input_string.split('-', 1)
                hash_value = parts[0]

                # Separate awaits for each coroutine call
                raw_data = await cache_utils.async_get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
                try:
                    references = extract_section(raw_data=raw_data, keyword="References")
                except AttributeError as e:
                    print(f"raw data: :{raw_data}")
            except HydraResponseException as e:
                print(f"missed hash ({hash_value})")
                missed_hash = True
                continue
            # except Exception as e:
            #     print(f"failed to retrieve direct dependencies of build: {build} with error: {e}")

            for dependency in references:
                if dependency in out_path:
                    continue
                # Separate await for the coroutine call
                weight, weight_key, nodes, total_file_size, count_file_size = await count_ancestors(hydra, dependency)
                total_weight = {key: total_weight.get(key, 0) + weight.get(key, 0) for key in set(total_weight.keys()).union(set(weight.keys()))}
                total_weight_key = {key: total_weight_key.get(key, 0) + weight_key.get(key, 0) for key in set(total_weight_key.keys()).union(set(weight_key.keys()))}
                total_nodes += nodes
                total_total_file_size = {key: total_total_file_size.get(key, 0) + total_file_size.get(key, 0) for key in set(total_total_file_size.keys()).union(set(total_file_size.keys()))}
                total_count_file_size = {key: total_count_file_size.get(key, 0) + count_file_size.get(key, 0) for key in set(total_count_file_size.keys()).union(set(count_file_size.keys()))}

        if not missed_hash:
            dependency_weight_cache[jobset] = total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size

    return total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size


    
def temp(project_name, hydra, jobset):
    total_weight, total_nodes, _, _, _ = asyncio.run(calculate_dependency_weight(project_name, hydra, jobset))
    return total_weight, total_nodes
                    
# notes: 
        # - FileSize equals NarSize in the narinfo and the numbers seem suspicious?
        # - packages with two of the same dependency with different hashes? --> throw out

#BUG: I think that when there is a new jobset at least the reverse dependencies gets messed up bc of update_dicts_cache
def mike(project_name: string, hydra: Hydra):
    # store_path_hash_dict[x][y] where y is the hash of a direct dependency of x
    store_path_hash_dict = {}

    # store_path_entropy_dict[x] is incremented when the hash for x changes
    store_path_entropy_dict = {}

    # store_path_file_size_dict[x] is the file size of a store path of a build
    store_path_file_size_dict = {}

    # every item in reverse_dependencies_dict[x] reverse DIRECTLY depends on x 
    reverse_dependencies_dict = {}

    # dependency_store_path_dict[x] is the last instance of a store path for a dependency x
    dependency_store_path_dict = {}

    # all store paths for x
    dependency_all_store_path_dict = {}

    # all jobsets containing x
    store_path_jobsets_dict = {}

    missed_hash = False

    # Initialize variables to store the result
    remaining_jobsets = []

    print(f"Generating a list of the 100 largest store paths sorted by entropy in project: {project_name}")

    # ['v2.32.0-20240102033847-0', 'v2.32.0-20240102144952-0', 'v2.32.0-20240102154952-0',...
    jobsets = hydra.get_jobsets(project=project_name)

    total_jobsets = len(jobsets)
    bar_length = 20

    # Assuming jobsets is a list of strings containing timestamps
    sorted_jobsets = sorted(jobsets, key=lambda x: datetime.strptime(x.split('-')[1], '%Y%m%d%H%M%S'))
    earliest_jobset = sorted_jobsets[0]

    if sorted_jobsets in update_dicts_cache:
        # cache hit;
        pass
        return update_dicts_cache[sorted_jobsets]

    # Iterate in reverse order
    # for n in range(len(sorted_jobsets), 0, -1):
    #     prefix = sorted_jobsets[:n]
    #     matching_sublist = next((lst for lst in update_dicts_cache if prefix == lst[:len(prefix)]), None)
    #     if matching_sublist is not None:
    #         result_n = n
    #         remaining_jobsets = sorted_jobsets[result_n:]
    #         break

    # print("The highest value of n is:", result_n)
    # print("Remaining elements:", remaining_jobsets)
    # print("Matching sublist in my_second_list:", matching_sublist)
    
    # if (matching_sublist is not None) and matching_sublist in update_dicts_cache:
    #     # partial cache hit!
    #     (store_path_entropy_dict,
    #     store_path_file_size_dict,
    #     reverse_dependencies_dict,
    #     dependency_store_path_dict,
    #     dependency_all_store_path_dict,
    #     earliest_jobset,
    #     latest_jobset) = update_dicts_cache[matching_sublist]

    # else: 
    remaining_jobsets = sorted_jobsets

    for idx, jobset in enumerate(remaining_jobsets):
        utils.print_progress_update(idx, total_jobsets, bar_length)
        data = cache_utils.get_cached_or_fetch_jobset_evals(hydra, jobset_evals_cache, project_name, jobset)
        # Access builds information
        evals_info = data.get('evals', [])

        for eval_info in evals_info:
            builds = eval_info.get('builds', [])

            # [487521, 487524, 487530, 487554,...
            for build in builds:
                build_info = cache_utils.get_cached_or_fetch_build_info(hydra, build_info_cache, build)
                out_path = build_info.get('outPath', [])
                job = build_info.get('job', [])
                try:
                    input_string = out_path
                    # Removing "/nix/store" from the beginning of the string
                    input_string = input_string[len("/nix/store/"):]

                    # Splitting the string based on the first hyphen
                    parts = input_string.split('-', 1)

                    # Extracting the hash and the stuff after the first hyphen
                    hash_value = parts[0]
                    raw_data = cache_utils.get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
                    references = extract_section(raw_data=raw_data, keyword="References")
                    file_size = extract_section(raw_data=raw_data, keyword="FileSize")
                except HydraResponseException as e:
                    print(f"missed hash ({hash_value})")
                    missed_hash = True
                    continue
                except Exception as e:
                    print(f"failed to retrieve direct dependencies of build: {build} with error: {e}")
                
                grouped_items = {}
                for dependency in references:
                    # Group items based on the equality of the second part after splitting by '-'
                    parts = dependency.split('-', 1)
                    hash = parts[0]
                    key = parts[1] if len(parts) > 1 else dependency  # Using the second part as the grouping criterion
                    grouped_items.setdefault(key, []).append(dependency)
                    dependency_store_path_dict[key] = hash

                for key, group in grouped_items.items():

                    # temporary measure against weird timestamp packages
                    if has_timestamp(dependency):
                        continue
                    update_hash_tables(job,
                                       jobset,
                                       key,
                                       group,
                                       store_path_hash_dict,
                                       store_path_entropy_dict,
                                       store_path_file_size_dict,
                                       reverse_dependencies_dict,
                                       dependency_all_store_path_dict,
                                       store_path_jobsets_dict,
                                       file_size)
        #TODO: ???
        latest_jobset = sorted_jobsets[-1]
                    
    # populate cache
    update_dicts_cache[sorted_jobsets] = (store_path_entropy_dict, 
                                        store_path_file_size_dict, 
                                        reverse_dependencies_dict,
                                        dependency_store_path_dict,
                                        dependency_all_store_path_dict,
                                        store_path_jobsets_dict,
                                        earliest_jobset,
                                        latest_jobset)
    
    return (store_path_entropy_dict,
            store_path_file_size_dict,
            reverse_dependencies_dict,
            dependency_store_path_dict,
            dependency_all_store_path_dict,
            store_path_jobsets_dict,
            earliest_jobset,
            jobsets)
                    
def main():
    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    # Example: Pushing a jobset
    project_name = "v2-32-devel"

    mike(project_name=project_name,hydra=hydra)

if __name__ == "__main__":
    main()

