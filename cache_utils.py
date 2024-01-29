# nar caching
import threading
import aiohttp
import asyncio

def get_cached_or_fetch_nar_info(hydra, cache, hash):
    if hash in cache:
        return cache.get(hash)

    # # If hash is not in the cache, fetch the data
    raw_data = hydra.get_nar_info(hash=hash)

    # with cache:
    #     try:
    #         cache[hash] = raw_data
    #     except Exception as e:
    #         print(f"Error caching data: {e}")

    return raw_data

def get_cached_or_fetch_jobset_evals(hydra, cache, project_name, jobset_name):
    # ???
    if False and (project_name,jobset_name) in cache:
        print(f"get_cached_or_fetch_jobset_evals cache hit!")
        return cache[(project_name,jobset_name)]
    data = hydra.get_jobset_evals(project=project_name,jobset_name=jobset_name)
    cache[(project_name,jobset_name)] = data
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