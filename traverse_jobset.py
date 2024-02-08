import cache_utils
from cache_directories import *
from hydra_client import HydraResponseException

def traverse_jobset(hydra, project_name, jobset, func):
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
            # try:
            input_string = out_path
            # Removing "/nix/store" from the beginning of the string
            input_string = input_string[len("/nix/store/"):]

            # Splitting the string based on the first hyphen
            parts = input_string.split('-', 1)

            # Extracting the hash and the stuff after the first hyphen
            hash_value = parts[0]
            try:
                raw_data = cache_utils.get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
                func(job, raw_data)
            except HydraResponseException as e:
                print(f"missed hash ({hash_value})")
            # except Exception as e:
            #     print(f"failed to retrieve direct dependencies of build: {build} with error: {e}")