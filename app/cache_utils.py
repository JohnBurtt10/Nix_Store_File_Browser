# nar caching
from .hydra_client import Hydra, HydraResponseException
from .cache_directories import *
import asyncio
from .raw_data_utilities import extract_section
from .group_items import group_items
import random
import time
from .get_sorted_jobsets import get_sorted_jobsets
from tqdm import tqdm
from .get_best_partial_jobsets_cache_key import get_best_partial_jobsets_cache_key

# Exponential backoff parameters
max_retries = 2
base_delay = 2  # Initial delay in seconds


def get_cached_or_fetch_nar_info(hydra, cache, hash, exponential_back_off_enabled):

    raw_data = None

    if hash in cache:
        return cache.get(hash)

    retries = 0

    while retries <= max_retries:
        try:
            # If hash is not in the cache, fetch the data
            raw_data = hydra.get_nar_info(hash=hash)
            # If the function succeeds, break out of the loop
            break
        except HydraResponseException as e:

            if not exponential_back_off_enabled:
                print("Retrying is disabled. Exiting.")
                break
            print(f"Attempt {retries + 1} failed: {e}")

            # Calculate the next delay using exponential backoff
            delay = base_delay * (2 ** retries)

            # Add some jitter to the delay to prevent synchronized retries
            jitter = random.uniform(0, 1)
            delay += jitter

            print(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

            retries += 1

    if retries > max_retries:
        print(f"Max retries reached. Exiting.")

    return raw_data


def get_cached_or_fetch_jobset_evals(hydra, cache, project_name, jobset_name):
    # ???
    if False and (project_name, jobset_name) in cache:
        return cache[(project_name, jobset_name)]
    data = hydra.get_jobset_evals(
        project=project_name, jobset_name=jobset_name)
    retries = 0

    # while retries <= max_retries:
    #     try:
    #         # If hash is not in the cache, fetch the data
    #         data = hydra.get_jobset_evals(project=project_name, jobset_name=jobset_name)
    #         (data.get('evals', []))[0]
    #         # If the function succeeds, break out of the loop
    #         break
    #     except IndexError as e:

    #         if False:
    #             print("Retrying is disabled. Exiting.")
    #             break
    #         print(f"Attempt {retries + 1} failed: {e}")

    #         # Calculate the next delay using exponential backoff
    #         delay = base_delay * (2 ** retries)

    #         # Add some jitter to the delay to prevent synchronized retries
    #         jitter = random.uniform(0, 1)
    #         delay += jitter

    #         print(f"Retrying in {delay:.2f} seconds...")
    #         time.sleep(delay)

    #         retries += 1

    # if retries > max_retries:
    #     print(f"Max retries reached. Exiting.")
    cache[(project_name, jobset_name)] = data
    return data


def get_cached_or_fetch_build_info(hydra, cache, build):
    if False and build in cache:
        return cache[build]
    build_info = hydra.get_build_info(build)
    cache[build] = build_info
    return build_info


async def async_get_cached_or_fetch_nar_info(hydra, cache, hash):
    if hash in cache:
        return cache.get(hash)

    # # If hash is not in the cache, fetch the data
    raw_data = await hydra.async_get_nar_info(hash=hash)

    # with cache:
    #     try:
    cache[hash] = raw_data
    #     except Exception as e:
    #         print(f"Error caching data: {e}")

    return raw_data


# build info caching?
async def async_get_cached_or_fetch_build_info(hydra, cache, build):
    if build in cache:
        return cache[build]

    loop = asyncio.get_event_loop()

    def sync_get_build_info():
        return hydra.get_build_info(build)

    build_info = await loop.run_in_executor(None, sync_get_build_info)

    cache[build] = build_info
    return build_info


def get_cached_or_fetch_out_path(build_info, out_path_cache):
    if False and build_info in out_path_cache:
        out_path = out_path_cache[build_info]
    else:
        out_path = build_info.get('outPath', [])
        out_path_cache[build_info] = out_path
    return out_path


def get_cached_or_fetch_job(build_info, job_cache):
    if False and build_info in job_cache:
        job = job_cache[build_info]
    else:
        job = build_info.get('job', [])
        job_cache[build_info] = job
    return job


def get_cached_or_fetch_jobset(build_info, jobset_cache):
    if False and build_info in jobset_cache:
        jobset = jobset_cache[build_info]
    else:
        jobset = build_info.get('jobset', [])
        jobset_cache[build_info] = jobset
    return jobset


def get_cached_or_fetch_builds(eval_info, builds_cache):
    if False and eval_info in builds_cache:
        builds = builds_cache[eval_info]
    else:
        builds = eval_info.get('builds', [])
        builds_cache[eval_info] = builds
    return builds


def get_cached_or_fetch_evals_info(data, evals_info_cache):
    if False and data in evals_info_cache:
        evals_info = evals_info_cache[data]
    else:
        evals_info = data.get('evals', [])
        evals_info_cache[data] = evals_info
    return evals_info


def _populate_references_and_file_size(raw_data, references_dict, file_size_dict, jobset, job):
    store_path = extract_section(raw_data=raw_data, keyword="StorePath")[0]
    references = extract_section(raw_data=raw_data, keyword="References")
    file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])
    references_dict[store_path[len("/nix/store/"):]] = references
    file_size_dict[store_path[len("/nix/store/"):]] = file_size


