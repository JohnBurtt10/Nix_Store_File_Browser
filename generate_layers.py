import copy
from calculate_overhead import calculate_overhead
from update_stuff import update_stuff
from get_file_size_from_store_path import get_file_size_from_store_path
from cache_directories import *
from hydra_client import Hydra
from new_get_recursive_dependencies import get_recursive_dependencies
from traverse_jobset import traverse_jobset
from new_calculate_entropy import get_cached_or_fetch_store_path_entropy_dict
from topological_sort import topological_sort_until_all_packages
import cache_utils
from sum_dicts import sum_dicts_of_lists
from job_whitelist import job_whitelist
from itertools import combinations
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path
from layering_sanity_check import layering_sanity_check
from get_sorted_jobsets import get_sorted_jobsets
import pickle
from get_file_sizes_by_path import get_file_sizes_by_path

def retrieve_and_check_cancel():
    return False

    # Retrieve variables from the file
    with open('data.pkl', 'rb') as f:  # Open file in binary read mode
        loaded_data = pickle.load(f)
    if loaded_data['cancel']:
        print(f"Cancellign operation!")
        return True


def split_dict_by_value(my_dict, entropy_dict):
    matching_values = {}
    non_matching_values = {}

    for key in my_dict:
        if key.split('-', 1)[1] in entropy_dict:
            matching_values[key] = my_dict[key]
        else:
            non_matching_values[key] = my_dict[key]

    return matching_values, non_matching_values

def get_recursive_dependency_weight(package, recursive_dependencies_dict, package_file_size):
    recursive_dependency_weight = 0
    recursive_dependency_weight += package_file_size.get(package, 0)
    for item in recursive_dependencies_dict.get(package, []):
        recursive_dependency_weight += package_file_size.get(item, 0)

    return recursive_dependency_weight

def get_true_recursive_file_size(hydra, layer, recursive_dependencies_dict, package_file_size):
    true_recursive_file_size = 0

    for package in layer['packages']:
        true_recursive_file_size +=  get_file_size_from_store_path(
            hydra, package)
        for item in recursive_dependencies_dict[package]:
            true_recursive_file_size += get_file_size_from_store_path(
            hydra, item)
    return true_recursive_file_size


def generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, coverage_threshold_mode_enabled=False, coverage_threshold=0, package_count_mode_enabled=False, package_count=0, project_name="v2-34-devel"):

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)
    jobset = sorted_jobsets[0]

    # zzz has demo version
    if ("generate_layersa", minimum_layer_recursive_file_size, maximum_layer_recursive_file_size) in cache:
        answer, recursive_dependencies_dict = cache[("generate_layersa", minimum_layer_recursive_file_size, maximum_layer_recursive_file_size)]
    else:
        recursive_dependencies_dict = get_recursive_dependencies(
            hydra, update_progress, report_error, project_name, jobset, traverse_jobset, unique_packages_enabled=True)
        answer, _ = _generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, 
                                  coverage_threshold_mode_enabled, coverage_threshold, package_count_mode_enabled, package_count, project_name, jobset)
        cache[("generate_layersa", minimum_layer_recursive_file_size, maximum_layer_recursive_file_size)] = answer, recursive_dependencies_dict
    # print(f"answer={answer}")
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
    #cppcheck total file size

    if False and (jobset, "gwgwfg") in cache:

        package_file_size, unique_packge_world_file_size = cache[(
            jobset, "gwgwfg")]

    else:
        package_file_size, unique_packge_world_file_size = get_file_sizes_by_path(
            recursive_dependencies_dict, hydra, recursive_dependencies_dict)

        cache[(jobset, "gwgwfg")] = package_file_size, unique_packge_world_file_size

    for job, layers in job_layer_dict.items():
        # if job != "ottoFmCoreContainer.x86_64-linux":
        #     continue
        # print(f"job={job}")
        # Sorting the dictionary of dictionaries based on 'total_recursive_file_size'
        # 0 has the lowest total_recursive_file_size since we want to create a layer with stuff at the bottom of the tree first then create
        # the next layer based on everything but what's included in layer 0 and so on...
        sorted_data = sorted(layers, key=lambda x: get_true_recursive_file_size(hydra, x, recursive_dependencies_dict, package_file_size))
        fioq2wf = set()
        ggg = set ()
        containerData[job] = []
        count = 0
        thing = {}
        other_thing = {}

        other_thing[0] = {'smallest': 0}

        for index, tiwrio in enumerate(sorted_data):
            tiwrio['total_recursive_file_size'] = get_true_recursive_file_size(hydra, tiwrio, recursive_dependencies_dict, package_file_size)
            first_item = next(iter(tiwrio['packages']))
            packages = set(recursive_dependencies_dict[first_item]).union({first_item})
            new = packages.difference(fioq2wf)
            fioq2wf = packages.union(fioq2wf)
            if not packages.issubset((ggg.union(new))):
                ggg = fioq2wf
                other_thing[count]['largest'] = index-1
                count += 1
                other_thing[count] = {}
                other_thing[count]['smallest'] = index
            thing[str(tiwrio['packages'])] = count
            sum = 0
            for item in new:
                sum += get_file_size_from_store_path(hydra, item)
            tiwrio['new_file_size_layer_wise'] = sum

            sorted_accounted_for_packages = sorted(list(new), key=lambda x: get_recursive_dependency_weight(x, recursive_dependencies_dict, package_file_size))

            sorted_accounted_for_packages = [item for item in sorted_accounted_for_packages if "ros" in item]

            tiwrio['accounted_for_packages'] = sorted_accounted_for_packages

            new_data_magnitude = str(round(sum/( 1024 * 1024), 2))
            
            tiwrio['new_data_magnitude'] = new_data_magnitude

            total_recursive_file_size_magnitude = str(round(tiwrio['total_recursive_file_size']/( 1024 * 1024), 2))

            tiwrio['total_recursive_file_size_magnitude'] = total_recursive_file_size_magnitude

        
        other_thing[count]['largest'] = len(sorted_data)-1
        
        for index, tiwrio in enumerate(sorted_data):
            first_item = next(iter(tiwrio['packages']))

            first_item_file_size = str(round(package_file_size[first_item]/( 1024 * 1024), 2))

            stripped_packages = [strip_hash(
              item) for item in tiwrio['accounted_for_packages']]
            

            if other_thing[thing[str(tiwrio['packages'])]]['smallest'] == other_thing[thing[str(tiwrio['packages'])]]['largest']:
                layer_string = str(other_thing[thing[str(tiwrio['packages'])]]['smallest'])
            else:
                layer_string = str(other_thing[thing[str(tiwrio['packages'])]]['smallest']) + '-' + str(other_thing[thing[str(tiwrio['packages'])]]['largest'])


            containerData[job].append({'layer': 'Layer ' + layer_string, 'packages': [first_item], 'packageFileSize': first_item_file_size + 'MB', 'newData': tiwrio['new_data_magnitude'] + 'MB', 'accountedForPackages': stripped_packages, 'totalRecursiveFileSize':tiwrio['total_recursive_file_size_magnitude'] + 'MB'})
    
    return containerData
        
        # break


def _generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, coverage_threshold_mode_enabled, coverage_threshold, package_count_mode_enabled, package_count, project_name, jobset):

    if True:
        store_path_entropy_dict, fokwfko = get_cached_or_fetch_store_path_entropy_dict(
            hydra, project_name, update_progress, approximate_uncalculated_jobsets_mode_enabled=True)

    else:
        dependency_all_store_path_dict = cache_utils.general_cache_function(hydra, update_progress, report_error, "v2-32-devel", traverse_jobset, dependency_all_store_path_dict_cache,
                                                                            cache_utils.update_dependency_all_store_path_dict, False, False, True, True, "Finding all store paths for packages", None, sum_dicts_of_lists)[0]
        store_path_entropy_dict = cache_utils.get_basic_entropy(
            dependency_all_store_path_dict)

    # if retrieve_and_check_cancel():
    #     return True

    return __generate_layers(hydra, update_progress, report_error,
                             send_layer, update_layer_progress,
                             project_name, jobset, store_path_entropy_dict, fokwfko, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size)


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


def get_fikwsfkmwdfio(hydra, recursive_dependencies_dict, packages):
    my_set = set()
    for package in packages:
        my_set.add(package)
        my_set.update(recursive_dependencies_dict[package])

    total_file_size = 0

    for item in my_set:
        _, file_size = get_references_and_file_size_from_store_path(
            hydra, item)
        total_file_size += file_size
    return total_file_size, len(my_set)


def check_intersection(list1, list2):
    # Convert lists to sets for faster intersection operation
    set1 = set(list1)
    set2 = set(list2)

    # Check if there is any intersection between the two sets
    if set1.intersection(set2):
        return True
    else:
        return False


