from cache_directories import *
import datetime
from write_to_file import write_list_to_file, write_dict_to_file, write_layer_to_file
from hydra_client import Hydra
from new_get_recursive_dependencies import get_recursive_dependencies
from traverse_jobset import traverse_jobset
from new_calculate_entropy import get_cached_or_fetch_store_path_entropy_dict
from topological_sort import topological_sort_until_all_packages
import re
import cache_utils
from sum_dicts import sum_dicts_of_lists
from job_whitelist import job_whitelist
from itertools import combinations
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path
from layering_sanity_check import layering_sanity_check
from get_sorted_jobsets import get_sorted_jobsets
import json
import time
from merge_dicts_with_preference import merge_dicts_with_preference


def split_dict_by_value(my_dict, entropy_dict, target_value):
    matching_values = {}
    non_matching_values = {}

    for key in my_dict:
        if key.split('-', 1)[1] in entropy_dict:
            matching_values[key] = my_dict[key]
        else:
            non_matching_values[key] = my_dict[key]

    return matching_values, non_matching_values


def generate_layers(hydra, update_progress, number_of_layers=10, not_sure=5, project_name="v2-32-devel"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    jobset = sorted_jobsets[-2]
    recursive_dependencies_dict = get_recursive_dependencies(
        hydra, update_progress, project_name, jobset, traverse_jobset)

    print(
        f"len(recursive_dependencies_dict): {len(recursive_dependencies_dict)}")

    # recursive_dependencies_dict = get_recursive_dependencies_cache[jobset]

    write_dict_to_file(recursive_dependencies_dict,
                       "full_recursive_dependencies_dict", "output_files", timestamp)

    if False:
        store_path_entropy_dict = get_cached_or_fetch_store_path_entropy_dict(
            hydra, "v2-32-devel", approximate_uncalculated_jobsets_mode_enabled=True)

    else:
        dependency_all_store_path_dict = cache_utils.general_cache_function(hydra, update_progress, "v2-32-devel", traverse_jobset, dependency_all_store_path_dict_cache,
                                                                            cache_utils.update_dependency_all_store_path_dict, False, False, True, True, "Finding all store paths for packages", None, sum_dicts_of_lists)[0]
        store_path_entropy_dict = cache_utils.get_basic_entropy(
            dependency_all_store_path_dict)

    write_dict_to_file(store_path_entropy_dict, "entropy",
                       "output_files", timestamp)

    write_list_to_file(list(recursive_dependencies_dict.keys()),
                       "keys", "output_files", timestamp)

    test = recursive_dependencies_dict
    other_test = []
    recursive_dependencies_dict = {}

    for item in test:
        key = item.split('-', 1)[1]

        # Define a regular expression pattern to match timestamps
        timestamp_pattern = r'\d{14}'

        # Replace timestamps in both strings with an empty string
        str_without_timestamp = re.sub(timestamp_pattern, '', key)
        if str_without_timestamp not in other_test:
            other_test.append(str_without_timestamp)
            recursive_dependencies_dict[item] = test[item]

    sorted_recursive_dependencies_dict = dict(sorted(recursive_dependencies_dict.items(
    ), key=lambda x: store_path_entropy_dict.get(x[0].split('-', 1)[1], 0)))

    non_zero_entropy_packages, zero_entropy_packages = split_dict_by_value(
        sorted_recursive_dependencies_dict, store_path_entropy_dict, 0)

    mike = list(zero_entropy_packages.keys())

    write_dict_to_file(zero_entropy_packages, "mike",
                       "output_files", timestamp)

    write_list_to_file(mike, "mike2", "output_files", timestamp)

    return _generate_layers(hydra, update_progress, non_zero_entropy_packages, timestamp,
                            number_of_layers, not_sure, project_name, jobset)


def _generate_layers(hydra, update_progress, recursive_dependencies_dict, timestamp, number_of_layers, not_sure, project_name, jobset):

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    # adjusting the user input which is at minimum 1 and at maximum 10 such that 1 corresponds to the highest combination_length_sum possible
    # and 10 the lowest
    if (sorted_jobsets, "fgasgfwsg") in _generate_layers_cache:
        (low, high) = _generate_layers_cache[sorted_jobsets, "fgasgfwsg"]
    else:
        low = None
        high = None
        for x in range(1000):
            z = x*0.15
            layers = __generate_layers(
                hydra, update_progress, recursive_dependencies_dict, timestamp, 10, z, project_name, jobset)
            combination_length_sum = 0
            for layer in layers:
                # print(f"len(layer[0]): {len(layer[0])}, layer[0]: {layer[0]}")
                combination_length = len(layer[0])
                combination_length_sum = combination_length_sum + combination_length
                # 13 is the lowest combination_length sum possible with 10 layers
            if combination_length_sum != 20 and low is None:
                low = z-0.15
                print(
                    f"low: {low} combination_length_sum: {combination_length_sum}")
                # 59 is the highest combination_length sum possible with 10 layers
            if combination_length_sum >= 59:
                high = z
                print(
                    f"high: {high} combination_length_sum: {combination_length_sum}")
                break
            # print(f"combination_length_sum: {combination_length_sum}")
        _generate_layers_cache[(sorted_jobsets, "fgasgfwsg")] = (low, high)

    factor = low+(10-not_sure)*((high-low)/9)

    return __generate_layers(hydra, update_progress, recursive_dependencies_dict, timestamp, number_of_layers, factor, project_name, jobset)


def reduce_package_list(recursive_dependencies_dict, non_zero_entropy_packages):
    _non_zero_entropy_packages = {}
    for key in non_zero_entropy_packages:
        if key in recursive_dependencies_dict:
            _non_zero_entropy_packages[key] = recursive_dependencies_dict[key]
    reduced_package_list = topological_sort_until_all_packages(
        recursive_dependencies_dict, non_zero_entropy_packages)

    print(f"reduced_package_list: {len(reduced_package_list)}")

    if not layering_sanity_check(non_zero_entropy_packages, reduced_package_list, recursive_dependencies_dict):
        print(f"LAYERING SANITY CHECK FAILED, PROGRAM IS BROKEN!")
    
    return reduced_package_list


def __generate_layers(hydra, update_progress, recursive_dependencies_dict, timestamp, number_of_layers, not_sure, project_name, jobset):
    output_directory = "output_files"

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    write_dict_to_file(recursive_dependencies_dict,
                       "recursive_dependencies_dict", output_directory, timestamp)

    # Convert to list to avoid modifying the dictionary during iteration
    for key in list(recursive_dependencies_dict.keys()):
        if key in recursive_dependencies_dict:
            try:
                recursive_dependencies_dict[key] = [
                    neighbor for neighbor in recursive_dependencies_dict[key] if neighbor in recursive_dependencies_dict]
            except Exception as e:
                recursive_dependencies_dict[key] = []

    if False:
        store_path_entropy_dict = get_cached_or_fetch_store_path_entropy_dict(
            hydra, "v2-32-devel", approximate_uncalculated_jobsets_mode_enabled=True)

    else:
        dependency_all_store_path_dict = cache_utils.general_cache_function(hydra, update_progress, "v2-32-devel", traverse_jobset, dependency_all_store_path_dict_cache,
                                                                            cache_utils.update_dependency_all_store_path_dict, False, False, True, True, "Finding all store paths for packages", None, sum_dicts_of_lists)[0]
        store_path_entropy_dict = cache_utils.get_basic_entropy(
            dependency_all_store_path_dict)

    print(
        f"len(recursive_dependencies_dict): {len(recursive_dependencies_dict)}")

    result = []
    layer_count = 0
    iteration = 0
    base = None
    selected_combinations_list = []
    threshold = 0
    # TODO: take stuff out of while loop
    while layer_count < number_of_layers:
        iteration = iteration+1

        job_overhead_dict = {}
        combination_lengths = [1, 7, 6, 5, 4, 3, 2]
        for combination_length in combination_lengths:
            if combination_length == 1 and iteration != 1:
                continue
            combinations_list = list(combinations(
                job_whitelist, combination_length))
            for combination in reversed(combinations_list):
                if layer_count == number_of_layers:
                    return result
                # if combination_length != 1 and (sorted_jobsets, combination) in _generate_layers_cache:
                if (sorted_jobsets, combination) in _generate_layers_cache:
                    (overhead, reduced_package_list) = _generate_layers_cache[(
                        sorted_jobsets, combination)]
                    if combination_length == 1:
                        job_overhead_dict[combination[0]] = overhead

                else:
                    combination_recursive_dependencies = get_recursive_dependencies(
                        hydra, update_progress, "v2-32-devel", jobset, traverse_jobset, jobs=combination)

                    # print(f"{combination}, len(combination_recursive_dependencies): {len(combination_recursive_dependencies)}")
                    non_zero_entropy_packages, _ = split_dict_by_value(
                        combination_recursive_dependencies, store_path_entropy_dict, 0)

                    print(
                        f"non_zero_entropy_packages len: {len(non_zero_entropy_packages)}")

                    _non_zero_entropy_packages = {}
                    for key in non_zero_entropy_packages:
                        if key in recursive_dependencies_dict:
                            _non_zero_entropy_packages[key] = recursive_dependencies_dict[key]
                    non_zero_entropy_packages = _non_zero_entropy_packages

                    reduced_package_list = topological_sort_until_all_packages(
                        recursive_dependencies_dict, non_zero_entropy_packages)
                    # reduced_package_list = list(non_zero_entropy_packages.keys())
                    print(f"reduced_package_list: {len(reduced_package_list)}")
                    # return

                    if not layering_sanity_check(non_zero_entropy_packages, reduced_package_list, recursive_dependencies_dict):
                        print(f"LAYERING SANITY CHECK FAILED, PROGRAM IS BROKEN!")
                        return

                    overhead = 0
                    if combination_length == 1:
                        # this should be done recursively
                        # switched this from reduced_package_list
                        ddd = [item for item in list(
                            recursive_dependencies_dict.keys()) if item not in non_zero_entropy_packages]
                        for item in ddd:
                            _, file_size = get_references_and_file_size_from_store_path(
                                hydra, item)
                            overhead += file_size
                        job_overhead_dict[combination[0]] = overhead
                        _generate_layers_cache[(sorted_jobsets, combination)] = (
                            overhead, reduced_package_list)

                    else:
                        for job in combination:
                            overhead += job_overhead_dict[job]
                    _generate_layers_cache[(sorted_jobsets, combination)] = (
                        overhead, reduced_package_list)
                if combination_length == 1:
                    if base is None:
                        base = overhead
                    # we want to go through the combination_length == 1 combinations first to calculate the job_overhead_dict but then consider the combinations
                    # in descending order of combination length such that if two different combinations both meet the same threshold, the one of higher combination
                    # length will be looked at first
                    if iteration == 1:
                        continue
                threshold = base/2 + combination_length * \
                    base*(not_sure)/(2.5) + iteration*base*.1
                if overhead < threshold and combination not in selected_combinations_list:
                    layer_count = layer_count + 1
                    selected_combinations_list.append(combination)

                    print(
                        f"{combination}, {len(combination)}: {overhead/100000000}, reduced from {len(recursive_dependencies_dict)} to {len(reduced_package_list)}")
                    layer_info = (combination, overhead, reduced_package_list)
                    result.append(layer_info)
                    write_layer_to_file(
                        combination, overhead, reduced_package_list, "output_files/layers", layer_count, timestamp)

    return result


def main():

    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")
    thing = generate_layers(hydra, 10, 5)
    sum = 0
    for t in thing:
        sum = sum + len(t[0])
    print(f"sum={sum}")
    thing = generate_layers(hydra, 10, 1)
    sum = 0
    for t in thing:
        sum = sum + len(t[0])
    print(f"sum={sum}")
    thing = generate_layers(hydra, 10, 10)
    sum = 0
    for t in thing:
        sum = sum + len(t[0])
    print(f"sum={sum}")
    return
    low = None
    high = None
    for x in range(1000):
        z = 2+x*0.1
        # if x < 16:
        #     continue
        y = 4.0+(10-x)*((7.1-5.4)/10)
        thing = generate_layers(hydra, 10, z)
        print(f"not_sure={z}")
        sum = 0
        for t in thing:
            sum = sum + len(t[0])
        print(f"sum={sum}")
        if sum != 13 and low is None:
            low = z
        if sum >= 59:
            high = z
            break
    print(f"low: {low}, high: {high}")


if __name__ == '__main__':
    main()
