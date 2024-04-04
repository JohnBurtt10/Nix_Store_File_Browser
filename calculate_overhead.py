
from write_to_file import write_list_to_file

# TODO: put this in a while loop for while something is added
# calculate overhead based on if a given package would be pulled with an image
# TODO;make this global
def strip_hash(string):
    return string.split('-', 1)[1]


def calculate_overhead(combination, individual_job_package_lists, recursive_dependencies_dict, stripped_non_zero_entropy_packages, recursive_added_job, accounted_for_packages_in_jobs, i, is_creating_zero_entropy_layers, package_file_size, max_recursive_file_size, other_dict, combination_packages_dict, answer, combination_layer_count_dict):
    # packages recursively pulled with this layer
    recursive_added = set()
    overhead = 0
    # recursive file size of packages that are not yet accounted for in a layer
    accounted_for_packages_file_size = 0
    # portion of the world that the packages make up by recursive file size
    relative_accounted_for = 0
    # recursive file size of all packages
    total_recursive_file_size = 0
    # added packages (non recursive)
    selected_packages = []
    #
    _accounted_for_packages_in_jobs = {}

    dqadqd = 0

    
    # print(f"calculating overhead for combination={combination}")
    while (True):

        best = None
        count = 0
        visited_keys = set()
        best_relative_accounted_for = None


        for item, value in stripped_non_zero_entropy_packages.items():
            # shouldn't be needed
            if item in selected_packages:
                continue
            count += 1
            visited_keys.add(item)

            # Print elements that haven't been iterated over yet
            remaining_keys = set(
                stripped_non_zero_entropy_packages.keys()) - visited_keys
            
            # if len(combination) == 7:
            # print(f"len(remaining_keys)={len(remaining_keys)}, count={count}")

            if best_relative_accounted_for:
                # print(f"checking count...")
                if count > 50:
                    break

            dqadqd += 1
            # checking packages themselves
            # TODO: seems unnecessary?
            if strip_hash(item) in recursive_added:
                continue

            _overhead = 0
            _accounted_for_packages_file_size = 0
            _relative_accounted_for = 0
            __accounted_for_packages_in_jobs = {}

            # for job, lisrtt in individual_job_package_lists:
            #     flag = True
            #     # this item has already been considered in this jobs/images overhead
            #     if strip_hash(item) in recursive_added_job[job]:
            #         # if this item has already been considered in this jobs/images overhead, then so has its dependencies
            #         # so we can safely skip here
            #         continue

            #     for gkgege in lisrtt:
            #         # if item == gkgege:
            #         # item is either required by the job something that is depends on item
            #         if item == gkgege or item in recursive_dependencies_dict[gkgege]:
            #             flag = False
            #             break
            #     if flag:
            #         _overhead += package_file_size[item]
            #     else:
            #         # if the item doesn't introduce new overhead, then nothing the item depends on will either because the image/job
            #         # also needs it so we can safely skip here
            #         continue

            #     # checking recursive dependencies of packages
            #     for p in recursive_dependencies_dict[item]:
            #         if p in recursive_added:
            #             continue
            #         flag = True

            #         # this p has already been considered in this jobs/images overhead
            #         if strip_hash(p) in recursive_added_job[job]:
            #             continue

            #         for gkgege in lisrtt:
            #             # p is either required by the job something that is depends on p
            #             if p == gkgege or p in recursive_dependencies_dict[gkgege]:
            #                 # if p == gkgege:
            #                 flag = False
            #                 break

            #         if flag:
            #             _overhead += package_file_size[p]

            if _overhead > 15000:
                continue
            
            # if this would be starting a new layer, don't add a package that isn't needed for every job in the combination
            if (combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination]) not in answer and _overhead != 0:
                continue

            continue_flag = False
            for job, lisrtt in individual_job_package_lists:
                unique_packages = set()
                __accounted_for_package_file_size = 0
                total_file_size = 0
                __accounted_for_packages_in_jobs[job] = set()

                for ddd in lisrtt:
                    unique_packages.add((ddd))
                    for p in recursive_dependencies_dict[ddd]:
                        unique_packages.add((p))

                if job not in _accounted_for_packages_in_jobs:
                    _accounted_for_packages_in_jobs[job] = set()

                if not len(unique_packages):
                    continue

                for fgwfiow in unique_packages:
                    total_file_size += package_file_size[fgwfiow]


                # double counting here
                if strip_hash(item) not in accounted_for_packages_in_jobs[job] and item in unique_packages and strip_hash(item) not in _accounted_for_packages_in_jobs[job]:
                    __accounted_for_package_file_size += package_file_size[item]
                    __accounted_for_packages_in_jobs[job].add(strip_hash(item))

                for p in recursive_dependencies_dict[item]:
                    if strip_hash(p) not in accounted_for_packages_in_jobs[job] and p in unique_packages and strip_hash(p) not in _accounted_for_packages_in_jobs[job]:
                        __accounted_for_package_file_size += package_file_size[p]
                        __accounted_for_packages_in_jobs[job].add(strip_hash(p))

                # if the package doesn't account for anything for a job in the combination, we don't want to start a layer with it
                if (combination, is_creating_zero_entropy_layers, combination_layer_count_dict[combination]) not in answer and __accounted_for_package_file_size == 0:
                    continue_flag = True
                    break

                _accounted_for_packages_file_size += __accounted_for_package_file_size

                _relative_accounted_for += __accounted_for_package_file_size / total_file_size
            
            if continue_flag:
                continue


            if (best_relative_accounted_for is not None and _relative_accounted_for > best_relative_accounted_for) or (best_relative_accounted_for is None and ((_overhead == 0 and _relative_accounted_for >= 0.005) or (_overhead < 500000 and _relative_accounted_for >= 0.01))):

                count = 0

                best = (item, _accounted_for_packages_file_size, _relative_accounted_for, _overhead, __accounted_for_packages_in_jobs)

                best_relative_accounted_for = _relative_accounted_for

                # print(f"new best_relative_acoutned_for={best_relative_accounted_for}")

                # break

            else:
                #TODO: fix this
                if item in combination_packages_dict[(
                    combination, is_creating_zero_entropy_layers)]:
                    combination_packages_dict[(
                        combination, is_creating_zero_entropy_layers)].pop(item)

        if best is None:
            break
        (item, _accounted_for_packages_file_size, _relative_accounted_for, _overhead, __accounted_for_packages_in_jobs) = best
        # print(f"item={item}, _accounted_for_packages_file_size={_accounted_for_packages_file_size}, _relative_accounted_for={_relative_accounted_for}, _overhead={_overhead}")
        if (_overhead == 0 and _relative_accounted_for >= 0.005) or (_overhead < 500000 and _relative_accounted_for >= 0.01):
            for job, _ in individual_job_package_lists:

                try:
                    _accounted_for_packages_in_jobs[job].update(
                        __accounted_for_packages_in_jobs[job])
                    
                except Exception as e:
                    print(f"Exception: {e}, {job in _accounted_for_packages_in_jobs}, {job in __accounted_for_packages_in_jobs}")

            accounted_for_packages_file_size += _accounted_for_packages_file_size
            relative_accounted_for += _relative_accounted_for
            total_recursive_file_size += package_file_size[item]
            selected_packages.append((item))

            for p in recursive_dependencies_dict[item]:
                recursive_added.add(strip_hash(p))
                total_recursive_file_size += package_file_size[p]
            recursive_added.add(item)
            overhead += _overhead

            if total_recursive_file_size > max_recursive_file_size:
                break


            # only one package per layer
            
            break

            
    return overhead, accounted_for_packages_file_size, selected_packages, relative_accounted_for, total_recursive_file_size