def remove_common_elements(list1, list2):
    # Convert lists to sets for faster intersection operation
    set1 = set(list1)
    set2 = set(list2)

    # Remove common elements from list1
    result = [x for x in list1 if x not in set2]

    return result


def find_highest_average_package_combination(packages, answer, combination, is_creating_zero_entropy_layers, fokwfko, store_path_entropy_dict, threshold, not_visted):
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
            average = fwfo(package_list, fokwfko,
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


def get_top_10_by_dependency_weight_file_size(hydra, recursive_dependencies_dict, packages, coverage_threshold_mode_enabled, coverage_threshold, package_count_mode_enabled, package_count):

    # sort by file size dependency weight after filtering dependencies
    # take #1, remove all packages that #1 account for from filter pool
    # repeat until pool empty
    file_size_dict = {}
    for package in packages:
        file_size_dict[package] = get_file_size_from_store_path(hydra, package)
        for item in recursive_dependencies_dict[package]:
            file_size_dict[item] = get_file_size_from_store_path(hydra, item)

    # TODO: pass as list of keys for best practice?
    total_layer_file_size, total_items = get_fikwsfkmwdfio(
        hydra, recursive_dependencies_dict, packages)

    result = []
    i = 0
    while (True):
        if package_count_mode_enabled and i == int(package_count):
            return result
        highest_file_size_dependency_weight = 0
        highest_file_size_dependency_weight_package = None
        for package in packages:
            # print(f"package: {package}")
            file_size_dependency_weight = 0
            file_size = file_size_dict[package]
            file_size_dependency_weight += file_size
            for item in recursive_dependencies_dict[package]:
                # print(f"item: {item}")
                file_size = file_size_dict[item]
                file_size_dependency_weight += file_size
            if file_size_dependency_weight > highest_file_size_dependency_weight:
                highest_file_size_dependency_weight = file_size_dependency_weight
                highest_file_size_dependency_weight_package = package
        result.append(highest_file_size_dependency_weight_package)
        thing = packages[highest_file_size_dependency_weight_package]
        packages.pop(highest_file_size_dependency_weight_package)

        # check % coverage

        if coverage_threshold_mode_enabled:

            wfkow, items = get_fikwsfkmwdfio(
                hydra, recursive_dependencies_dict, result)

            print(
                f"wfkow/total_layer_file_size: {wfkow/total_layer_file_size}")
            if wfkow/total_layer_file_size > int(coverage_threshold)/100:
                return result

        # re-filtering

        sum = 0
        for key in packages:
            sum += 1
            sum += len(packages[key])

        for key, lst in packages.items():
            packages[key] = [item for item in lst if item not in thing]

        _packages = packages.copy()
        for key in packages:
            flag = False
            if len(packages[key]) == 0:
                for r in result:
                    if flag == True:
                        break
                    for item in recursive_dependencies_dict[r]:
                        if r == key or item == key:
                            _packages.pop(key)
                            flag = True
                            break

        packages = _packages.copy()

        # for key in list(packages.keys()):
        #     if key in packages:
        #         try:
        #             packages[key] = [
        #                 neighbor for neighbor in packages[key] if neighbor in packages]
        #         except Exception as e:
        #             packages[key] = []

        sum = 0
        for key in packages:
            sum += 1
            sum += len(packages[key])

        i = i + 1


def strip_hash(string):
    return string.split('-', 1)[1]


#
# def fwfo(package_list, fokwfko, store_path_entropy_dict):
#     sum = 0
#     count = 0
#     for package in package_list:
#         for p in package_list:
#             if p == package:
#                 continue
#             count = count + 1
#             numerator = fokwfko[p.split(
#                 '-', 1)[1]].get(package.split('-', 1)[1], 0)
#             denominator = store_path_entropy_dict.get(
#                 package.split('-', 1)[1], 0)

#             # REMOVOEOEOROR

#             if (denominator == 0):
#                 denominator = 1

#             sum += numerator/denominator
#     if count == 0:
#         return 0
#     average = 100*(sum/((count)))
#     return average


def n_choose_k_count(n, k):
    numerator = 1
    denominator = 1
    for i in range(1, min(k, n - k) + 1):
        numerator *= n - i + 1
        denominator *= i
    return numerator // denominator


def _send_layer(combination, zero_entropy_layer, layer, send_layer):
    _overhead = layer['overhead']
    _accounted_for_packages_file_size = layer['accounted_for_packages_file_size']
    stripped_packages = layer['packages']
    layer_info = {'combination': list(combination), 'overhead': _overhead, 'packages': list(
        stripped_packages), 'accounted_for_packages_file_size': _accounted_for_packages_file_size, 'zero_entropy_layer': zero_entropy_layer}
    send_layer(layer_info)


def send_layers(answer, is_creating_zero_entropy_layers, send_layer):
    for (combination, zero_entropy_layer, i) in answer:
        if is_creating_zero_entropy_layers != zero_entropy_layer:
            continue
        layer = answer[(combination, zero_entropy_layer, i)]
        _send_layer(combination, zero_entropy_layer, layer, send_layer)


def update_relative_accounted_for_dict(is_creating_zero_entropy_layers, recursive_dependencies_dict, package_file_size, accounted_for_packages_in_jobs, combination, master_list):

    relative_accounted_for_dict = {}

    is_accounted_for_file_size_threshold_satisified = True

    for job in job_whitelist:
        # ggg = master_list[(job, is_creating_zero_entropy_layers)]
        ggg = set()
        zero_entropy_packages = master_list[(job, True)]
        # non_zero_entropy_packages = master_list[(job, False)]
        ggg.update(zero_entropy_packages)
        # ggg.update(non_zero_entropy_packages)
        total_file_size = 0
        unique_packages = set()
        for item in ggg:

            # remove strip_hash from this to fix discrenpcy with accounted_for_file_size
            # TODO: define combination_package_dict to only have 1 of each package to start with
            unique_packages.add((strip_hash(item)))
            for p in recursive_dependencies_dict[item]:
                unique_packages.add((strip_hash(p)))
        for item in unique_packages:
            total_file_size += package_file_size[item]
        accounted_for_file_size = 0
        for item in accounted_for_packages_in_jobs[job]:
            accounted_for_file_size += package_file_size[item]
        if job in combination or job not in relative_accounted_for_dict:
            relative_accounted_for_dict[job] = 1 if total_file_size == 0 else accounted_for_file_size / \
                total_file_size
            # print(f"update_relative_accounted_for_dict, job={job}, total_file_size={total_file_size}")
            # y += accounted_for_file_size / \
            #     total_file_size
            # print(
            #     f"job:{job} is now {100*accounted_for_file_size/total_file_size}%, {accounted_for_file_size}/{total_file_size} accounted for")
        if total_file_size != 0 and accounted_for_file_size/total_file_size < 0.98:
            is_accounted_for_file_size_threshold_satisified = False

    # ffpwdfw = 0
    # for thing in recursive_dependencies_dict:
    #     ffpwdfw += len(recursive_dependencies_dict[thing])
    # for job in job_whitelist:
    #     all_job_packages = set()
    #     zero_entropy_packages = master_list[(job, True)]
    #     non_zero_entropy_packages = master_list[(job, False)]
    #     # print(f"job={job}, len(non_zero_entropy_packages)={len(non_zero_entropy_packages)}")
    #     all_job_packages.update(zero_entropy_packages)
    #     all_job_packages.update(non_zero_entropy_packages)
    #     total_file_size = 0
    #     zero_entropy_specific_recursive_total_file_size = 0
    #     non_zero_entropy_specific_recursive_total_file_size = 0
    #     unique_packages = set()
    #     for item in zero_entropy_packages:
    #         # remove strip_hash from this to fix discrenpcy with accounted_for_file_size
    #         # TODO: define combination_package_dict to only have 1 of each package to start with
    #         unique_packages.add((strip_hash(item)))
    #         for p in recursive_dependencies_dict[item]:
    #             unique_packages.add((strip_hash(p)))
    #     for item in unique_packages:
    #         zero_entropy_specific_recursive_total_file_size += package_file_size[item]
    #     unique_packages = set()
    #     for item in non_zero_entropy_packages:
    #         # remove strip_hash from this to fix discrenpcy with accounted_for_file_size
    #         # TODO: define combination_package_dict to only have 1 of each package to start with
    #         unique_packages.add((strip_hash(item)))
    #         for p in recursive_dependencies_dict[item]:
    #             unique_packages.add((strip_hash(p)))
    #     for item in unique_packages:
    #         non_zero_entropy_specific_recursive_total_file_size += package_file_size[item]
    #     unique_packages = set()
    #     for item in all_job_packages:
    #         # remove strip_hash from this to fix discrenpcy with accounted_for_file_size
    #         # TODO: define combination_package_dict to only have 1 of each package to start with
    #         unique_packages.add((strip_hash(item)))
    #         for p in recursive_dependencies_dict[item]:
    #             unique_packages.add((strip_hash(p)))
    #     for item in unique_packages:
    #         total_file_size += package_file_size[item]
    #     accounted_for_file_size = 0
    #     for item in accounted_for_packages_in_jobs[job]:
    #         accounted_for_file_size += package_file_size[item]
    #     if job in combination and job == "simGazeboContainer.x86_64-linux":
    #         # print(f"job={job}, len(unique_packages)={len(unique_packages)}, len(accounted_for_packages_in_jobs[{job}]={len(accounted_for_packages_in_jobs[job])}, non zero coverage={accounted_for_file_size/non_zero_entropy_specific_recursive_total_file_size}")
    #         print(f"job={job}, zero entropy coverage={accounted_for_file_size/zero_entropy_specific_recursive_total_file_size} ({accounted_for_file_size/(1024*1024)}/{zero_entropy_specific_recursive_total_file_size/(1024*1024)}), non zero coverage={accounted_for_file_size/non_zero_entropy_specific_recursive_total_file_size}, overall coverage={accounted_for_file_size/total_file_size}")
    return relative_accounted_for_dict, is_accounted_for_file_size_threshold_satisified


def fgwfa(unaccounted_for_packages, recursive_dependencies_dict, item, package_file_size):

    # print(f"len(unaccounted_for_packages)={len(unaccounted_for_packages)}")

    still_present = set()

    still_present.add(item)
    still_present.update(recursive_dependencies_dict[item])

    items_fwekf = still_present.intersection(unaccounted_for_packages)

    sum = 0

    for item in items_fwekf:
        sum += package_file_size[item]

    # print(f"sum={sum}")

    return sum

def limit_recursive_dependencies(recursive_dependencies_dict, limit, package_file_size):

    if limit is None:
        return _recursive_dependencies_dict

    _recursive_dependencies_dict = {}

    for key in recursive_dependencies_dict:
        sum = 0
        _recursive_dependencies_dict[key] = []
        if sum + package_file_size[key] > limit:
            continue
        sum += package_file_size[key]
        for package in recursive_dependencies_dict[key]:
            if sum + package_file_size[package] > limit:
                break
            sum += package_file_size[package]
            _recursive_dependencies_dict[key].append(package)

    return _recursive_dependencies_dict


def __generate_layers(hydra, update_progress, report_error,
                      send_layer, update_layer_progress,
                      project_name, jobset, store_path_entropy_dict, fokwfko, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size):

    print(f"__generate_layers()")

    output_directory = "output_files"

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    answer = {}
    recursive_added_job = {}
    accounted_for_packages_in_jobs = {}
    combination_packages_dict = {}
    package_file_size = None
    for_loop_flag = False

    fowfol = set()
    gigmi = set()

    # max_recursive_file_size = unique_packge_world_file_size*0.1
    # minimum_layer_recursive_file_size_bytes = maximum_layer_recursive_file_size*1024*1024
    maximum_layer_recursive_file_size_bytes = maximum_layer_recursive_file_size*1024*1024

    # updated to reflect accounted for packages
    other_dict = {}

    # master lists that don't change
    master_list = {}

    # combined master list that doesn't change
    recursive_dependencies_dict = {}
    for job in job_whitelist:
        _recursive_dependencies_dict = get_recursive_dependencies(
            hydra, update_progress, report_error, project_name, jobset, traverse_jobset, jobs=[job], unique_packages_enabled=True, fowfol=fowfol, gigmi=gigmi, maximum_recursive_file_size=maximum_layer_recursive_file_size_bytes)

        recursive_dependencies_dict.update(_recursive_dependencies_dict)
        non_zero_entropy_packages, zero_entropy_packages = split_dict_by_value(
            _recursive_dependencies_dict, store_path_entropy_dict)

        master_list[(job, True)] = zero_entropy_packages
        master_list[(job, False)] = non_zero_entropy_packages
        other_dict[job] = copy.deepcopy(_recursive_dependencies_dict)


    if False and (jobset, "gawsfgqwfg") in cache:

        package_file_size, unique_packge_world_file_size = cache[(
            jobset, "gawsfgqwfg")]

    else:
        package_file_size, unique_packge_world_file_size = get_file_sizes_by_path(
            recursive_dependencies_dict, hydra, recursive_dependencies_dict)

        cache[(jobset, "gawsfgqwfg")] = package_file_size, unique_packge_world_file_size

    sum = 0
    sum += package_file_size['lic263yjp40jmkc40y3vrcfbpv7lqn10-pth-2.0.7']
    for item in recursive_dependencies_dict['lic263yjp40jmkc40y3vrcfbpv7lqn10-pth-2.0.7']:
        sum += package_file_size[item]


    print(f"sum={sum/(1024*1024)}, len(recursive_dependencies_dict['lic263yjp40jmkc40y3vrcfbpv7lqn10-pth-2.0.7'])={len(recursive_dependencies_dict['lic263yjp40jmkc40y3vrcfbpv7lqn10-pth-2.0.7'])}, [maximum_layer_recursive_file_size={maximum_layer_recursive_file_size}")

    # TODO: take stuff out of while loop
    # make case in shared entropy thing for all 0 and take full package thing then pass in packages
    for i in range(2):
        # iteration = 0
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
        idk = 0

        total_iterations = 0

        for k in range(1, len(job_list)+1):
            total_iterations += n_choose_k_count(len(job_list)+1, k)

        for combination_length in combination_lengths:

            if for_loop_flag:

                # needed without while loop 
                for_loop_flag = False
                break
            idk = idk + 1

            combinations_list = list(
                combinations(job_list, combination_length))

            for combination in reversed(combinations_list):

                # if len(answer) > 7:
                #     return answer, recursive_dependencies_dict
                current_iteration += 1
                percentage_done = (current_iteration /
                                     total_iterations) * 100
                update_progress(
                     "Trying all possible layers...", percentage_done)


                done = False
                if for_loop_flag:
                    break
                while not done:
                    done = True
                    if for_loop_flag:
                        break
                    if combination not in combination_layer_count_dict:
                        combination_layer_count_dict[combination] = 0

                    # if retrieve_and_check_cancel():
                    #     return True

                    # TODO: get rid of this if else? replace all the _generate_layers_cache calls with get_recursive_dependencies?

                    if True or (combination, is_creating_zero_entropy_layers) not in combination_packages_dict:

                        if False and (sorted_jobsets, combination, is_creating_zero_entropy_layers) in _generate_layers_cache:
                            packages = _generate_layers_cache[(
                                sorted_jobsets, combination, is_creating_zero_entropy_layers)]

                            combination_packages_dict[(
                                combination, is_creating_zero_entropy_layers)] = packages

                        else:

                            combination_recursive_dependencies = {}

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
                                combination_recursive_dependencies, store_path_entropy_dict)

                            packages = zero_entropy_packages if is_creating_zero_entropy_layers else non_zero_entropy_packages

                            if (combination, is_creating_zero_entropy_layers) in combination_packages_dict:
                                packages = {
                                    key: packages[key]
                                    for key in packages
                                    if key in combination_packages_dict.get((combination, is_creating_zero_entropy_layers), {})
                                }

                            # reduced_package_list = topological_sort_until_all_packages(
                            #     recursive_dependencies_dict, non_zero_entropy_packages)

                            # reduced_package_list = []

                            # if not layering_sanity_check(non_zero_entropy_packages, reduced_package_list, recursive_dependencies_dict):
                            #     print(f"LAYERING SANITY CHECK FAILED, PROGRAM IS BROKEN!")
                            #     return

                            _generate_layers_cache[(
                                sorted_jobsets, combination, is_creating_zero_entropy_layers)] = packages

                            combination_packages_dict[(
                                combination, is_creating_zero_entropy_layers)] = copy.deepcopy(packages)

                    if len(packages) == 0:
                        continue

                    if combination_length == 1:
                        # we want to go through the combination_length == 1 combinations first to calculate the job_overhead_dict but then consider the combinations
                        # in descending order of combination length such that if two different combinations both meet the same threshold, the one of higher combination
                        # length will be looked at first
                        # if iteration < 20:
                        #     continue
                        if idk == 1:
                            continue

                    not_visted = packages
                    while ((len(not_visted))):
                        if for_loop_flag:
                            break
                        # if is_creating_zero_entropy_layers:
                        dd = packages
                        # else:
                        #     dd = find_highest_average_package_combination(filtered_packages, answer, combination, is_creating_zero_entropy_layers, fokwfko, store_path_entropy_dict, threshold, not_visted)
                        #     if dd is None:
                        #         continue

                        not_visted = remove_common_elements(not_visted, dd)

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
                            combination, individual_job_package_lists, recursive_dependencies_dict, dd, recursive_added_job, accounted_for_packages_in_jobs, i, is_creating_zero_entropy_layers, package_file_size, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size_bytes, other_dict, combination_packages_dict, answer, combination_layer_count_dict)

                        if relative_accounted_for == 0:
                            continue

                        if done:
                            done = False

                        # TODO: CHECK WHICH JOBS ACTUALLY NEED THE PACKAGES ADDED

                        # TODO: INVESTIGATE WHY SCREEN-SHELL IS BEING ADDED WITH ACCOUNTED_FOR_PACKAGE_FILE_SIZE=0 and OVERHEAD!=0

                        update_stuff(recursive_dependencies_dict, recursive_added_job,
                                        accounted_for_packages_in_jobs, selected_packages, other_dict, individual_job_package_lists, package_file_size)

                        relative_accounted_for_dict, is_accounted_for_file_size_threshold_satisified = update_relative_accounted_for_dict(
                            is_creating_zero_entropy_layers, recursive_dependencies_dict, package_file_size, accounted_for_packages_in_jobs, combination, master_list)
                        
                        # stripped_packages = [strip_hash(
                        #     item) for item in selected_packages]

                        stripped_packages = selected_packages

                        # adding new package(s) to an existing layer
                        if (combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination]) in answer:

                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['packages'].update(
                                stripped_packages)
                            answer[(
                                combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['overhead'] += overhead
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])
                                    ]['accounted_for_packages_file_size'] += accounted_for_packages_file_size
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])
                                    ]['relative_accounted_for'] += relative_accounted_for
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])
                                    ]['total_recursive_file_size'] += total_recursive_file_size

                            if not is_creating_zero_entropy_layers:
                                # answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['average'] = fwfo(
                                #     answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])]['packages'], fokwfko, store_path_entropy_dict)
                                answer[(combination, is_creating_zero_entropy_layers,
                                        combination_layer_count_dict[combination])]['average'] = 0

                        # creating a new layer
                        else:

                            average = 0 if is_creating_zero_entropy_layers else 0
                            # fwfo(
                            #     set(selected_packages), fokwfko, store_path_entropy_dict)
                            answer[(combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination])] = {'overhead': overhead, 'packages': set(stripped_packages),
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
                        x = 0
                        for (a, b, c) in answer:
                            layer = {}
                            layer = answer[(a, b, c)].copy()
                            layer['is_creating_zero_entropy_layers'] = b
                            file_size_accounted_for_relative = layer['relative_accounted_for']
                            x += file_size_accounted_for_relative
                            layer['packages'] = list(layer['packages'])
                            layer['file_size_accounted_for_relative'] = file_size_accounted_for_relative/len(
                                job_whitelist)
                            
                            layers[str((a, c))] = layer

                        progress = {'is_creating_zero_entropy_layers': is_creating_zero_entropy_layers, 'layer_count': len(
                            answer), 'overhead': total_overhead, 'relative_accounted_for_dict': relative_accounted_for_dict, 'lowest_average': lowest_average, 'new_packages': new_packages, 'layers': layers}
                        update_layer_progress(progress)

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
    return answer, recursive_dependencies_dict

def main():

    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    def update_progress(task, progress):
        pass

    def report_error(error):
        pass

    def send_layer(layer):
        pass

    def update_layer_progress(progress):
        pass

    project_name = "v2-34-devel"

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)
    jobset = sorted_jobsets[-3]

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    store_path_entropy_dict, fokwfko = get_cached_or_fetch_store_path_entropy_dict(
        hydra, "v2-32-devel", update_progress, approximate_uncalculated_jobsets_mode_enabled=True)

    values = [50, 100, 200, 400, 800, 1600, 2000]

    for v in values:
        answers = __generate_layers(hydra, update_progress, report_error,
                                    send_layer, update_layer_progress,
                                    project_name, jobset, store_path_entropy_dict, fokwfko, v)
        print(f"v={v}, len(answers)={len(answers)}")


if __name__ == '__main__':
    main()
