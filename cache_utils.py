# nar caching
import aiohttp
import asyncio


def get_cached_or_fetch_nar_info(hydra, cache, hash):
    if hash in cache:
        return cache.get(hash)

    # # If hash is not in the cache, fetch the data
    raw_data = hydra.get_nar_info(hash=hash)

    return raw_data

def get_cached_or_fetch_jobset_evals(hydra, cache, project_name, jobset_name):
    # ???
    if False and (project_name, jobset_name) in cache:
        print(f"get_cached_or_fetch_jobset_evals cache hit!")
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

        print(f"reverse_dependency_weight_dict: {reverse_dependency_weight_dict}")
        reverse_dependency_weight_cache[jobset] = (
            reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)

    return (reverse_dependency_weight_dict, file_size_reverse_dependency_weight_dict)

def get_cached_or_compute_dependency_weight(project_name, jobset, dependency_weight_cache, traverse_jobset, hydra, calculate_dependency_weight):

    total_weight = {}

    total_weight_key = {}

    total_nodes = 0

    total_total_file_size = 0

    total_count_file_size = {}

    if False and jobset in dependency_weight_cache:
        print(f"hit cache with: {jobset}")
        (total_weight, total_weight_key, total_nodes, total_count_file_size,
         total_total_file_size) = dependency_weight_cache[jobset]
    
    else:
        
        total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size =calculate_dependency_weight(hydra,project_name,jobset,total_weight,total_weight_key,total_nodes,total_total_file_size,total_count_file_size)
        
        # traverse_jobset(hydra,project_name,jobset,lambda job,raw_data: calculate_dependency_weight(hydra,
        #                                                                                 raw_data,
        #                                                                                 total_weight,
        #                                                                                 total_weight_key,
        #                                                                                 total_nodes,
        #                                                                                 total_total_file_size,
        #                                                                                 total_count_file_size))
        
        # print(f"total_weight: {total_weight}")
        
        dependency_weight_cache[jobset] = (
            total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size)

    return total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size