def get_cached_or_compute_reverse_dependency_weight(project_name, jobset, reverse_dependency_weight_cache, traverse_jobset, hydra, count_descendants):
    reverse_dependency_weight_dict = {}
    file_size_reverse_dependency_weight_dict = {}

    if jobset in reverse_dependency_weight_cache:
        print(f"reverse_dependency_weight_cache hit!")
        (reverse_dependency_weight_dict,
         file_size_reverse_dependency_weight_dict) = reverse_dependency_weight_cache[jobset]

    else:

        # def update_progress(task, progress):
        #     pass

        # def report_error(error):
        #     pass

        references_dict = {}

        file_size_dict = {}

        traverse_jobset(hydra, lambda task, progress: None, lambda error: None, project_name, jobset,
                        lambda job, raw_data: _populate_references_and_file_size(
                            raw_data, references_dict, file_size_dict, jobset, job),
                        only_visit_once_enabled=True,
                        recursive_mode_enabled=True,
                        whitelist_enabled=False,
                        exponential_back_off_enabled=False,
                        cancellable=True,
                        unique_packages_enabled=False)

        # TODO: Why are the dicts acting immutable??
        traverse_jobset(hydra, lambda task, progress: None, lambda error: None, project_name, jobset,
                        lambda job, raw_data: count_descendants(hydra,
                                                                raw_data,
                                                                reverse_dependency_weight_dict,
                                                                file_size_reverse_dependency_weight_dict, references_dict, file_size_dict), recursive_mode_enabled=False, only_visit_once_enabled=False, progress_bar_enabled=True, progress_bar_desc="Computing reverse dependency weights")

        reverse_dependency_weight_cache[jobset] = (
            reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)

    return (reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)


def get_cached_or_compute_dependency_weight(project_name, jobset, dependency_weight_cache, hydra, calculate_dependency_weight, traverse_jobset):

    if jobset in dependency_weight_cache:
        print(f"dependency_weight_cache hit!")
        (total_weight, total_weight_key, total_nodes, total_count_file_size,
         total_total_file_size) = dependency_weight_cache[jobset]

    else:

        # def update_progress(task, progress):
        #     pass

        # def report_error(error):
        #     pass

        references_dict = {}

        file_size_dict = {}

        traverse_jobset(hydra, lambda: None, lambda: None, project_name, jobset,
                        lambda job, raw_data: _populate_references_and_file_size(
                            raw_data, references_dict, file_size_dict, jobset, job),
                        only_visit_once_enabled=True,
                        recursive_mode_enabled=True,
                        whitelist_enabled=False,
                        exponential_back_off_enabled=False,
                        cancellable=True,
                        unique_packages_enabled=False)

        total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size = calculate_dependency_weight(
            hydra, project_name, jobset, references_dict, file_size_dict)

        dependency_weight_cache[jobset] = (
            total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size)

    return (total_weight, total_weight_key, total_nodes, total_count_file_size,
            total_total_file_size)


def general_cache_function(hydra, update_progress, report_error, project_name, traverse_jobset, cache, update_func, recursive_mode_enabled, exponential_back_off_enabled, progress_bar_enabled=True, whitelist_enabled=False, progress_bar_desc="Default progress bar desc", jobsets=None, *args):

    result_dicts = [{} for _ in args]

    if jobsets:
        sorted_jobsets = jobsets
    else:
        sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    processed_jobsets = []

    visited_store_paths = []

    partial_jobset_lists = list(cache.iterkeys())

    (best_list, remaining_jobsets) = get_best_partial_jobsets_cache_key(
        sorted_jobsets, partial_jobset_lists)

    if best_list is not None:
        processed_jobsets = list(best_list)
        partial_cache_key = tuple(best_list)

        if partial_cache_key in cache:
            (result_dicts, visited_store_paths) = cache[partial_cache_key]

            # result_dicts = cache[partial_cache_key]
    with tqdm(initial=0 if best_list is None else len(best_list), disable=not progress_bar_enabled, total=len(sorted_jobsets), desc=progress_bar_desc, unit="jobsets") as pbar:
        update_progress(progress_bar_desc+"...", 100 *
                        pbar.n/len(sorted_jobsets))
        for jobset in remaining_jobsets:
            _result_dicts = [{} for _ in args]
            if not traverse_jobset(hydra, update_progress, report_error, project_name, jobset,
                                   lambda job, raw_data: update_func(
                                       raw_data, _result_dicts, jobset, job), only_visit_once_enabled=True, recursive_mode_enabled=True, whitelist_enabled=whitelist_enabled, exponential_back_off_enabled=exponential_back_off_enabled, visited=visited_store_paths, cancellable=True, unique_packages_enabled=False):
                update_progress("", 0)
                print(
                    f"Proceeding without remaining {len(sorted_jobsets)-pbar.n} jobsets...")
                return result_dicts
            processed_jobsets.append(jobset)

            for index, value in enumerate(args):
                result_dicts[index] = value(
                    result_dicts[index], _result_dicts[index])
            cache_key = tuple(processed_jobsets)
            cache[cache_key] = (result_dicts, visited_store_paths)
            pbar.update(1)
            update_progress(progress_bar_desc+"...", 100 *
                            pbar.n/len(sorted_jobsets))

    update_progress("", 0)
    return result_dicts


