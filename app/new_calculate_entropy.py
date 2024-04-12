from tqdm import tqdm
from .cache_directories import *
from .hydra_client import Hydra  # Import specific objects from hydra_client module
from .get_sorted_jobsets import get_sorted_jobsets
from . import cache_utils
from .get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path
from .remove_timestamp import remove_timestamp
from .compare_and_group_references import compare_and_group_references
from .get_jobset_builds import get_jobset_builds
from .get_best_partial_jobsets_cache_key import get_best_partial_jobsets_cache_key
from .job_whitelist import job_whitelist
from .sum_dicts import sum_dicts
import pickle
from .update_file_variable_value import update_file_variable_value
from .traverse_jobset import traverse_jobset as tra
from .raw_data_utilities import extract_section

def retrieve_and_check_cancel():
    # Retrieve variables from the file
    with open('data.pkl', 'rb') as f:  # Open file in binary read mode
        loaded_data = pickle.load(f)
    if loaded_data['proceed']:
        update_file_variable_value('proceed', False)
        return True
    if loaded_data['cancel']:
        return True
    
def report_error(error):
    pass

def _populate_references(raw_data, references_dict, jobset, job):
    store_path = extract_section(raw_data=raw_data, keyword="StorePath")[0]
    references = extract_section(raw_data=raw_data, keyword="References")
    references_dict[store_path[len("/nix/store/"):]] = references

def populate_references(hydra, project_name, jobset, references_dict, visited):
     
     def update_progress(task, progress):
         pass
     
     def report_error(error):
         pass
     tra(hydra, update_progress, report_error, project_name, jobset,
                            lambda job, raw_data: _populate_references(
                                raw_data, references_dict, jobset, job), 
                                only_visit_once_enabled=True,
                                recursive_mode_enabled=True,
                                whitelist_enabled=False,
                                exponential_back_off_enabled=False,
                                visited=visited,
                                cancellable=True)

def get_cached_or_fetch_store_path_entropy_dict(hydra, project_name, update_progress, approximate_uncalculated_jobsets_mode_enabled=False, check_cancel_enabled=True):

    print(f"project_name={project_name}")

    store_path_entropy_dict = {}

    fokwfko = {}

    sorted_jobsets = get_sorted_jobsets(hydra, project_name)

    partial_jobset_lists = list(store_path_entropy_dict_cache.iterkeys())

    (best_list, remaining_jobsets) = get_best_partial_jobsets_cache_key(
        sorted_jobsets, partial_jobset_lists)

    if best_list is not None:
        partial_cache_key = tuple(best_list)

        # return store_path_entropy_dict_cache[partial_cache_key]

        if partial_cache_key in store_path_entropy_dict_cache:
            store_path_entropy_dict, fokwfko = store_path_entropy_dict_cache[partial_cache_key]
            if approximate_uncalculated_jobsets_mode_enabled:
                print(f"approximating the entropy for the remaining {len(sorted_jobsets)-len(best_list)}/{len(sorted_jobsets)} jobsets...")
                factor = len(sorted_jobsets)/len(best_list)
                for key in store_path_entropy_dict:
                    store_path_entropy_dict[key] = round(store_path_entropy_dict[key] * factor)
                return store_path_entropy_dict, fokwfko

    return calculate_entropy(hydra,
                             project_name,
                             sorted_jobsets,
                             remaining_jobsets,
                             update_progress,
                             best_list,
                             store_path_entropy_dict,
                             fokwfko,
                             approximate_uncalculated_jobsets_mode_enabled,
                             check_cancel_enabled)


def calculate_entropy(hydra,
                      project_name,
                      sorted_jobsets,
                      remaining_jobsets,
                      update_progress,
                      best_list=None,
                      store_path_entropy_dict={},
                      fokwfko = {},
                      approximate_uncalculated_jobsets_mode_enabled=False,
                      check_cancel_enabled=True,
                      recursive_mode_enabled=False,
                      exponential_back_off_enabled=False):

    processed_jobsets = []
    
    if best_list is not None:
        processed_jobsets = list(best_list)

    current_iteration = 0
    for jobset in processed_jobsets:
        current_iteration += len(get_jobset_builds(hydra, project_name, jobset))

    total_iterations = 0
    for jobset in sorted_jobsets:
        total_iterations += len(get_jobset_builds(hydra, project_name, jobset))

    update_progress("Calculating entropy...", 100*(current_iteration/total_iterations))

    initial = 0 if best_list is None else len(best_list)

    references_dict = {}
    
    visited = []

    # populate_references(hydra, project_name, remaining_jobsets[0], references_dict, visited)

    with tqdm(initial=initial, total=len(sorted_jobsets), desc="Computing entropy", unit="jobsets") as pbar:
        for jobset in remaining_jobsets:

            if remaining_jobsets.index(jobset) < len(remaining_jobsets) - 1:
                next_jobset = remaining_jobsets[remaining_jobsets.index(
                    jobset) + 1]
            else:
                break

            print(f"jobset={jobset}, next_jobset={next_jobset}")
            
            # populate_references(hydra, project_name, next_jobset, references_dict, visited)

            _store_path_entropy_dict = {}
            if not traverse_jobset(hydra, project_name, jobset, next_jobset,
                            _store_path_entropy_dict, update_progress, current_iteration, total_iterations, references_dict, check_cancel_enabled):
                
                update_progress("", 0)
                print(f"Proceeding without remaining {len(sorted_jobsets)-(pbar.n+initial)} jobsets...")
                return store_path_entropy_dict, fokwfko
            
            for key in _store_path_entropy_dict:
                for k in _store_path_entropy_dict:
                    if key != k:
                        if key in fokwfko:
                            if k in fokwfko[key]:
                                fokwfko[key][k] += 1
                            else:
                                fokwfko[key][k] = 1
                        else:
                            fokwfko[key] = {}
                            fokwfko[key][k] = 1

            store_path_entropy_dict = sum_dicts(store_path_entropy_dict, _store_path_entropy_dict)

            processed_jobsets.append(jobset)
            cache_key = tuple(processed_jobsets)
            store_path_entropy_dict_cache[cache_key] = (store_path_entropy_dict, fokwfko)
            pbar.update(1)

            current_iteration = 0
            for jobset in remaining_jobsets:
                current_iteration += len(get_jobset_builds(hydra, project_name, jobset))
            
            if False and approximate_uncalculated_jobsets_mode_enabled:
                print(f"approximating the entropy for the remaining {len(sorted_jobsets)-len(processed_jobsets)}/{len(sorted_jobsets)} jobsets...")
                factor = len(sorted_jobsets)/len(processed_jobsets)
                for key in store_path_entropy_dict:
                    store_path_entropy_dict[key] = round(store_path_entropy_dict[key] * factor)
                update_progress("", 0)
                return store_path_entropy_dict

    # cache_key = tuple(sorted_jobsets)
    # store_path_entropy_dict_cache[cache_key] = store_path_entropy_dict
    update_progress("", 0)
    return store_path_entropy_dict, fokwfko


