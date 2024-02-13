# nar caching
from hydra_client import Hydra, HydraResponseException
from cache_directories import *
import aiohttp
import asyncio
from raw_data_utilities import extract_section
from group_items import group_items
import random
import time
from hydra_client import Hydra

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
    if (project_name, jobset_name) in cache:
        return cache[(project_name, jobset_name)]
    data = hydra.get_jobset_evals(
        project=project_name, jobset_name=jobset_name)
    cache[(project_name, jobset_name)] = data
    return data


def get_cached_or_fetch_build_info(hydra, cache, build):
    if build in cache:
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


async def async_get_cached_or_fetch_jobset_evals(hydra, cache, project_name, jobset_name):
    if (project_name, jobset_name) in cache:
        print(f"get_cached_or_fetch_jobset_evals cache hit!")
        return cache[(project_name, jobset_name)]

    async with aiohttp.ClientSession() as session:
        # Assuming hydra.get_jobset_evals is an asynchronous function
        data = await hydra.get_jobset_evals(session, project=project_name, jobset_name=jobset_name)

    cache[(project_name, jobset_name)] = data
    return data


def get_cached_or_fetch_out_path(build_info, out_path_cache):
    if build_info in out_path_cache:
        out_path = out_path_cache[build_info]
    else:
        out_path = build_info.get('outPath', [])
        out_path_cache[build_info] = out_path
    return out_path


def get_cached_or_fetch_job(build_info, job_cache):
    if build_info in job_cache:
        job = job_cache[build_info]
    else:
        job = build_info.get('job', [])
        job_cache[build_info] = job
    return job


def get_cached_or_fetch_jobset(build_info, jobset_cache):
    if build_info in jobset_cache:
        jobset = jobset_cache[build_info]
    else:
        jobset = build_info.get('jobset', [])
        jobset_cache[build_info] = jobset
    return jobset


def get_cached_or_fetch_builds(eval_info, builds_cache):
    if eval_info in builds_cache:
        builds = builds_cache[eval_info]
    else:
        builds = eval_info.get('builds', [])
        builds_cache[eval_info] = builds
    return builds


def get_cached_or_fetch_evals_info(data, evals_info_cache):
    if data in evals_info_cache:
        evals_info = evals_info_cache[data]
    else:
        evals_info = data.get('evals', [])
        evals_info_cache[data] = evals_info
    return evals_info


def get_cached_or_compute_reverse_dependency_weight(project_name, jobset, reverse_dependency_weight_cache, traverse_jobset, hydra, count_descendants):
    reverse_dependency_weight_dict = {}
    file_size_reverse_dependency_weight_dict = {}
    if jobset in reverse_dependency_weight_cache:
        (reverse_dependency_weight_dict,
         file_size_reverse_dependency_weight_dict) = reverse_dependency_weight_cache[jobset]

    else:

        # TODO: Why are the dicts acting immutable??
        traverse_jobset(hydra, project_name, jobset,
                        lambda job, raw_data: count_descendants(hydra,
                                                                raw_data,
                                                                reverse_dependency_weight_dict,
                                                                file_size_reverse_dependency_weight_dict))

        print(
            f"reverse_dependency_weight_dict: {reverse_dependency_weight_dict}")
        reverse_dependency_weight_cache[jobset] = (
            reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)

    return (reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)


def get_cached_or_compute_dependency_weight(project_name, jobset, dependency_weight_cache, traverse_jobset, hydra, calculate_dependency_weight):

    total_weight = {}

    total_weight_key = {}

    total_nodes = 0

    total_total_file_size = 0

    total_count_file_size = {}

    if jobset in dependency_weight_cache:
        print(f"hit cache with: {jobset}")
        (total_weight, total_weight_key, total_nodes, total_count_file_size,
         total_total_file_size) = dependency_weight_cache[jobset]

    else:

        total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size = calculate_dependency_weight(
            hydra, project_name, jobset, total_weight, total_weight_key, total_nodes, total_total_file_size, total_count_file_size)

        dependency_weight_cache[jobset] = (
            total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size)

    return total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size


