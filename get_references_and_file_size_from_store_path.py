import cache_utils
from raw_data_utilities import extract_section
from cache_directories import *

def get_references_and_file_size_from_store_path(hydra, store_path):
    parts = store_path.split('-', 1)
    hash_value = parts[0]
    raw_data = cache_utils.get_cached_or_fetch_nar_info(hydra, nar_info_cache, hash_value)
    references = extract_section(raw_data=raw_data, keyword="References")
    file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])
    return (references, file_size)
