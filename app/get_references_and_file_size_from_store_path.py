from . import cache_utils
from .raw_data_utilities import extract_section
from .cache_directories import *
from .hydra_client import Hydra


def get_references_and_file_size_from_store_path(hydra, store_path):
    if store_path is None:
        return ([], None)
    parts = store_path.split('-', 1)
    hash_value = parts[0]
    raw_data = cache_utils.get_cached_or_fetch_nar_info(
        hydra, nar_info_cache, hash_value, False)
    references = extract_section(raw_data=raw_data, keyword="References")
    file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])
    return (references, file_size)

def main():
    # Example usage of Hydra class
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)

    # Example: Logging in
    hydra.login(username="administrator", password="clearp@th")
    (get_references_and_file_size_from_store_path(hydra, "h22rpb6wa2mn21qppml8f5wgp0i0s2bi-image-sim-gazebo.json"))


if __name__ == "__main__":
    main()