def traverse_jobset(hydra, project_name, jobset1, jobset2, store_path_entropy_dict, update_progress, current_iteration, total_iterations, references_dict, check_cancel_enabled):
    # [487521, 487524, 487530, 487554,...
    builds1 = get_jobset_builds(hydra, project_name, jobset1)
    builds2 = get_jobset_builds(hydra, project_name, jobset2)
    filtered_builds1 = []

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
            found = False
            for build2 in builds2:
                build_info2 = cache_utils.get_cached_or_fetch_build_info(
                    hydra, build_info_cache, build2)
                job2 = build_info2.get('job', '')
                if job1 == job2:
                    found = True
                    break
            if not found:
                continue
            out_path1 = build_info1.get('outPath', [])
            store_name1 = out_path1[len("/nix/store/"):]
            out_path2 = build_info2.get('outPath', [])
            store_name2 = out_path2[len("/nix/store/"):]
            print(f"store_path={store_name1}")
            if not entropy_compare_jobset_recursive(
                hydra, job1, store_path_entropy_dict, store_name1, store_name2, references_dict, check_cancel_enabled):
                return False
            pbar.update(1)
            
            update_progress("Calculating entropy...", 100*(current_iteration+pbar.n)/total_iterations)
    
    return True


def entropy_compare_jobset_recursive(hydra, job, store_path_entropy_dict, store_name1, store_name2, references_dict, check_cancel_enabled, path=(), depth=0):


    # test
    try:
        if store_name1 in references_dict:
            references1 = references_dict[store_name1]
        else:
            (references1, _) = get_references_and_file_size_from_store_path(hydra, store_name1)
            references_dict[store_name1] = references1
    except:
        print(f"failed to get references for {store_name1}")
        return True
        # (references1, _) = get_references_and_file_size_from_store_path(hydra, store_name1)
    try:
        if store_name2 in references_dict:
            references2 = references_dict[store_name2]
        else:
            (references2, _) = get_references_and_file_size_from_store_path(hydra, store_name2)
            references_dict[store_name2] = references2
        # references2 = references_dict[store_name2]
    except:
        print(f"failed to get references for {store_name2}")
        return True       
        # (references2, _) = get_references_and_file_size_from_store_path(hydra, store_name2)

    grouped_items = compare_and_group_references(references1, references2)

    if check_cancel_enabled and retrieve_and_check_cancel():
        return False

    # if "screen-shell" in store_name1:
    #     print(f"references: {references1}")

    # if "screen-rc" in store_name1:
    print(f"store_name1: {store_name1}")
    # print(f"path: {path}\n")

    store_name1_without_timestamp = remove_timestamp(store_name1)
    store_name2_without_timestamp = remove_timestamp(store_name2)

    if store_name1_without_timestamp == store_name2_without_timestamp:
        return

    if store_name1_without_timestamp.split('-', 1)[1] not in store_path_entropy_dict:
        store_path_entropy_dict[store_name1_without_timestamp.split(
            '-', 1)[1]] = 1
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
        if depth == 1:
            return True
        if not entropy_compare_jobset_recursive(
            hydra, job, store_path_entropy_dict, _store_name1, _store_name2, references_dict, check_cancel_enabled, path + (key + '-' + store_name1.split('-', 1)[0] + '/' + store_name2.split('-', 1)[0], ), depth+1):
            return False
    
    return True


__all__ = ['get_cached_or_fetch_store_path_entropy_dict']

import time

def main():

    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    projects = hydra.get_projects()

    def update_progress(task, progress):
        pass

    while (1):
        try:
            for project in projects:
                get_cached_or_fetch_store_path_entropy_dict(hydra, "v2-34-devel", update_progress, approximate_uncalculated_jobsets_mode_enabled=False, check_cancel_enabled=False)
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

    def update_progress(task, progress):
        pass

    entropy, other = get_cached_or_fetch_store_path_entropy_dict(hydra, "v2-32-devel", update_progress, approximate_uncalculated_jobsets_mode_enabled=False, check_cancel_enabled=False)

    # for key in other:
    #     for k in other[key]:
    #         print(f"{other[key][k]/entropy[key]}")

if __name__ == "__main__":
    other_func()

