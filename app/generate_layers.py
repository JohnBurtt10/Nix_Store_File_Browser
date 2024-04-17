import copy
from .calculate_overhead import calculate_overhead
from .update_accounted_for_packages import update_accounted_for_packages
from .get_file_size_from_store_path import get_file_size_from_store_path
from .cache_directories import *
from .new_get_recursive_dependencies import get_recursive_dependencies
from .traverse_jobset import traverse_jobset
from .job_whitelist import job_whitelist
from itertools import combinations
from .get_sorted_jobsets import get_sorted_jobsets
from .get_file_sizes_by_path import get_file_sizes_by_path
from .fetch_and_compare_nix_paths import fetch_and_compare_nix_paths
from datetime import datetime
from .cancel_operation import file_exists
from .list_operations import check_intersection, remove_common_elements
from .n_choose_k_count import n_choose_k_count
from .split_dict_by_value import split_dict_by_value
from .populate_references_and_file_sizes import populate_references_and_file_sizes
from .send_layers import send_layers


def strip_hash(string):
    return string.split('-', 1)[1]


def get_recursive_dependency_weight(package, recursive_dependencies_dict, package_file_size):
    recursive_dependency_weight = 0
    recursive_dependency_weight += package_file_size.get(package, 0)
    for item in recursive_dependencies_dict.get(package, []):
        recursive_dependency_weight += package_file_size.get(item, 0)

    return recursive_dependency_weight


def get_true_recursive_file_size(hydra, layer, recursive_dependencies_dict):
    true_recursive_file_size = 0

    for package in layer['packages']:
        true_recursive_file_size += get_file_size_from_store_path(
            hydra, package)
        for item in recursive_dependencies_dict[package]:
            true_recursive_file_size += get_file_size_from_store_path(
                hydra, item)
    return true_recursive_file_size


def generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress,
                    minimum_layer_recursive_file_size, maximum_layer_recursive_file_size,
                    start_date, end_date, session_id, project_name="v2-34-devel"):

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)
    jobset = sorted_jobsets[0]

    if False and (jobset, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, start_date, end_date) in generate_layers_cache:
        answer, recursive_dependencies_dict = generate_layers_cache[(
            jobset, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, start_date, end_date)]

        if jobset in package_file_size_cache:

            package_file_size, unique_packge_world_file_size = package_file_size_cache[jobset]

        else:
            package_file_size, unique_packge_world_file_size = get_file_sizes_by_path(
                recursive_dependencies_dict, hydra, recursive_dependencies_dict)

            package_file_size_cache[jobset] = package_file_size, unique_packge_world_file_size

    else:

        if (jobset, "fgl0wfl") in cache:

            references_dict, file_size_dict = cache[(jobset, "fgl0wfl")]
        else:

            references_dict = {}

            file_size_dict = {}

            visited = {}

            traverse_jobset(hydra, lambda: None, lambda: None, project_name, jobset,
                            lambda job, raw_data: populate_references_and_file_sizes(
                                raw_data, references_dict, file_size_dict, jobset, job),
                            only_visit_once_enabled=True,
                            recursive_mode_enabled=True,
                            whitelist_enabled=False,
                            exponential_back_off_enabled=False,
                            visited=visited,
                            cancellable=True,
                            unique_packages_enabled=False)
            cache[(jobset, "fgl0wfl")] = references_dict, file_size_dict

        recursive_dependencies_dict = get_recursive_dependencies(
            hydra, update_progress, report_error, project_name, jobset, traverse_jobset, unique_packages_enabled=True, references_dict=references_dict,
            file_size_dict=file_size_dict)

        if False and jobset in package_file_size_cache:

            package_file_size, unique_packge_world_file_size = package_file_size_cache[jobset]

        else:
            package_file_size, unique_packge_world_file_size = get_file_sizes_by_path(
                recursive_dependencies_dict, hydra, recursive_dependencies_dict)

            package_file_size_cache[jobset] = package_file_size, unique_packge_world_file_size

        answer, _ = __generate_layers(hydra, update_progress, report_error,
                                      send_layer, update_layer_progress,
                                      project_name, jobset, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, package_file_size, session_id, start_date, end_date)

        generate_layers_cache[(jobset, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size,
                               start_date, end_date)] = answer, recursive_dependencies_dict
    job_layer_dict = {}

    # TODO: merge layers?
    for (combination, is_creating_zero_entropy_layers, i), value in answer.items():
        value['is_creating_zero_entropy_layers'] = is_creating_zero_entropy_layers
        for job in combination:
            if job in job_layer_dict:
                job_layer_dict[job].append(value)
            else:
                job_layer_dict[job] = [value]

    containerData = {}

    for job, layers in job_layer_dict.items():
        # Sorting the dictionary of dictionaries based on 'total_recursive_file_size'
        # 0 has the lowest total_recursive_file_size since we want to create a layer with stuff at the bottom of the tree first then create
        # the next layer based on everything but what's included in layer 0 and so on...
        sorted_data = sorted(layers, key=lambda x: get_true_recursive_file_size(
            hydra, x, recursive_dependencies_dict))
        # keeping track of the packages accounted for by all the partitions up to the current one
        previous_partition_packages = set()
        # keeping track of the packages accounted for by the current partition
        current_partition_packages = set()
        containerData[job] = []
        partition_count = 0
        # if package_partition_dict[x] = y, then layer x (using the 'packages' field as index) is in partition y
        package_partition_dict = {}

        # if for example, the order of layers 1-3 is interchangable, then that is a partition where the start index is 1 and the end index is 3
        partition_start_end_index = {}

        partition_start_end_index[0] = {'smallest': 0}

        # once layer n requires a layer in the current partition, the current partition is closed and a new one is started with layer n
        for index, layer in enumerate(sorted_data):
            layer['total_recursive_file_size'] = get_true_recursive_file_size(
                hydra, layer, recursive_dependencies_dict)
            first_item = next(iter(layer['packages']))
            packages = set(recursive_dependencies_dict[first_item]).union(
                {first_item})
            new = packages.difference(previous_partition_packages)
            previous_partition_packages = packages.union(
                previous_partition_packages)
            if not packages.issubset((current_partition_packages.union(new))):
                current_partition_packages = previous_partition_packages
                partition_start_end_index[partition_count]['largest'] = index-1
                partition_count += 1
                partition_start_end_index[partition_count] = {}
                partition_start_end_index[partition_count]['smallest'] = index
            package_partition_dict[str(layer['packages'])] = partition_count
            sum = 0
            for item in new:
                sum += get_file_size_from_store_path(hydra, item)
            layer['new_file_size_layer_wise'] = sum

            sorted_accounted_for_packages = sorted(list(new), key=lambda x: get_recursive_dependency_weight(
                x, recursive_dependencies_dict, package_file_size))

            sorted_accounted_for_packages = [
                item for item in sorted_accounted_for_packages if "ros" in item]

            layer['accounted_for_packages'] = sorted_accounted_for_packages

            new_data_magnitude = str(round(sum/(1024 * 1024), 2))

            layer['new_data_magnitude'] = new_data_magnitude

            total_recursive_file_size_magnitude = str(
                round(layer['total_recursive_file_size']/(1024 * 1024), 2))

            layer['total_recursive_file_size_magnitude'] = total_recursive_file_size_magnitude

        partition_start_end_index[partition_count]['largest'] = len(
            sorted_data)-1

        for index, layer in enumerate(sorted_data):
            first_item = next(iter(layer['packages']))

            first_item_file_size = str(
                round(package_file_size[first_item]/(1024 * 1024), 2))

            stripped_packages = [strip_hash(
                item) for item in layer['accounted_for_packages']]

            if partition_start_end_index[package_partition_dict[str(layer['packages'])]]['smallest'] == partition_start_end_index[package_partition_dict[str(layer['packages'])]]['largest']:
                layer_string = str(
                    partition_start_end_index[package_partition_dict[str(layer['packages'])]]['smallest'])
            else:
                layer_string = str(partition_start_end_index[package_partition_dict[str(layer['packages'])]]['smallest']) + '-' + str(
                    partition_start_end_index[package_partition_dict[str(layer['packages'])]]['largest'])

            containerData[job].append({'layer': 'Layer ' + layer_string, 'packages': [first_item], 'packageFileSize': first_item_file_size + 'MB', 'newData': layer['new_data_magnitude'] +
                                      'MB', 'accountedForPackages': stripped_packages, 'totalRecursiveFileSize': layer['total_recursive_file_size_magnitude'] + 'MB'})

    return containerData

    # break

