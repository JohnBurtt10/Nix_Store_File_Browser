from tqdm import tqdm
from traverse_jobset import traverse_jobset
from cache_directories import *
from hydra_client import Hydra
from get_sorted_jobsets import get_sorted_jobsets
from raw_data_utilities import extract_section
from group_items import group_items


class RawDataNullException(Exception):
    pass


def update_store_path_hash_dict(raw_data,
                                job,
                                _store_path_hash_dict,
                                _store_path_entropy_dict):

    if raw_data is None:
        raise RawDataNullException("Raw data is None")

    references = extract_section(raw_data=raw_data, keyword="References")
    store_path_hash_dict = _store_path_hash_dict
    store_path_entropy_dict = _store_path_entropy_dict

    grouped_items = group_items(references, {})

    for key, group in grouped_items.items():

        dependency = key

        if job in store_path_hash_dict:
            if dependency in store_path_hash_dict[job]:
                if store_path_hash_dict[job][dependency] != group:
                    # TODO: untested
                    if dependency not in store_path_entropy_dict:
                        store_path_entropy_dict[dependency] = 0
                    else:
                        store_path_entropy_dict[dependency] = store_path_entropy_dict[dependency] + 1
                    store_path_hash_dict[job][dependency] = group
            else:
                # init dicts
                store_path_hash_dict[job][dependency] = group
        else:
            store_path_hash_dict[job] = {}
            store_path_hash_dict[job][dependency] = group


def calculate_entropy(hydra,
                      project_name,
                      sorted_jobsets,
                      remaining_jobsets,
                      best_list=None,
                      store_path_hash_dict={},
                      store_path_entropy_dict={},
                      recursive_mode_enabled=False,
                      exponential_back_off_enabled=False):
    # TODO: ??
    dependency_store_path_dict = {}
    with tqdm(initial=0 if best_list is None else len(best_list), total=len(sorted_jobsets), desc="Computing entropy", unit="jobsets") as pbar:
        for jobset in remaining_jobsets:
            traverse_jobset(hydra, project_name, jobset,
                            lambda job, raw_data: update_store_path_hash_dict(raw_data, job, store_path_hash_dict, store_path_entropy_dict), recursive_mode_enabled, exponential_back_off_enabled, True)
            pbar.update(1)

    cache_key = tuple(sorted_jobsets)
    # store_path_entropy_dict_cache[cache_key] = (
    #     store_path_entropy_dict, store_path_hash_dict)
    return store_path_entropy_dict



def main():

    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")

    sorted_jobsets = get_sorted_jobsets(hydra, "v2-32-devel")

    calculate_entropy(hydra, "v2-32-devel", sorted_jobsets, sorted_jobsets)


if __name__ == "__main__":
    main()
