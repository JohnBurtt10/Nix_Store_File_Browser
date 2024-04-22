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
dependency_all_store_path_dict_cache_directory = "cache/dependency_all_store_path_dict_cache_directory"
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
_calculate_dependency_weight_cache_directory = "cache/_calculate_dependency_weight_cache_directory"
store_path_jobsets_dict_cache_directory = "cache/store_path_jobsets_dict_cache_directory"
store_path_entropy_dict_cache_directory = "cache/store_path_entropy_dict_cache_directory"
store_path_file_size_dict_cache_directory = "cache/store_path_file_size_dict_cache_directory"
dependency_store_path_dict_cache_directory = "cache/dependency_store_path_dict_cache_directory"
group_items_cache_directory = "cache/group_items_cache_directory"
reverse_dependencies_dict_cache_directory = "cache/reverse_dependencies_dict_cache_directory"
_get_recursive_dependencies_cache_directory = "cache/_get_recursive_dependencies_cache_directory"
get_recursive_dependencies_cache_directory = "cache/get_recursive_dependencies_cache_directory"
search_for_dependency_cache_directory = "cache/search_for_dependency_cache_directory"
entropy_tree_cache_directory = "cache/entropy_tree_cache_directory"
generate_layers_cache_directory = "cache/generate_layers_cache_directory"
_generate_layers_cache_directory = "cache/_generate_layers_cache_directory"
store_path_file_size_cache_directory = "cache/store_path_file_size_cache_directory"
fetch_and_compare_nix_paths_cache_directory = "cache/fetch_and_compare_nix_paths_cache_directory"
package_file_size_cache_diretory = "cache/package_file_size_directory"
build_info_cache_directory = "cache/build_info_cache_directory"
reference_file_size_dicts_cache_directory = "cache/reference_file_size_dicts_cache_directory"
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
store_path_jobsets_dict_cache = Cache(store_path_jobsets_dict_cache_directory)
dependency_all_store_path_dict_cache = Cache(dependency_all_store_path_dict_cache_directory)
store_path_entropy_dict_cache = Cache(store_path_entropy_dict_cache_directory)
store_path_file_size_dict_cache = Cache(store_path_file_size_dict_cache_directory)
dependency_store_path_dict_cache = Cache(dependency_store_path_dict_cache_directory)
group_items_cache = Cache(group_items_cache_directory)
reverse_dependencies_dict_cache = Cache(reverse_dependencies_dict_cache_directory)
_get_recursive_dependencies_cache = Cache(_get_recursive_dependencies_cache_directory)
get_recursive_dependencies_cache = Cache(get_recursive_dependencies_cache_directory)
search_for_dependency_cache = Cache(search_for_dependency_cache_directory)
entropy_tree_cache = Cache(entropy_tree_cache_directory)
generate_layers_cache = Cache(generate_layers_cache_directory)
_generate_layers_cache = Cache(_generate_layers_cache_directory)
store_path_file_size_cache = Cache(store_path_file_size_cache_directory)
fetch_and_compare_nix_paths_cache = Cache(fetch_and_compare_nix_paths_cache_directory)
package_file_size_cache = Cache(package_file_size_cache_diretory)
reference_file_size_dicts_cache = Cache(reference_file_size_dicts_cache_directory)

# Define __all__ to include all names
__all__ = [
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
    "_calculate_dependency_weight_cache",
    "store_path_jobsets_dict_cache",
    "dependency_all_store_path_dict_cache",
    "store_path_entropy_dict_cache",
    "store_path_file_size_dict_cache",
    "dependency_store_path_dict_cache",
    "group_items_cache",
    "reverse_dependencies_dict_cache",
    "_get_recursive_dependencies_cache",
    "get_recursive_dependencies_cache",
    "search_for_dependency_cache",
    "entropy_tree_cache",
    "_generate_layers_cache",
    "store_path_file_size_cache",
    "fetch_and_compare_nix_paths_cache",
    "generate_layers_cache",
    "package_file_size_cache",
    "build_info_cache",
    "reference_file_size_dicts_cache"
]
