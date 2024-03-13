import asyncio
from raw_data_utilities import extract_section
from count_ancestors import _count_ancestors
from cache_directories import *
from sum_dicts import sum_dicts
import cache_utils
from cache_directories import *
from hydra_client import HydraResponseException, Hydra
from get_sorted_jobsets import get_sorted_jobsets
from tqdm import tqdm

def _calculate_dependency_weight(hydra,
                                 raw_data,
                                 total_weight,
                                 total_weight_key,
                                 total_nodes,
                                 total_total_file_size,
                                 total_count_file_size,
                                 run_async=False):

    references = extract_section(raw_data=raw_data, keyword="References")
    
    tuple_key = tuple(references)
    
    if tuple_key in _calculate_dependency_weight_cache:
        return _calculate_dependency_weight_cache[tuple_key]

    for dependency in references:
        if dependency in count_ancestor_cache:
            weight, weight_key, nodes, target_count, total_file_size, count_file_size, target_file_size =  count_ancestor_cache[dependency]
        else:
            # if dependency in out_path:
            #     continue
            weight, weight_key, nodes, target_count, total_file_size, count_file_size, target_file_size = asyncio.run(
                _count_ancestors(hydra, dependency, 0, 0))
            count_ancestor_cache[dependency] = (
                weight, weight_key, nodes, target_count, total_file_size, count_file_size, target_file_size)

        # not adjusted, hence adjustments made
        total_weight = sum_dicts(total_weight, weight)
        total_weight_key = sum_dicts(total_weight_key, weight_key)
        total_nodes += nodes
        total_total_file_size += total_file_size
        total_count_file_size = sum_dicts(
            total_count_file_size, count_file_size)

    # not sure why we have to do this return when dicts are mutable, must be something to do with async
    _calculate_dependency_weight_cache[tuple_key] = total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size
    return total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size

def calculate_dependency_weight(hydra, project_name, jobset):

    total_weight = {}

    total_weight_key = {}

    total_nodes = 0

    total_total_file_size = 0

    total_count_file_size = {}

    #TEMP:
    if "gwkmfkowo" in cache:
        return cache["gwkmfkowo"]

    
    data = cache_utils.get_cached_or_fetch_jobset_evals(hydra, jobset_evals_cache, project_name, jobset)
    # Access builds information
    evals_info = data.get('evals', [])

    for eval_info in evals_info:
        builds = eval_info.get('builds', [])

        # [487521, 487524, 487530, 487554,...
        with tqdm(total=len(builds), desc="Computing dependency weight", unit="builds") as pbar:
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
                    raw_data = cache_utils.get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value, False)
                    (total_weight,
                    total_weight_key,
                    total_nodes,
                    total_count_file_size,
                    total_total_file_size) = _calculate_dependency_weight(hydra,
                                                               raw_data,
                                                               total_weight,
                                                               total_weight_key,
                                                               total_nodes,
                                                               total_total_file_size,
                                                               total_count_file_size,
                                                               run_async=False)
                except HydraResponseException as e:
                    print(f"missed hash ({hash_value})")
                pbar.update(1)

    cache["gwkmfkowo"] = (total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size)

    return total_weight, total_weight_key, total_nodes, total_count_file_size, total_total_file_size


def main():

    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    jobset = get_sorted_jobsets(hydra, "v2-32-devel")[0]

    calculate_dependency_weight(hydra, "v2-32-devel", jobset)


if __name__ == "__main__":
    main()




