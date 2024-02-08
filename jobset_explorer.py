from cache_directories import *
import re
from hydra_client import HydraResponseException
import cache_utils
from raw_data_utilities import extract_section
from hydra_client import Hydra
from traverse_jobset import traverse_jobset
from sum_dicts import sum_dicts
# TODO: name?


def update_job_references_dict_with_dict(job_references_dict, job, raw_data):
    references = extract_section(raw_data=raw_data, keyword="References")
    job_references_dict[job] = references


def get_job_references_dict(hydra, project_name, jobset):
    job_references_dict = {}
    # if (project_name, jobset) in get_job_references_dict_cache:
    #     # cache hit!
    #     return get_job_references_dict_cache[(project_name, jobset)]
    traverse_jobset(hydra, project_name, jobset, lambda job,
                    raw_data: update_job_references_dict_with_dict(job_references_dict, job, raw_data))
    get_job_references_dict_cache[(project_name, jobset)] = job_references_dict
    return job_references_dict


def get_references_from_store_path(hydra, store_path):
    parts = store_path.split('-', 1)
    # Extracting the hash and the stuff after the first hyphen
    hash_value = parts[0]
    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash_value)
    references = extract_section(raw_data=raw_data, keyword="References")
    if store_path in references:
        references.remove(store_path)
    return references


def handle_compare_and_group_references(hydra, store_path1, store_path2):
    if (store_path1, store_path2) in handle_compare_and_group_references_cache:
        return handle_compare_and_group_references_cache[(store_path1, store_path2)]
    result_tuples = []
    references1 = [] if store_path1 is None else get_references_from_store_path(
        hydra, store_path1)
    references2 = [] if store_path2 is None else get_references_from_store_path(
        hydra, store_path2)
    grouped_items = compare_and_group_references(references1, references2)
    for _, values in grouped_items.items():
        list1_item, list2_item, list1_item_file_size, list2_item_file_size = extract_list_info(
            hydra, values)
        val = 0
        result_tuples.append(
            (list1_item, list2_item, list2_item_file_size-list1_item_file_size, val))

    handle_compare_and_group_references_cache[(
        store_path1, store_path2)] = result_tuples
    return result_tuples


def get_disjunction(list1, list2):
    set1 = set(list1)
    set2 = set(list2)

    # Get elements present in either set, but not in both
    disjunction = set1.symmetric_difference(set2)

    # Convert the set back to a list
    return list(disjunction)


def store_path_get_file_size(hydra, store_path):
    parts = store_path.split('-', 1)
    # Extracting the hash and the stuff after the first hyphen
    hash_value = parts[0]
    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash_value)
    file_size = extract_section(raw_data=raw_data, keyword="FileSize")
    # TODO: ?
    return int(file_size[0])

# given 2 lists of references returns the changes in dependencies


def compare_and_group_references(references1, references2):

    if (references1, references2) in compare_and_group_references_cache:
        return compare_and_group_job_cache[(references1, references2)]

    jobset1_unique_references = [item for item in references1 if (
        item not in references2) and "merged" not in item]

    jobset2_unique_references = [item for item in references2 if (
        item not in references1) and "merged" not in item]
    # Create a dictionary to group items
    grouped_items = {}

    for item in jobset1_unique_references + jobset2_unique_references:
        key = item.split('-', 1)[1]

        # Define a regular expression pattern to match timestamps
        timestamp_pattern = r'\d{14}'

        # Replace timestamps in both strings with an empty string
        str_without_timestamp = re.sub(timestamp_pattern, '', key)

        if str_without_timestamp not in grouped_items:
            grouped_items[str_without_timestamp] = {'list1': [], 'list2': []}

        if item in references1:
            grouped_items[str_without_timestamp]['list1'].append(item)
        elif item in references2:
            grouped_items[str_without_timestamp]['list2'].append(item)

    compare_and_group_job_cache[(references1, references2)] = grouped_items
    return grouped_items


def calculate_recursive_file_size_change(hydra, store_path1, store_path2):
    if ("calculate", store_path1, store_path2) in cache:
        return cache[("calculate", store_path1, store_path2)]
    result = 0
    grouped_items = handle_compare_and_group_references(
        hydra, store_path1, store_path2)
    for x in grouped_items:
        result += x[2]
        # calculate_recursive_file_size_change(hydra, x[0], x[1])
    cache[("calculate", store_path1, store_path2)] = result
    return result


