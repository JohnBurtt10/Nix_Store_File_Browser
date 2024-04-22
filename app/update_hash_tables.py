# TODO: break this into multiple methods
# TODO: same name?
# TODO: dependency tree for packages
def update_hash_tables(job,
                       jobset,
                       dependency,
                       group,
                       store_path_hash_dict,
                       store_path_entropy_dict,
                       store_path_file_size_dict,
                       reverse_dependencies_dict,
                       dependency_all_store_path_dict,
                       store_path_jobsets_dict,
                       file_size):
    input_string = dependency
    # Removing "/nix/store" from the beginning of the string
    input_string = input_string[len("/nix/store"):]

    store_path_file_size_dict[dependency] = int(file_size[0])

    if dependency in store_path_jobsets_dict:
        for store_path in group:
            if store_path in store_path_jobsets_dict[dependency]:
                if jobset not in store_path_jobsets_dict[dependency][store_path]:
                    store_path_jobsets_dict[dependency][store_path].append(
                        jobset)
            else:
                # If store_path is not in the dictionary, create a new entry
                store_path_jobsets_dict[dependency][store_path] = [jobset]
    else:
        # If dependency is not in the dictionary, create a new entry
        store_path_jobsets_dict[dependency] = {}
        for store_path in group:
            if store_path in store_path_jobsets_dict[dependency]:
                if jobset not in store_path_jobsets_dict[dependency][store_path]:
                    store_path_jobsets_dict[dependency][store_path].append(
                        jobset)
            else:
                # If store_path is not in the dictionary, create a new entry
                store_path_jobsets_dict[dependency][store_path] = [jobset]

    if dependency in dependency_all_store_path_dict:
        dependency_all_store_path_dict[dependency] = list(
            set(dependency_all_store_path_dict[dependency]) | set(group))
    else:
        dependency_all_store_path_dict[dependency] = group

    # TODO: change this so that it also has the versions of the job
    if dependency in reverse_dependencies_dict:
        if job in reverse_dependencies_dict[dependency]:
            reverse_dependencies_dict[dependency][job].append(jobset)
        else:
            reverse_dependencies_dict[dependency][job] = [jobset]

    else:
        reverse_dependencies_dict[dependency] = {}
        reverse_dependencies_dict[dependency][job] = [jobset]

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


def update_store_path_jobsets_dict(dependency, store_path_jobsets_dict, group, jobset):
    if dependency in store_path_jobsets_dict:
        for store_path in group:
            if store_path in store_path_jobsets_dict[dependency]:
                if jobset not in store_path_jobsets_dict[dependency][store_path]:
                    store_path_jobsets_dict[dependency][store_path].append(
                        jobset)
            else:
                # If store_path is not in the dictionary, create a new entry
                store_path_jobsets_dict[dependency][store_path] = [jobset]
    else:
        # If dependency is not in the dictionary, create a new entry
        store_path_jobsets_dict[dependency] = {}
        for store_path in group:
            if store_path in store_path_jobsets_dict[dependency]:
                if jobset not in store_path_jobsets_dict[dependency][store_path]:
                    store_path_jobsets_dict[dependency][store_path].append(
                        jobset)
            else:
                # If store_path is not in the dictionary, create a new entry
                store_path_jobsets_dict[dependency][store_path] = [jobset]


def update_dependency_all_store_path_dict(dependency, dependency_all_store_path_dict, group):
    if dependency in dependency_all_store_path_dict:
        dependency_all_store_path_dict[dependency] = list(
            set(dependency_all_store_path_dict[dependency]) | set(group))
    else:
        dependency_all_store_path_dict[dependency] = group


def update_reverse_dependencies_dict(dependency, reverse_dependencies_dict, jobset, job):
    # TODO: change this so that it also has the versions of the job
    if dependency in reverse_dependencies_dict:
        if job in reverse_dependencies_dict[dependency]:
            reverse_dependencies_dict[dependency][job].append(jobset)
        else:
            reverse_dependencies_dict[dependency][job] = [jobset]

    else:
        reverse_dependencies_dict[dependency] = {}
        reverse_dependencies_dict[dependency][job] = [jobset]


def update_store_path_hash_dict(job, store_path_hash_dict, dependency, group, store_path_entropy_dict):
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
