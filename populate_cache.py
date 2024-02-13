from hydra_client import Hydra
from cache_directories import *
from traverse_jobset import traverse_jobset
from count_descendants import count_descendants
import cache_utils
from calculate_dependency_weight import calculate_dependency_weight
from process_dependency_group import process_dependency_group


def populate_reverse_dependency_weight_cache(hydra, project, jobsets):

    for jobset in jobsets:

        if jobset not in reverse_dependency_weight_cache:
            cache_utils.get_cached_or_compute_reverse_dependency_weight(
                project, jobset, reverse_dependency_weight_cache, traverse_jobset, hydra, count_descendants)


def populate_update_dicts_cache(hydra, project, jobsets):

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

    if jobsets not in dependency_weight_cache:

        # TODO: do I need to sort?

        # Iterate in reverse order
        for n in range(len(jobsets), 0, -1):
            prefix = jobsets[:n]
            matching_sublist = next(
                (lst for lst in update_dicts_cache if prefix == lst[:len(prefix)]), None)
            if matching_sublist is not None:
                result_n = n
                remaining_jobsets = jobsets[result_n:]
                break

        # print("The highest value of n is:", result_n)
        # print("Remaining elements:", remaining_jobsets)
        # print("Matching sublist in my_second_list:", matching_sublist)

        if (matching_sublist is not None) and matching_sublist in update_dicts_cache:

            # partial cache hit!
            (store_path_entropy_dict,
                store_path_file_size_dict,
                reverse_dependencies_dict,
                dependency_store_path_dict,
                dependency_all_store_path_dict,
                store_path_jobsets_dict,
                earliest_jobset,
                jobsets) = update_dicts_cache[matching_sublist]

        else:
            remaining_jobsets = jobsets

        for jobset in remaining_jobsets:
            traverse_jobset(hydra, project, jobset,
                            lambda job, raw_data: process_dependency_group(
                                raw_data,
                                dependency_store_path_dict,
                                job,
                                jobset,
                                store_path_hash_dict,
                                store_path_entropy_dict,
                                store_path_file_size_dict,
                                reverse_dependencies_dict,
                                dependency_all_store_path_dict,
                                store_path_jobsets_dict))

        latest_jobset = remaining_jobsets[-1]

        update_dicts_cache[jobsets] = (store_path_entropy_dict,
                                       store_path_file_size_dict,
                                       reverse_dependencies_dict,
                                       dependency_store_path_dict,
                                       dependency_all_store_path_dict,
                                       store_path_jobsets_dict,
                                       earliest_jobset,
                                       latest_jobset)


def populate_dependency_weight_cache(hydra, jobsets, project):

    for jobset in jobsets:
        cache_utils.get_cached_or_compute_dependency_weight(
            project, jobset, dependency_weight_cache, traverse_jobset, hydra, calculate_dependency_weight)


def populate_cache(hydra):

    # hydra config
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    hydra.login(username="administrator", password="clearp@th")

    projects = hydra.get_projects()

    for project in projects:

        jobsets = hydra.get_jobsets(project)

        populate_dependency_weight_cache(hydra, jobsets, project)

        populate_update_dicts_cache(hydra, project, jobsets)
