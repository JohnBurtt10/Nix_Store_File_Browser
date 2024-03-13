from tqdm import tqdm
from cache_directories import *
from hydra_client import Hydra
from get_sorted_jobsets import get_sorted_jobsets
import cache_utils
from get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path
from remove_timestamp import remove_timestamp
from compare_and_group_references import compare_and_group_references
from get_jobset_builds import get_jobset_builds
from get_best_partial_jobsets_cache_key import get_best_partial_jobsets_cache_key
from job_whitelist import job_whitelist

def get_cached_or_fetch_store_path_entropy_dict(hydra, project_name, approximate_uncalculated_jobsets_mode_enabled=False):

    store_path_entropy_dict = {}

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    partial_jobset_lists = list(store_path_entropy_dict_cache.iterkeys())

    (best_list, remaining_jobsets) = get_best_partial_jobsets_cache_key(
        sorted_jobsets, partial_jobset_lists)

    if best_list is not None:
        partial_cache_key = tuple(best_list)

        if partial_cache_key in store_path_entropy_dict_cache:
            store_path_entropy_dict = store_path_entropy_dict_cache[partial_cache_key]
            if approximate_uncalculated_jobsets_mode_enabled:
                print(f"approximating the entropy for the remaining {len(sorted_jobsets)-len(best_list)}/{len(sorted_jobsets)} jobsets...")
                factor = len(sorted_jobsets)/len(best_list)
                for key in store_path_entropy_dict:
                    store_path_entropy_dict[key] = round(store_path_entropy_dict[key] * factor)
                return store_path_entropy_dict

    return calculate_entropy(hydra,
                             project_name,
                             sorted_jobsets,
                             remaining_jobsets,
                             best_list,
                             store_path_entropy_dict,
                             approximate_uncalculated_jobsets_mode_enabled)


def calculate_entropy(hydra,
                      project_name,
                      sorted_jobsets,
                      remaining_jobsets,
                      best_list=None,
                      store_path_entropy_dict={},
                      approximate_uncalculated_jobsets_mode_enabled=False,
                      recursive_mode_enabled=False,
                      exponential_back_off_enabled=False):

    processed_jobsets = []
    
    if best_list is not None:
        processed_jobsets = list(best_list)

    with tqdm(initial=0 if best_list is None else len(best_list), total=len(sorted_jobsets), desc="Computing entropy", unit="jobsets") as pbar:
        for jobset in remaining_jobsets:
            # print(f"starting jobset: {jobset}")
            if remaining_jobsets.index(jobset) < len(remaining_jobsets) - 1:
                next_jobset = remaining_jobsets[remaining_jobsets.index(
                    jobset) + 1]
            else:
                break
            traverse_jobset(hydra, project_name, jobset, next_jobset,
                            store_path_entropy_dict)

            processed_jobsets.append(jobset)
            cache_key = tuple(processed_jobsets)
            store_path_entropy_dict_cache[cache_key] = store_path_entropy_dict
            pbar.update(1)
            if approximate_uncalculated_jobsets_mode_enabled:
                print(f"approximating the entropy for the remaining {len(sorted_jobsets)-len(processed_jobsets)}/{len(sorted_jobsets)} jobsets...")
                factor = len(sorted_jobsets)/len(processed_jobsets)
                for key in store_path_entropy_dict:
                    store_path_entropy_dict[key] = round(store_path_entropy_dict[key] * factor)
                return store_path_entropy_dict

    # cache_key = tuple(sorted_jobsets)
    # store_path_entropy_dict_cache[cache_key] = store_path_entropy_dict
    return store_path_entropy_dict


