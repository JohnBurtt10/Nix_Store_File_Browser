import cache_utils
from cache_directories import *
from raw_data_utilities import extract_section


def traverse_jobset(hydra, project_name, jobset, func, recursive_mode_enabled, exponential_back_off_enabled):
    data = cache_utils.get_cached_or_fetch_jobset_evals(
        hydra, jobset_evals_cache, project_name, jobset)
    # Access builds information
    evals_info = data.get('evals', [])

    for eval_info in evals_info:
        builds = eval_info.get('builds', [])

        # [487521, 487524, 487530, 487554,...
        for build in builds:
            build_info = cache_utils.get_cached_or_fetch_build_info(
                hydra, build_info_cache, build)
            out_path = build_info.get('outPath', [])
            job = build_info.get('job', [])
            # try:
            input_string = out_path
            # Removing "/nix/store" from the beginning of the string
            input_string = input_string[len("/nix/store/"):]
            traverse_jobset_recursive(
                hydra, func, job, input_string, recursive_mode_enabled, exponential_back_off_enabled)


def traverse_jobset_recursive(hydra, func, job, input_string, recursive_mode_enabled, exponential_back_off_enabled):
    # Splitting the string based on the first hyphen
    parts = input_string.split('-', 1)
    # Extracting the hash and the stuff after the first hyphen
    hash_value = parts[0]
    # try:
    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash_value, exponential_back_off_enabled)
    if raw_data is None:
        return
    func(job, raw_data)
    references = extract_section(raw_data=raw_data, keyword="References")
    if recursive_mode_enabled:
        for reference in references:
            if reference not in input_string:
                traverse_jobset_recursive(
                    hydra, func, job, reference, recursive_mode_enabled, exponential_back_off_enabled)