def update_store_path_jobsets_dict(raw_data, dicts, jobset, job):

    references = extract_section(raw_data=raw_data, keyword="References")

    store_path_jobsets_dict = dicts[0]

    grouped_items = group_items(references, {})

    for dependency, group in grouped_items.items():
        if dependency in store_path_jobsets_dict:
            for store_path in group:
                if store_path in store_path_jobsets_dict[dependency]:
                    if jobset not in store_path_jobsets_dict[dependency][store_path]:
                        store_path_jobsets_dict[dependency][store_path].append(
                            jobset)
                else:
                    # If store_path is not in the dictionary, create a new entry
                    store_path_jobsets_dict[dependency][store_path] = [jobset]
        else:
            # If dependency is not in the dictionary, create a new entry
            store_path_jobsets_dict[dependency] = {}
            for store_path in group:
                if store_path in store_path_jobsets_dict[dependency]:
                    if jobset not in store_path_jobsets_dict[dependency][store_path]:
                        store_path_jobsets_dict[dependency][store_path].append(
                            jobset)
                else:
                    # If store_path is not in the dictionary, create a new entry
                    store_path_jobsets_dict[dependency][store_path] = [jobset]


def get_basic_entropy(dependency_all_store_path_dict):
    basic_entropy_dict = {}
    for key in dependency_all_store_path_dict:
        entropy = len(dependency_all_store_path_dict[key]) - 1
        if entropy > 0:
            basic_entropy_dict[key] = len(dependency_all_store_path_dict[key])
    return basic_entropy_dict


# dependency_all_store_path_dict


def update_dependency_all_store_path_dict(raw_data, dicts, jobset, job):
    references = extract_section(raw_data=raw_data, keyword="References")

    dependency_all_store_path_dict = dicts[0]

    grouped_items = group_items(references, {})

    for dependency, group in grouped_items.items():
        if dependency in dependency_all_store_path_dict:
            dependency_all_store_path_dict[dependency] = list(
                set(dependency_all_store_path_dict[dependency]) | set(group))
        else:
            dependency_all_store_path_dict[dependency] = group


# reverse dependencies


def update_reverse_dependencies_dict(raw_data, dicts, jobset, job):
    references = extract_section(raw_data=raw_data, keyword="References")
    reverse_dependencies_dict = dicts[0]
    grouped_items = group_items(references, {})

    for key in grouped_items:

        dependency = key

        # TODO: change this so that it also has the versions of the job
        if dependency in reverse_dependencies_dict:
            if job in reverse_dependencies_dict[dependency]:
                reverse_dependencies_dict[dependency][job].append(jobset)
            else:
                reverse_dependencies_dict[dependency][job] = [jobset]

        else:
            reverse_dependencies_dict[dependency] = {}
            reverse_dependencies_dict[dependency][job] = [jobset]


# store path hash dict


def update_store_path_file_size_dict(raw_data, dicts, jobset, job):

    file_size = extract_section(raw_data=raw_data, keyword="FileSize")
    references = extract_section(raw_data=raw_data, keyword="References")

    store_path_file_size_dict = dicts[0]

    grouped_items = group_items(references, {})

    for key in grouped_items:

        dependency = key

        store_path_file_size_dict[dependency] = int(file_size[0])


def update_dependency_store_path_dict(raw_data, dicts, jobset, job):

    references = extract_section(raw_data=raw_data, keyword="References")

    dependency_store_path_dict = dicts[0]

    for dependency in references:

        parts = dependency.split('-', 1)

        hash = parts[0]

        key = parts[1]

        dependency_store_path_dict[key] = hash


def main():

    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")


if __name__ == "__main__":
    main()
