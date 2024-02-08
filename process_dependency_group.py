from raw_data_utilities import extract_section
from has_timestamp import has_timestamp
from update_hash_tables import update_hash_tables
import cache_utils
from cache_directories import *


def process_dependency_group(hydra,
                             recursive_mode_enabled,
                             raw_data,
                             dependency_store_path_dict,
                             job,
                             jobset,
                             store_path_hash_dict,
                             store_path_entropy_dict,
                             store_path_file_size_dict,
                             reverse_dependencies_dict,
                             dependency_all_store_path_dict,
                             store_path_jobsets_dict):

    references = extract_section(raw_data=raw_data, keyword="References")

    for reference in references:
        parts = reference.split('-', 1)
        hash_value = parts[0]
        _process_dependency_group(hydra,
                                  recursive_mode_enabled,
                                  hash_value,
                                  dependency_store_path_dict,
                                  job,
                                  jobset,
                                  store_path_hash_dict,
                                  store_path_entropy_dict,
                                  store_path_file_size_dict,
                                  reverse_dependencies_dict,
                                  dependency_all_store_path_dict,
                                  store_path_jobsets_dict)


def _process_dependency_group(hydra,
                              recursive_mode_enabled,
                              hash_value,
                              dependency_store_path_dict,
                              job,
                              jobset,
                              store_path_hash_dict,
                              store_path_entropy_dict,
                              store_path_file_size_dict,
                              reverse_dependencies_dict,
                              dependency_all_store_path_dict,
                              store_path_jobsets_dict):

    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash_value)
    references = extract_section(raw_data=raw_data, keyword="References")
    file_size = extract_section(raw_data=raw_data, keyword="FileSize")
    # file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])
    grouped_items = {}
    for dependency in references:
        # Group items based on the equality of the second part after splitting by '-'
        parts = dependency.split('-', 1)
        hash = parts[0]
        # Using the second part as the grouping criterion
        key = parts[1] if len(parts) > 1 else dependency
        grouped_items.setdefault(key, []).append(dependency)
        dependency_store_path_dict[key] = hash
        # if recursive_mode_enabled:
        #     _process_dependency_group(hydra,
        #                               recursive_mode_enabled,
        #                               hash,
        #                               dependency_store_path_dict,
        #                               job,
        #                               jobset,
        #                               store_path_hash_dict,
        #                               store_path_entropy_dict,
        #                               store_path_file_size_dict,
        #                               reverse_dependencies_dict,
        #                               dependency_all_store_path_dict,
        #                               store_path_jobsets_dict)

    for key, group in grouped_items.items():

        # temporary measure against weird timestamp packages
        if has_timestamp(dependency):
            continue

        update_hash_tables(job,
                           jobset,
                           key,
                           group,
                           store_path_hash_dict,
                           store_path_entropy_dict,
                           store_path_file_size_dict,
                           reverse_dependencies_dict,
                           dependency_all_store_path_dict,
                           store_path_jobsets_dict,
                           file_size)
