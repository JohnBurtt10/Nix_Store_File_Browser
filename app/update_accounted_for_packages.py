
# TODO: put this in a while loop for while something is added
# calculate overhead based on if a given package would be pulled with an image
# TODO;make this global

def strip_hash(string):
    return string.split('-', 1)[1]


def update_accounted_for_packages(recursive_dependencies_dict, recursive_added_job, accounted_for_packages_in_jobs, selected_packages, other_dict, individual_job_package_lists, package_file_size):
    # packages recursively pulled with this layer

    unique_packages_dict = {}

    for job, lisrtt in individual_job_package_lists:

        accounted_for = 0

        unique_packages = set()

        for ddd in lisrtt:
            unique_packages.add((strip_hash(ddd)))
            for p in recursive_dependencies_dict[ddd]:
                unique_packages.add((strip_hash(p)))

        unique_packages_dict[job] = unique_packages

    for item in selected_packages:

        for job in unique_packages_dict:

            accounted_for = 0

            unique_packages = unique_packages_dict[job]

            if strip_hash(item) not in accounted_for_packages_in_jobs[job] and strip_hash(item) in unique_packages:

                accounted_for_packages_in_jobs[job].add(strip_hash(item))

                accounted_for += package_file_size[item]

            for p in recursive_dependencies_dict[item]:

                if strip_hash(p) not in accounted_for_packages_in_jobs[job] and strip_hash(p) in unique_packages:

                    accounted_for_packages_in_jobs[job].add(strip_hash(p))

                    accounted_for += package_file_size[p]

            recursive_added_job[job].add(strip_hash(item))
            for p in recursive_dependencies_dict[item]:
                recursive_added_job[job].add(strip_hash(p))

    # cleaning up accounted for packages

    for job, _ in individual_job_package_lists:
        for it in other_dict[job]:
            # List to store keys to remove
            items_to_remove = []
            for i in other_dict[job][it]:
                if strip_hash(i) in accounted_for_packages_in_jobs[job]:
                    items_to_remove.append(i)

            sum = 0

            # Remove the keys outside the loop
            for key in items_to_remove:
                sum += package_file_size[item]
                other_dict[job][it].remove(key)
        # List to store keys to remove
        keys_to_remove = []

        for it in other_dict[job]:
            # if the package is accounted for but still has unaccounted for recursive dependencies, then we still want to consider the package to be added to a layer
            if strip_hash(it) in accounted_for_packages_in_jobs[job] and len(other_dict[job][it]) == 0:
                keys_to_remove.append(it)

        # Remove the keys outside the loop
        for key in keys_to_remove:
            del other_dict[job][key]