def extract_list_info(hydra, values):
    list1 = values.get('list1')
    list2 = values.get('list2')
    list1_item = None if len(list1) == 0 else list1[0]
    list2_item = None if len(list2) == 0 else list2[0]
    list1_item_file_size = 0 if list1_item is None else store_path_get_file_size(
        hydra, list1_item)
    list2_item_file_size = 0 if list2_item is None else store_path_get_file_size(
        hydra, list2_item)
    return list1_item, list2_item, list1_item_file_size, list2_item_file_size

# given a project, job and 2 jobsets, get the differences in the direct dependencies of the jobsets


def compare_and_group_job(hydra, project_name, jobs, jobset1, jobset2):

    jobset1_job_references_dict = get_job_references_dict(
        hydra, project_name, jobset1)
    jobset2_job_references_dict = get_job_references_dict(
        hydra, project_name, jobset2)

    final_result_tuples = {}

    for job in jobs:

        if (project_name, job, jobset1, jobset2) in compare_and_group_job_cache:
            result_tuples = compare_and_group_job_cache[(
                project_name, job, jobset1, jobset2)]
            final_result_tuples[job] = result_tuples
            continue

        grouped_items = compare_and_group_references(
            jobset1_job_references_dict[job], jobset2_job_references_dict[job])

        # Create tuples
        result_tuples = []

        for key, values in grouped_items.items():
            list1_item, list2_item, list1_item_file_size, list2_item_file_size = extract_list_info(
                hydra, values)
            val = 0
            result_tuples.append(
                (list1_item, list2_item, list2_item_file_size-list1_item_file_size, val))

        compare_and_group_job_cache[(
            project_name, job, jobset1, jobset2)] = result_tuples
        final_result_tuples[job] = result_tuples
    return final_result_tuples


def get_references_from_build_info(hydra, build_info):
    references = []
    out_path = build_info.get('outPath', [])
    try:
        input_string = out_path
        input_string = input_string[len("/nix/store/"):]
        parts = input_string.split('-', 1)
        hash_value = parts[0]

        # Separate awaits for each coroutine call
        raw_data = cache_utils.get_cached_or_fetch_nar_info(
            hydra, nar_info_cache, hash_value)
        try:
            references = extract_section(
                raw_data=raw_data, keyword="References")
        except AttributeError as e:
            print(f"raw data: :{raw_data}")
    except HydraResponseException as e:
        print(f"missed hash ({hash_value})")
    # except Exception as e:
    #     print(f"failed to retrieve direct dependencies of build: {build} with error: {e}")
    return references


def get_jobs(hydra, project_name, jobset):

    jobs = []

    data = cache_utils.get_cached_or_fetch_jobset_evals(
        hydra, jobset_evals_cache, project_name, jobset)

    eval_info = data.get('evals', [])[0]

    builds = eval_info.get('builds', [])
    for build in builds:
        print(f"build: {build}")
        build_info = cache_utils.get_cached_or_fetch_build_info(
            hydra, build_info_cache, build)
        job = build_info.get('job', '')
        jobs.append(job)

    return jobs


def update_maps_for_grouped_items(hydra, grouped_items, final_hash_map, final_count_hash_map):
    for _, values in grouped_items.items():
        list1_item, list2_item, _, list2_item_file_size = extract_list_info(
            hydra, values)
        result_hash_map, count_hash_map = process_and_compare_paths(
            hydra, list1_item, list2_item, list2_item_file_size)
        final_hash_map = sum_dicts(final_hash_map, result_hash_map)
        final_count_hash_map = sum_dicts(final_count_hash_map, count_hash_map)
    return (final_hash_map, final_count_hash_map)


def update_maps_with_cache(project_name, job1, jobset1, jobset2, final_hash_map, final_count_hash_map):
    (result_hash_map, count_hash_map) = compare_and_process_builds_cache[(
        project_name, job1, jobset1, jobset2)]
    final_hash_map = sum_dicts(final_hash_map, result_hash_map)
    final_count_hash_map = sum_dicts(final_count_hash_map, count_hash_map)


def get_jobset_builds(hydra, project_name, jobset):
    data = cache_utils.get_cached_or_fetch_jobset_evals(
        hydra, jobset_evals_cache, project_name, jobset)
    eval_info = data.get('evals', [])[0]
    builds = eval_info.get('builds', [])
    return builds


