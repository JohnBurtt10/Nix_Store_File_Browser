from . import cache_utils
from .cache_directories import *
from .raw_data_utilities import extract_section
from tqdm import tqdm
import time
from .job_whitelist import job_whitelist
from .has_timestamp import has_timestamp
import pickle
from .update_file_variable_value import update_file_variable_value



def retrieve_and_check_cancel():
    # Retrieve variables from the file
    with open('data.pkl', 'rb') as f:  # Open file in binary read mode
        loaded_data = pickle.load(f)
    if loaded_data['proceed']:
        update_file_variable_value('proceed', False)
        return True
    if loaded_data['cancel']:
        return True


def traverse_jobset(hydra, update_progress, report_error, project_name, jobset, func, recursive_mode_enabled=False,
                    exponential_back_off_enabled=False, only_visit_once_enabled=False, progress_bar_enabled=False,
                    whitelist_enabled=False, progress_bar_desc="Default progress bar desc", visited_store_paths=[], jobs=[],
                    cancellable=False, unique_packages_enabled=True, visited_packages=set()):
    """
    Traverse a jobset and apply a function to each build.

    Args:
    - hydra (Hydra): The hydra information.
    - project_name (str): The name of the project.
    - jobset (str): The jobset information.
    - func (callable): The function to apply to each build.
    - recursive_mode_enabled (bool): Flag indicating whether to traverse recursively.
    - exponential_back_off_enabled (bool): Flag indicating whether to use exponential back-off.
    - only_visit_once_enabled (bool): Flag indicating whether to visit a given store path more than once.
    - progress_bar_enabled (bool): Flag indicating whether to show a progress bar.
    - progress_bar_desc (str): Description for the progress bar.
    - visited_store_paths (list): Store paths already visted.
    - jobs (list): Which jobs to consider.
    - cancellable (bool): Flag indicating whether this operation can be called via the UI 'Cancel' button. 
    - unique_packages_enabled (bool): Flag indicating whether to visit a given package more than once.
      visited_packages (set): Packages already visited.

    Returns:
    - None

    Note:
    The function uses caching utilities to get information about jobset evaluations and build details.
    It then iterates through the builds, applying the provided function to each build.

    Example:
    ```
    hydra =
    project_name = "example_project"
    jobset = "example_jobset"
    func = lambda x: print(x)
    traverse_jobset(hydra, project_name, jobset, func, recursive_mode_enabled=True, exponential_back_off_enabled=True, progress_bar_enabled=True, progress_bar_desc="Traversing jobset")
    ```

    """
    data = cache_utils.get_cached_or_fetch_jobset_evals(
        hydra, jobset_evals_cache, project_name, jobset)
    # Access builds information
    evals_info = data.get('evals', [])

    # print(f"{project_name}, {jobset}, {jobs}")

    # for eval_info in evals_info:
    while (1):
        try:
            builds = evals_info[0].get('builds', [])
            break
        except IndexError as e:
            report_error(1)
            print(
                f"encountered {e} while trying to get builds, sleeping for 5 seconds and then trying again...")
            time.sleep(5)

    my_list = []

    filtered_builds = []

    # if you remove this it reuses the same one
    visited_store_paths = []

    if whitelist_enabled:

        for build in builds:
            build_info = cache_utils.get_cached_or_fetch_build_info(
                hydra, build_info_cache, build)
            job = build_info.get('job', [])
            if job in job_whitelist and (not jobs or job in jobs):
                filtered_builds.append(build)

    else:
        filtered_builds = builds

    # progress = {'task': 'getting recursive dependencies...', 'progress': 0}
    # # Serialize JSON to bytes before yielding
    # yield json.dumps(progress) + '\n'
    if progress_bar_enabled:
        if not jobs:
            update_progress(
                "Getting recursive dependencies for all jobs...", 0)
        else:
            if len(jobs) == 1:
                result_string = jobs[0]
            else:
                # Joining all elements except the last one with commas
                result_string = ', '.join(jobs[:-1])
                # Adding 'and' before the last element
                result_string += ', and ' + jobs[-1]

            update_progress(
                "Getting recursive dependencies for " + result_string + "...", 0)
        # [487521, 487524, 487530, 487554,...
    with tqdm(total=len(filtered_builds), disable=not progress_bar_enabled, desc=progress_bar_desc, unit="builds") as pbar:
        for build in filtered_builds:
            build_info = cache_utils.get_cached_or_fetch_build_info(
                hydra, build_info_cache, build)
            out_path = build_info.get('outPath', [])
            job = build_info.get('job', [])
            my_list.append(job)
            # try:
            input_string = out_path
            # Removing "/nix/store" from the beginning of the string
            input_string = input_string[len("/nix/store/"):]

            if cancellable and retrieve_and_check_cancel():
                return False

            traverse_jobset_recursive(
                hydra, func, job, input_string, recursive_mode_enabled, exponential_back_off_enabled, only_visit_once_enabled,
                whitelist_enabled, 0, visited_store_paths, unique_packages_enabled, visited_packages)
            pbar.update(1)
            if progress_bar_enabled:
                if not jobs:
                    update_progress(
                        "Getting recursive dependencies for all jobs...", 100*pbar.n/len(filtered_builds))
                else:
                    if len(jobs) == 1:
                        result_string = jobs[0]
                    else:
                        # Joining all elements except the last one with commas
                        result_string = ', '.join(jobs[:-1])
                        # Adding 'and' before the last element
                        result_string += ', and ' + jobs[-1]

                    update_progress("Getting recursive dependencies for " +
                                    result_string + "...", 100*pbar.n/len(filtered_builds))

            if cancellable and retrieve_and_check_cancel():
                return False

    return True


