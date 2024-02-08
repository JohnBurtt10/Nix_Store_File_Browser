from diskcache import Cache
my_cache_directory = "cache/my_cache_directory"
my_out_path_cache_directory = "cache/my_out_path_cache_directory"
job_cache_directory = "cache/job_cache_directory"
jobset_cache_directory = "cache/jobset_cache_directory"
builds_cache_directory = "cache/builds_cache_directory"
evals_info_cache_directory = "cache/evals_info_cache_directory"
first_sort_cache_directory = "cache/first_sort_cache_directory"
jobset_evals_cache_directory = "cache/jobset_evals_cache_directory"
build_info_cache_directory = "cache/build_info_cache_directory"
nar_info_cache_directory = "cache/nar_info_cache_directory"
count_ancestor_cache_directory = "cache/count_ancestor_cache_directory"
dependency_weight_cache_directory = "cache/dependency_weight_cache_directory"
#TODO: name?
update_dicts_cache_directory = "cache/update_dicts_cache_directory"
compare_and_process_builds_cache_directory = "cache/compare_and_process_builds_cache_directory"
compare_and_group_job_cache_directory = "cache/compare_and_group_job_cache_directory"
process_and_compare_paths_cache_directory = "cache/process_and_compare_paths_cache_directory"
get_job_references_dict_cache_directory = "cache/get_job_references_dict_cache_directory"
compare_and_group_references_cache_directory = "cache/compare_and_group_references_cache_directory"
handle_compare_and_group_references_cache_directory = "cache/handle_compare_and_group_references_cache_directory"
count_descentdants_cache_directory = "cache/count_descentdants_cache_directory"
reverse_dependency_weight_cache_directory = "cache/reverse_dependency_weight_cache_directory"
_calculate_dependency_weight_cache_directory = "cache/_calculate_dependency_weight_cache/directory"
cache = Cache(my_cache_directory)
dependency_weight_cache = Cache(dependency_weight_cache_directory)
first_sort_cache = Cache(first_sort_cache_directory)
count_ancestor_cache = Cache(count_ancestor_cache_directory)
jobset_evals_cache = Cache(jobset_evals_cache_directory)
build_info_cache = Cache(build_info_cache_directory)
nar_info_cache = Cache(nar_info_cache_directory, threaded=True)
out_path_cache = Cache(my_out_path_cache_directory)
job_cache = Cache(job_cache_directory)
jobset_cache = Cache(jobset_cache_directory)
evals_info_cache = Cache(evals_info_cache_directory)
builds_cache = Cache(builds_cache_directory)
update_dicts_cache = Cache(update_dicts_cache_directory)
compare_and_process_builds_cache = Cache(compare_and_process_builds_cache_directory)
compare_and_group_job_cache = Cache(compare_and_group_job_cache_directory)
process_and_compare_paths_cache = Cache(process_and_compare_paths_cache_directory)
get_job_references_dict_cache = Cache(get_job_references_dict_cache_directory)
compare_and_group_references_cache = Cache(compare_and_group_references_cache_directory)
handle_compare_and_group_references_cache = Cache(handle_compare_and_group_references_cache_directory)
count_descentdants_cache = Cache(count_descentdants_cache_directory)
reverse_dependency_weight_cache = Cache(reverse_dependency_weight_cache_directory)
_calculate_dependency_weight_cache = Cache(_calculate_dependency_weight_cache_directory)

# Define __all__ to include all names
__all__ = [
    "my_cache_directory",
    "my_out_path_cache_directory",
    "job_cache_directory",
    "jobset_cache_directory",
    "builds_cache_directory",
    "evals_info_cache_directory",
    "first_sort_cache_directory",
    "jobset_evals_cache_directory",
    "build_info_cache_directory",
    "nar_info_cache_directory",
    "count_ancestor_cache_directory",
    "dependency_weight_cache_directory",
    "update_dicts_cache_directory",
    "compare_and_process_builds_cache_directory",
    "compare_and_group_job_cache_directory",
    "process_and_compare_paths_cache_directory",
    "get_job_references_dict_cache_directory",
    "cache",
    "dependency_weight_cache",
    "first_sort_cache",
    "count_ancestor_cache",
    "jobset_evals_cache",
    "build_info_cache",
    "nar_info_cache",
    "out_path_cache",
    "job_cache",
    "jobset_cache",
    "evals_info_cache",
    "builds_cache",
    "update_dicts_cache",
    "compare_and_process_builds_cache",
    "compare_and_group_job_cache",
    "process_and_compare_paths_cache",
    "get_job_references_dict_cache",
    "compare_and_group_references_cache",
    "handle_compare_and_group_references_cache",
    "count_descentdants_cache", 
    "reverse_dependency_weight_cache",
    "_calculate_dependency_weight_cache"
]