def general_cache_function(hydra, project_name, traverse_jobset, cache, update_func, recursive_mode_enabled, exponential_back_off_enabled, *args):

    result_dicts = [{} for _ in args]

    jobsets = hydra.get_jobsets(project_name)

    (remaining_jobsets, cache_value) = partial_jobsets_cache(jobsets, cache)

    # remaining_jobsets = jobsets

    # cache_value = None

    if cache_value is not None:
        result_dicts = cache_value

    # TODO: check for complete cache hit?

    for jobset in remaining_jobsets:
        cache_key = tuple([jobset])
        if cache_key in cache:
            print(f"cache: {cache}, jobset: {jobset} cache hit!")
            # cache hit!
            _result_dicts = cache[cache_key]
        else:
            print(f"cache: {cache}, jobset: {jobset} cache miss!")
            _result_dicts = [{} for _ in args]
            traverse_jobset(hydra, project_name, jobset,
                            lambda job, raw_data: update_func(
                                raw_data, _result_dicts, jobset, job), recursive_mode_enabled, exponential_back_off_enabled)
            cache[cache_key] = _result_dicts

        # TODO: ???

        # Using enumerate to iterate through the list with index
        for index, value in enumerate(args):
            result_dicts[index] = value(
                result_dicts[index], _result_dicts[index])

    cache_key = tuple(jobsets)
    cache[cache_key] = result_dicts
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


# dependency_all_store_path_dict

def partial_jobsets_cache(jobsets, cache):
    cache_value = None
    result_n = 0
    remaining_jobsets = []
    matching_sublist = None
    for n in range(len(jobsets), 0, -1):
        prefix = jobsets[:n]
        matching_sublist = next(
            (key for key in cache if prefix == key[:len(prefix)]), None)
        for key in cache:
            key = list(key)
            if prefix == key[:len(prefix)]:
                matching_sublist = prefix
                # break  # If you only want to print the first matching sublist, you can break out of the loop
        if matching_sublist is not None:
            result_n = n
            remaining_jobsets = jobsets[result_n:]
            break

    print("The highest value of n is:", result_n)
    # print("Remaining elements:", remaining_jobsets)
    # print("Matching sublist in my_second_list:", matching_sublist)
    if (matching_sublist is not None) and tuple(matching_sublist) in cache:
        cache_value = cache[tuple(matching_sublist)]

    else:
        remaining_jobsets = jobsets

    return remaining_jobsets, cache_value


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

    for key, group in grouped_items.items():

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

def get_cached_or_fetch_store_path_entropy_dict(hydra, project_name, traverse_jobset, recursive_mode_enabled, exponential_back_off_enabled, store_path_entropy_dict_cache):

    store_path_hash_dict = {}

    store_path_entropy_dict = {}

    dependency_store_path_dict = {}

    jobsets = hydra.get_jobsets(project_name)

    cache_key = tuple(jobsets)

    if cache_key in store_path_entropy_dict_cache:
        return store_path_entropy_dict_cache[cache_key][0]

    remaining_jobsets = jobsets

    for jobset in remaining_jobsets:
        traverse_jobset(hydra, project_name, jobset,
                        lambda job, raw_data: update_store_path_hash_dict(raw_data, job, store_path_hash_dict, store_path_entropy_dict, dependency_store_path_dict), recursive_mode_enabled, exponential_back_off_enabled)

    cache_key = tuple(jobsets)
    store_path_entropy_dict_cache[cache_key] = (
        store_path_entropy_dict, store_path_hash_dict)
    return store_path_entropy_dict


def update_store_path_hash_dict(raw_data, job, _store_path_hash_dict, _store_path_entropy_dict, _dependency_store_path_dict):

    if raw_data is None:
        print(f"update_store_path_hash_dict got raw_data is None")
        return

    references = extract_section(raw_data=raw_data, keyword="References")
    store_path_hash_dict = _store_path_hash_dict
    store_path_entropy_dict = _store_path_entropy_dict

    grouped_items = group_items(references, {})

    for key, group in grouped_items.items():

        dependency = key

        if job in store_path_hash_dict:
            if dependency in store_path_hash_dict[job]:
                if store_path_hash_dict[job][dependency] != group:
                    # TODO: untested
                    if dependency not in store_path_entropy_dict:
                        store_path_entropy_dict[dependency] = 0
                    else:
                        store_path_entropy_dict[dependency] = store_path_entropy_dict[dependency] + 1
                    store_path_hash_dict[job][dependency] = group
            else:
                # init dicts
                store_path_hash_dict[job][dependency] = group
        else:
            store_path_hash_dict[job] = {}
            store_path_hash_dict[job][dependency] = group


def update_store_path_file_size_dict(raw_data, dicts, jobset, job):

    file_size = extract_section(raw_data=raw_data, keyword="FileSize")
    references = extract_section(raw_data=raw_data, keyword="References")

    store_path_file_size_dict = dicts[0]

    grouped_items = group_items(references, {})

    for key, group in grouped_items.items():

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

    get_cached_or_fetch_nar_info(hydra, nar_info_cache, "1")


if __name__ == "__main__":
    main()