# This is not used for now, but may be in the future (see More Sophisticated Entropy Calculation in the Road Map section of the README)


def find_highest_average_package_combination(packages, answer, combination, is_creating_zero_entropy_layers, entropy_overlap_dict, store_path_entropy_dict, threshold, not_visted):
    highest = 0
    best_combination = None
    done = False
    close = False
    searched_combination_count_once_close = 0
    for r in reversed(range(1, len(list(packages)) + 1)):
        if done:
            break
        for combination in combinations(list(packages), r):
            package_list = combination + \
                tuple(answer[(combination, is_creating_zero_entropy_layers)]['packages']
                      ) if combination in answer else combination
            average = calculate_entropy_overlap(package_list, entropy_overlap_dict,
                                                store_path_entropy_dict)

            if threshold - average > 15:
                if not close and best_combination is not None:
                    break
            else:
                if close is False:
                    close = True
            if close:
                searched_combination_count_once_close = searched_combination_count_once_close + 1
            if searched_combination_count_once_close > 75:
                done = True
                break
            if average > highest and check_intersection(combination, not_visted):
                highest = average
                best_combination = combination
            if average > threshold:
                done = True
                break
    return best_combination

#
# def calculate_entropy_overlap(package_list, entropy_overlap_dict, store_path_entropy_dict):
#     sum = 0
#     count = 0
#     for package in package_list:
#         for p in package_list:
#             if p == package:
#                 continue
#             count = count + 1
#             numerator = entropy_overlap_dict[p.split(
#                 '-', 1)[1]].get(package.split('-', 1)[1], 0)
#             denominator = store_path_entropy_dict.get(
#                 package.split('-', 1)[1], 0)ive

#             sum += numerator/denominator
#     if count == 0:
#         return 0
#     average = 100*(sum/((count)))
#     return average

def update_relative_accounted_for_dict(recursive_dependencies_dict, package_file_size, accounted_for_packages_in_jobs, combination, master_list):

    relative_accounted_for_dict = {}

    is_accounted_for_file_size_threshold_satisified = True

    for job in job_whitelist:
        unique_packages = set()
        zero_entropy_packages = master_list[(job, True)]
        non_zero_entropy_packages = master_list[(job, False)]
        unique_packages.update(zero_entropy_packages)
        unique_packages.update(non_zero_entropy_packages)
        total_file_size = 0
        stripped_unique_packages = set()
        for item in unique_packages:
            # remove strip_hash from this to fix discrenpcy with accounted_for_file_size
            # TODO: define combination_package_dict to only have 1 of each package to start with
            stripped_unique_packages.add((strip_hash(item)))
            for p in recursive_dependencies_dict[item]:
                stripped_unique_packages.add((strip_hash(p)))
        for item in stripped_unique_packages:
            total_file_size += package_file_size[item]
        accounted_for_file_size = 0
        for item in accounted_for_packages_in_jobs[job]:
            accounted_for_file_size += package_file_size[item]
        if job in combination or job not in relative_accounted_for_dict:
            relative_accounted_for_dict[job] = accounted_for_file_size / \
                total_file_size
        # print(
        #     f"job={job}, 100*accounted_for_file_size/total_file_size={100*accounted_for_file_size/total_file_size}")
        if total_file_size != 0 and accounted_for_file_size/total_file_size < 0.98:
            is_accounted_for_file_size_threshold_satisified = False

    return relative_accounted_for_dict, is_accounted_for_file_size_threshold_satisified