def traverse_jobset(hydra, project_name, jobset1, jobset2, store_path_entropy_dict):
    # [487521, 487524, 487530, 487554,...
    builds1 = get_jobset_builds(hydra, project_name, jobset1)
    builds2 = get_jobset_builds(hydra, project_name, jobset2)
    filtered_builds1 = []
    # filtered_builds2 = []

    if True:
        for build in builds1:
            build_info = cache_utils.get_cached_or_fetch_build_info(
            hydra, build_info_cache, build)
            job = build_info.get('job', [])
            if job in job_whitelist:
                filtered_builds1.append(build)

    else:
        filtered_builds1 = builds1
        # for build in builds2:
        #     build_info = cache_utils.get_cached_or_fetch_build_info(
        #     hydra, build_info_cache, build)
        #     job = build_info.get('job', [])
        #     if job in job_whitelist:
        #         filtered_builds2.append(build)
    with tqdm(total=len(filtered_builds1), desc="progress_bar_desc", unit="builds") as pbar:
        for build1 in filtered_builds1:
            build_info1 = cache_utils.get_cached_or_fetch_build_info(
                hydra, build_info_cache, build1)
            job1 = build_info1.get('job', '')
            if job1 not in job_whitelist:
                continue
            # if job1 != "system-manager-profile-dev.x86_64-linux":
            #     continue
            for build2 in builds2:
                build_info2 = cache_utils.get_cached_or_fetch_build_info(
                    hydra, build_info_cache, build2)
                job2 = build_info2.get('job', '')
                if job1 == job2:
                    break
            out_path1 = build_info1.get('outPath', [])
            store_name1 = out_path1[len("/nix/store/"):]
            out_path2 = build_info2.get('outPath', [])
            store_name2 = out_path2[len("/nix/store/"):]
            entropy_compare_jobset_recursive(
                hydra, job1, store_path_entropy_dict, store_name1, store_name2)
            pbar.update(1)


def entropy_compare_jobset_recursive(hydra, job, store_path_entropy_dict, store_name1, store_name2, path=()):

    (references1, _) = get_references_and_file_size_from_store_path(
        hydra, store_name1)
    (references2, _) = get_references_and_file_size_from_store_path(
        hydra, store_name2)

    grouped_items = compare_and_group_references(references1, references2)

    # if "screen-shell" in store_name1:
    #     print(f"references: {references1}")

    # if "screen-rc" in store_name1:
    #     print(f"store_name1: {store_name1}, store_name2: {store_name2}")
    #     print(f"path: {path}\n")

    store_name1_without_timestamp = remove_timestamp(store_name1)
    store_name2_without_timestamp = remove_timestamp(store_name2)

    if store_name1_without_timestamp == store_name2_without_timestamp:
        return

    if store_name1_without_timestamp.split('-', 1)[1] not in store_path_entropy_dict:
        store_path_entropy_dict[store_name1_without_timestamp.split(
            '-', 1)[1]] = 0
        # print(f"len(store_path_entropy_dict): {len(store_path_entropy_dict)}")
    else:
        store_path_entropy_dict[store_name1_without_timestamp.split(
            '-', 1)[1]] = store_path_entropy_dict[store_name1_without_timestamp.split('-', 1)[1]] + 1

        # print(
        #     f"incrementing {store_name1_without_timestamp.split('-', 1)[1]}'s entropy value to {store_path_entropy_dict[store_name1_without_timestamp.split('-', 1)[1]]}")

    for key in grouped_items:
        try:
            _store_name1 = grouped_items[key].get('list1', None)[0]
        except IndexError:
            continue
        try:
            _store_name2 = grouped_items[key].get('list2', None)[0]
        except IndexError:
            continue

        # TODO: ??
        if _store_name1 == store_name1 or _store_name1 == store_name2:
            continue
        entropy_compare_jobset_recursive(
            hydra, job, store_path_entropy_dict, _store_name1, _store_name2, path + (key + '-' + store_name1.split('-', 1)[0] + '/' + store_name2.split('-', 1)[0], ))


__all__ = ['get_cached_or_fetch_store_path_entropy_dict']

import time

def main():

    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    while (1):
        try:
            get_cached_or_fetch_store_path_entropy_dict(hydra, "v2-32-devel")
        except Exception as e:
            print(f"Encountered Exception: {e}")
        print(f"calculate entropy node sleeping for 5 minutes...")
        time.sleep(300)

def other_func():

    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    projects = hydra.get_projects()

    for project in projects:
        print(f"{project}")
        jobsets = get_sorted_jobsets(hydra, "v2-32-devel")



    calculate_entropy(hydra, "v2-32-devel", jobsets, jobsets)

if __name__ == "__main__":
    main()