def check(input_string):
    words = ["robot", "debug", "dev", "Ros1", "Ros2",
             "sim", "merged", "otto", "push", "gazebo", "copy-to", "outlinks", "virtualRobot", "image-testrunner.json", "sdk", "skopeo", "appliance_proxy"]
    parts = input_string.split('-')
    if len(parts) == 2 and len(parts[1]) > 50:
        return False
    if has_timestamp(input_string):
        return False
    for word in words:
        if word in input_string:
            return False
    return True


def strip_hash(string):
    return string.split('-', 1)[1]


def traverse_jobset_recursive(hydra, func, job, input_string, recursive_mode_enabled, exponential_back_off_enabled, only_visit_once_enabled,
                              whitelist_enabled, depth, visited_store_paths, unique_packages_enabled, visited_packages):
    # filter by timestamp
    # go through images and make groups based on common
    # Splitting the string based on the first hyphen
    parts = input_string.split('-', 1)
    # Extracting the hash and the stuff after the first hyphen
    hash_value = parts[0]
    # try:
    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash_value, exponential_back_off_enabled)
    if raw_data is None:
        return
    if not whitelist_enabled or check(input_string):
        func(job, raw_data)
    references = extract_section(raw_data=raw_data, keyword="References")
    if recursive_mode_enabled:
        for reference in references:
            if reference not in input_string:
                # TODO: first part of the AND can be removed
                # only visit a package once (i.e. cpr_base_navigation)
                if unique_packages_enabled:
                    if (strip_hash(reference) in visited_packages) and (reference not in visited_store_paths):
                        continue
                # only visit a store path once (i.e. bc3svx54m6q6xwqy83h3kb2favkn9rlp-cpr_base_navigation)
                if only_visit_once_enabled:
                    if reference in visited_store_paths:
                        continue
                    visited_packages.add(strip_hash(reference))
                    visited_store_paths.append(reference)
                    traverse_jobset_recursive(
                        hydra, func, job, reference, recursive_mode_enabled, exponential_back_off_enabled, only_visit_once_enabled, whitelist_enabled,
                        depth+1, visited_store_paths, unique_packages_enabled, visited_packages)
