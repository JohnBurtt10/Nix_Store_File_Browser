from .get_file_size_from_store_path import get_file_size_from_store_path

def get_file_sizes_by_path(all_packages, hydra, recursive_dependencies_dict):
    package_file_size = {}

    unique_packge_world_file_size = 0

    for item in all_packages:
        file_size = get_file_size_from_store_path(
            hydra, item)
        package_file_size[item] = file_size
        if item.split('-', 1)[1] not in package_file_size:
            package_file_size[item.split(
                '-', 1)[1]] = file_size
            unique_packge_world_file_size += file_size
        # if not recursive_dependencies_dict[item]:
        #     continue
        for p in recursive_dependencies_dict[item]:
            file_size = get_file_size_from_store_path(
                hydra, p)
            package_file_size[p] = file_size
            if p.split('-', 1)[1] not in package_file_size:
                package_file_size[p.split(
                    '-', 1)[1]] = file_size
                unique_packge_world_file_size += file_size

    return package_file_size, unique_packge_world_file_size