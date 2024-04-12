from .get_references_and_file_size_from_store_path import get_references_and_file_size_from_store_path
from .cache_directories import store_path_file_size_cache

def get_file_size_from_store_path(hydra, store_path):
    if store_path in store_path_file_size_cache:
        return store_path_file_size_cache[store_path]
    _, file_size = get_references_and_file_size_from_store_path(hydra, store_path)
    store_path_file_size_cache[store_path] = file_size
    return file_size