def compare_and_process_builds(project_name, hydra, jobs, jobset1, jobset2):

    final_hash_map = {}
    final_count_hash_map = {}

    builds1 = get_jobset_builds(hydra, project_name, jobset1)
    builds2 = get_jobset_builds(hydra, project_name, jobset2)

    for build1 in builds1:
        build_info1 = cache_utils.get_cached_or_fetch_build_info(
            hydra, build_info_cache, build1)
        job1 = build_info1.get('job', '')
        if job1 not in jobs:
            continue
        if (project_name, job1, jobset1, jobset2) in compare_and_process_builds_cache:
            update_maps_with_cache(
                project_name, job1, jobset1, jobset2, final_hash_map, final_count_hash_map)
            continue
        for build2 in builds2:
            build_info2 = cache_utils.get_cached_or_fetch_build_info(
                hydra, build_info_cache, build2)
            job2 = build_info2.get('job', '')
            if job1 == job2:
                break
        references1 = get_references_from_build_info(hydra, build_info1)
        references2 = get_references_from_build_info(hydra, build_info2)
        grouped_items = compare_and_group_references(references1, references2)
        (final_hash_map, final_count_hash_map) = update_maps_for_grouped_items(
            hydra, grouped_items, final_hash_map, final_count_hash_map)

    return final_hash_map, final_count_hash_map


def update_process_compare_store_paths_maps(result_hash_map, count_hash_map, r_c_m, c_h_m):
    result_hash_map = sum_dicts(result_hash_map, r_c_m)
    count_hash_map = sum_dicts(count_hash_map, c_h_m)
    return (result_hash_map, count_hash_map)


def process_and_compare_paths(hydra, store_path1, store_path2, file_size, result_hash_map=None, count_hash_map=None):
    if result_hash_map is None:
        result_hash_map = {}
    if count_hash_map is None:
        count_hash_map = {}
    if (store_path1, store_path2, file_size) in process_and_compare_paths_cache:
        # cache hit!
        print(f"cache hit!")
        r_c_m, c_h_m = process_and_compare_paths_cache[(
            store_path1, store_path2, file_size)]
    else:
        grouped_items = handle_compare_and_group_references(
            hydra, store_path1, store_path2)
        r_c_m = {}
        c_h_m = {}
        for item in grouped_items:
            list1_item = None if len(item) == 0 else item[0]
            list2_item = None if len(item) < 2 else item[1]
            if (list1_item is None and list2_item is None):
                print(f"######################ITEM: {item}")
            list1_item_file_size = 0 if (
                list1_item is None) else store_path_get_file_size(hydra, list1_item)
            list2_item_file_size = 0 if (
                list2_item is None) else store_path_get_file_size(hydra, list2_item)
            if (list1_item_file_size != list2_item_file_size):
                # TODO: figure out better way to handle this
                if list2_item is not None:
                    if list2_item in r_c_m:
                        r_c_m[list2_item] += file_size+list2_item_file_size
                    else:
                        r_c_m[list2_item] = file_size+list2_item_file_size

                    if list2_item in c_h_m:
                        c_h_m[list2_item] += 1
                    else:
                        c_h_m[list2_item] = 1
                else:
                    if list1_item:
                        if list1_item in r_c_m:
                            r_c_m[list1_item] += file_size+list1_item_file_size
                        else:
                            r_c_m[list1_item] = file_size+list1_item_file_size

                        if list1_item in c_h_m:
                            c_h_m[list1_item] += 1
                        else:
                            c_h_m[list1_item] = 1
        process_and_compare_paths_cache[(
            store_path1, store_path2, file_size)] = (r_c_m, c_h_m)
    print(f"r_c_m: {r_c_m}, c_h_m: {c_h_m}")
    (result_hash_map, count_hash_map) = update_process_compare_store_paths_maps(
        result_hash_map, count_hash_map, r_c_m, c_h_m)
    print(
        f"result_hash_map: {result_hash_map}, count_hash_map: {count_hash_map}")
    # TODO: shouldn't need to do this?
    return result_hash_map, count_hash_map


# TODO: finish this
# Specify which functions to export
__all__ = ['func1', 'func3']


def main():

    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    # Example: Pushing a jobset
    project_name = "v2-32-devel"

    print(f"{get_job_references_dict(hydra, project_name, 'v2.32.0-20240130164931-0')}")


if __name__ == "__main__":
    main()