def __generate_layers(hydra, update_progress, report_error,
                      send_layer, update_layer_progress,
                      project_name, jobset, minimum_layer_recursive_file_size,
                      maximum_layer_recursive_file_size, package_file_size, session_id, start_date, end_date):

    # stores the layers
    answer = {}
    # recursive_added_job[x] is a set of the packages recursively added to an image
    recursive_added_job = {}
    # accounted_for_packages_in_jobs[x] is a set of the required packages recursively added to an image
    accounted_for_packages_in_jobs = {}
    # stores the packages that could potentially be added to a combination (used to filter out packages that we know we won't want to add to a combination for efficency)
    combination_packages_dict = {}
    # used to itterate the for loop
    for_loop_flag = False

    # max_recursive_file_size = unique_packge_world_file_size*0.1
    maximum_layer_recursive_file_size_bytes = maximum_layer_recursive_file_size*1024*1024

    entropy_overlap_dict = {}

    # updated to reflect accounted for packages
    other_dict = {}

    # master lists that don't change
    master_list = {}

    # combined master list that doesn't change
    recursive_dependencies_dict = {}

    fowfol = set()

    gigmi = set()

    parsed_start_date = datetime.strptime(
        start_date, '%Y-%m-%dT%H:%M:%S.%fZ')

    parsed_end_date = datetime.strptime(
        end_date, '%Y-%m-%dT%H:%M:%S.%fZ')

    entropy_dict = fetch_and_compare_nix_paths(
        update_progress, parsed_start_date, parsed_end_date)

    maximum_layer_recursive_file_size_bytes = maximum_layer_recursive_file_size*1024*1024

    if (jobset, "fgl0wfl") in cache:

        references_dict, file_size_dict = cache[(jobset, "fgl0wfl")]
    else:

        references_dict = {}

        file_size_dict = {}

        visited_store_paths = {}

        traverse_jobset(hydra, lambda: None, lambda: None, project_name, jobset,
                        lambda job, raw_data: populate_references_and_file_sizes(
                            raw_data, references_dict, file_size_dict, jobset, job),
                        only_visit_once_enabled=True,
                        recursive_mode_enabled=True,
                        whitelist_enabled=False,
                        exponential_back_off_enabled=False,
                        visited_store_paths=visited_store_paths,
                        cancellable=True,
                        unique_packages_enabled=False)
        cache[(jobset, "fgl0wfl")] = references_dict, file_size_dict

    for job in job_whitelist:

        # note here that there is a maximum_recursive_file_size which is why we can't reuse the recursive_dependencies_dict from generate_layers()
        _recursive_dependencies_dict = get_recursive_dependencies(
            hydra, update_progress, report_error, project_name, jobset, traverse_jobset, references_dict, file_size_dict, jobs=[
                job],
            unique_packages_enabled=True, fowfol=fowfol, gigmi=gigmi, maximum_recursive_file_size=maximum_layer_recursive_file_size_bytes)

        recursive_dependencies_dict.update(_recursive_dependencies_dict)

        non_zero_entropy_packages, zero_entropy_packages = split_dict_by_value(
            _recursive_dependencies_dict, entropy_dict)

        master_list[(job, True)] = zero_entropy_packages

        master_list[(job, False)] = non_zero_entropy_packages

        other_dict[job] = copy.deepcopy(_recursive_dependencies_dict)

    for i in range(2):
        relative_accounted_for_dict = {}
        # keeping track of how many layers there are for a given combination
        combination_layer_count_dict = {}
        job_list = job_whitelist.copy()
        is_creating_zero_entropy_layers = i != 1
        print("Creating " + ("" if is_creating_zero_entropy_layers else "non") +
              "zero entropy layers...")
        current_iteration = 0

        percentage_done = 0
        update_progress("Trying all possible layers...", percentage_done)

        combination_lengths = [1, 7, 6, 5, 4, 3, 2, 1]
        combination_length_iteration = 0

        total_iterations = 0

        for k in range(1, len(job_list)+1):
            total_iterations += n_choose_k_count(len(job_list)+1, k)

        for combination_length in combination_lengths:

            if for_loop_flag:

                # needed without while loop
                for_loop_flag = False
                break
            combination_length_iteration = combination_length_iteration + 1

            combinations_list = list(
                combinations(job_list, combination_length))

            for combination in reversed(combinations_list):

                current_iteration += 1
                percentage_done = (current_iteration /
                                   total_iterations) * 100
                update_progress(
                    "Trying all possible layers...", percentage_done)

                done = False
                if for_loop_flag:
                    break

                # create as many layers based on a given combination as possible
                while not done:
                    done = True
                    if for_loop_flag:
                        break
                    if combination not in combination_layer_count_dict:
                        combination_layer_count_dict[combination] = 0

                    if file_exists(str(session_id)):
                        return True

                    combination_recursive_dependencies = {}

                    # hardcoding to just look at intersection of packages (no overlap mode)
                    if True:
                        combination_recursive_dependencies = other_dict[combination[0]]
                        for job in combination:

                            combination_recursive_dependencies = {
                                key: combination_recursive_dependencies[key]
                                for key in combination_recursive_dependencies
                                if key in other_dict[job]
                            }

                    else:

                        for job in combination:
                            combination_recursive_dependencies.update(
                                other_dict[job])

                    non_zero_entropy_packages, zero_entropy_packages = split_dict_by_value(
                        combination_recursive_dependencies, entropy_dict)

                    packages = zero_entropy_packages if is_creating_zero_entropy_layers else non_zero_entropy_packages

                    if (combination, is_creating_zero_entropy_layers) in combination_packages_dict:
                        packages = {
                            key: packages[key]
                            for key in packages
                            if key in combination_packages_dict.get((combination, is_creating_zero_entropy_layers), {})
                        }

                    combination_packages_dict[(
                        combination, is_creating_zero_entropy_layers)] = copy.deepcopy(packages)

                    if len(packages) == 0:
                        continue

                    if combination_length == 1:
                        # we want to go through the combination_length == 1 combinations first to calculate the job_overhead_dict but then consider the combinations
                        # in descending order of combination length such that if two different combinations both meet the same threshold, the one of higher combination
                        # length will be looked at first
                        if combination_length_iteration == 1:
                            continue

                    # this currently depreciated code exists to make future development easier (see More Sophisticated Entropy Calculation in the README)
                    not_visted = packages
                    while ((len(not_visted))):
                        if for_loop_flag:
                            break
                        # if is_creating_zero_entropy_layers:
                        _packages = packages
                        # else:
                        #     _packages = find_highest_average_package_combination(filtered_packages, answer, combination, is_creating_zero_entropy_layers, entropy_overlap_dict, store_path_entropy_dict, threshold, not_visted)
                        #     if _packages is None:
                        #         continue

                        not_visted = remove_common_elements(
                            not_visted, _packages)

                        individual_job_package_lists = []

                        for job in combination:
                            if job not in recursive_added_job:
                                recursive_added_job[job] = set()
                            if job not in accounted_for_packages_in_jobs:
                                accounted_for_packages_in_jobs[job] = set()

                            all_job_packages = {}
                            all_job_packages.update(master_list[(job, True)])
                            all_job_packages.update(master_list[(job, False)])

                            individual_job_package_lists.append(
                                (job, all_job_packages))

                        overhead, accounted_for_packages_file_size, selected_packages, relative_accounted_for, total_recursive_file_size = calculate_overhead(
                            combination, individual_job_package_lists, recursive_dependencies_dict, _packages, recursive_added_job, accounted_for_packages_in_jobs, i, is_creating_zero_entropy_layers, package_file_size, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size_bytes, other_dict, combination_packages_dict, answer, combination_layer_count_dict)

                        if relative_accounted_for == 0:
                            continue

                        if done:
                            done = False

                        update_accounted_for_packages(recursive_dependencies_dict, recursive_added_job,
                                                      accounted_for_packages_in_jobs, selected_packages, other_dict, individual_job_package_lists, package_file_size)

                        relative_accounted_for_dict, is_accounted_for_file_size_threshold_satisified = update_relative_accounted_for_dict(
                            recursive_dependencies_dict, package_file_size, accounted_for_packages_in_jobs, combination, master_list)

                        # adding new package(s) to an existing layer
                        if (combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination]) in answer:

                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['packages'].update(
                                selected_packages)
                            answer[(
                                combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['overhead'] += overhead
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])
                                   ]['accounted_for_packages_file_size'] += accounted_for_packages_file_size
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])
                                   ]['relative_accounted_for'] += relative_accounted_for
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])
                                   ]['total_recursive_file_size'] += total_recursive_file_size

                            if not is_creating_zero_entropy_layers:
                                # answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['average'] = calculate_entropy_overlap(
                                #     answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['packages'], entropy_overlap_dict, store_path_entropy_dict)
                                answer[(combination, is_creating_zero_entropy_layers,
                                        combination_layer_count_dict[combination])]['average'] = 0

                        # creating a new layer
                        else:

                            average = 0 if is_creating_zero_entropy_layers else 0
                            # calculate_entropy_overlap(
                            #     set(selected_packages), entropy_overlap_dict, store_path_entropy_dict)
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])] = {'overhead': overhead, 'packages': set(selected_packages),
                                                                                                                                 'accounted_for_packages_file_size': accounted_for_packages_file_size, 'average': average,
                                                                                                                                 'relative_accounted_for': relative_accounted_for, 'total_recursive_file_size': total_recursive_file_size}

                        total_overhead = 0
                        lowest_average = None
                        for layer in answer:
                            total_overhead += answer[layer]['overhead']
                            if lowest_average is None or answer[layer]['average'] < lowest_average:
                                lowest_average = answer[layer]['average']

                        new_packages_names = set()
                        for package in selected_packages:
                            new_packages_names.add(strip_hash(package))
                        new_packages = {'names': list(new_packages_names), 'overhead': overhead,
                                        'accounted_for_packages_file_size': accounted_for_packages_file_size}

                        layers = {}
                        for (_combination, _is_creating_zero_entropy_layers, _index) in answer:
                            layer = {}
                            layer = answer[(
                                _combination, _is_creating_zero_entropy_layers, _index)].copy()
                            layer['is_creating_zero_entropy_layers'] = _is_creating_zero_entropy_layers
                            file_size_accounted_for_relative = layer['relative_accounted_for']
                            layer['packages'] = list(layer['packages'])
                            layer['file_size_accounted_for_relative'] = file_size_accounted_for_relative/len(
                                job_whitelist)

                            layers[str((_combination, _index))] = layer

                        progress = {'is_creating_zero_entropy_layers': is_creating_zero_entropy_layers, 'layer_count': len(
                            answer), 'overhead': total_overhead, 'relative_accounted_for_dict': relative_accounted_for_dict, 'lowest_average': lowest_average, 'new_packages': new_packages, 'layers': layers}
                        update_layer_progress(progress)

                        # Hard coding 1 package per layer for now
                        if True or (combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination]) in answer and \
                                answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['total_recursive_file_size'] >= maximum_layer_recursive_file_size_bytes:
                            # print(
                            #     f"starting a new layer for combination={combination}")
                            # _send_layer(combination, is_creating_zero_entropy_layers, answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])], send_layer)
                            combination_layer_count_dict[combination] += 1

                        if is_accounted_for_file_size_threshold_satisified:
                            for_loop_flag = True
                            break

                        # is_new_package_added = True
                        # break

    send_layers(answer, is_creating_zero_entropy_layers, send_layer)
    print("Layer generation completed!")
    return answer, recursive_dependencies_dict


def main():
    pass


if __name__ == '__main__':
    main()
