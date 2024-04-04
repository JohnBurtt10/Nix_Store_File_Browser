from raw_data_utilities import extract_section
from cache_directories import *
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path
import sys
from get_sorted_jobsets import get_sorted_jobsets
from hydra_client import Hydra
from traverse_jobset import traverse_jobset
from merge_dicts_with_preference import merge_dicts_with_preference
from tqdm import tqdm
from job_whitelist import job_whitelist


def get_recursive_dependencies(hydra, update_progress, report_error, project_name, jobset, traverse_jobset, recursive_mode_enabled=False, exponential_back_off_enabled=False, only_visit_once_enabled=True, progress_bar_enabled=False, progress_bar_desc="Default progress bar desc", jobs=[], unique_packages_enabled=False, fowfol=set(), gigmi=set()):

    recursive_dependencies_dict = {}

    if not jobs:
        jobs = job_whitelist

    # if jobs:
    with tqdm(total=len(jobs), disable=not progress_bar_enabled, desc=progress_bar_desc, unit="builds") as pbar:
        for job in jobs:
            if False and (jobset, job, unique_packages_enabled) in get_recursive_dependencies_cache:
                recursive_dependencies_dict = merge_dicts_with_preference(
                    get_recursive_dependencies_cache[(jobset, job, unique_packages_enabled)], recursive_dependencies_dict)
            else:
                _recursive_dependencies_dict = {}
                traverse_jobset(hydra, update_progress, report_error, project_name, jobset,
                                lambda job, raw_data: _get_recursive_dependencies(hydra,
                                                                                raw_data,
                                                                                _recursive_dependencies_dict), recursive_mode_enabled=True, only_visit_once_enabled=True, progress_bar_enabled=True, whitelist_enabled=True, progress_bar_desc="Getting recursive dependencies:", jobs=[job], cancellable=True, unique_packages_enabled=unique_packages_enabled, fowfol=fowfol, gigmi=gigmi)
                get_recursive_dependencies_cache[(
                    jobset, job, unique_packages_enabled)] = _recursive_dependencies_dict
                recursive_dependencies_dict = merge_dicts_with_preference(
                    recursive_dependencies_dict, _recursive_dependencies_dict)
            pbar.update(1)
        return recursive_dependencies_dict
    # elif (jobset) in get_recursive_dependencies_cache:
    #     return get_recursive_dependencies_cache[jobset]

    # traverse_jobset(hydra, update_progress, report_error, project_name, jobset,
    #                 lambda job, raw_data: _get_recursive_dependencies(hydra,
    #                                                                   raw_data,
    #                                                                   recursive_dependencies_dict), recursive_mode_enabled=True, only_visit_once_enabled=True, progress_bar_enabled=True, whitelist_enabled=True, progress_bar_desc="Getting recursive dependencies:", cancellable=True)

    # get_recursive_dependencies_cache[jobset] = recursive_dependencies_dict
    # return recursive_dependencies_dict


def _get_recursive_dependencies(hydra, raw_data, recursive_dependencies_dict):
    store_path = extract_section(raw_data=raw_data, keyword="StorePath")[0]
    result = store_path.split("/nix/store/")[1]

    if False and result in _get_recursive_dependencies_cache:
        recursive_dependencies_dict[result] = _get_recursive_dependencies_cache[result]
        # print(f"{result}, {len(recursive_dependencies_dict[result])}")
    else:
        # print(f"cache miss :(")
        recursive_dependencies = __get_recursive_dependencies(hydra, result)
        recursive_dependencies_dict[result] = recursive_dependencies
        # print(f"len(recursive_dependencies_dict): {len(recursive_dependencies_dict)}")
        _get_recursive_dependencies_cache[result] = recursive_dependencies


def get_size_of_list_with_elements(my_list):
    size = sys.getsizeof(my_list)
    for element in my_list:
        size += sys.getsizeof(element)
    return size


def __get_recursive_dependencies(hydra, package, depth=0, recursive_dependencies=[], flag=False, path=()):
    if package is None:
        return (None)

    # if package in _get_recursive_dependencies_cache:

    #     return _get_recursive_dependencies_cache[package]
    (references, _) = get_references_and_file_size_from_store_path(hydra, package)
    count = 0
    for child in references:
        count = count + 1
        if child != package:
            if "roscpp" in child:
                print(f"package={package}")
            if child not in recursive_dependencies:
                recursive_dependencies.append(child)
                __get_recursive_dependencies(
                    hydra, child, depth+1, recursive_dependencies, flag=flag, path=path + (child,))

    # used to keep track of which ones are done
    return None if recursive_dependencies == [] else recursive_dependencies


def main():

    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    sorted_jobsets = get_sorted_jobsets(hydra, "v2-32-devel")

    jobset = sorted_jobsets[-2]

    get_recursive_dependencies(hydra, None, "v2-32-devel", jobset, traverse_jobset)


if __name__ == "__main__":
    main()
