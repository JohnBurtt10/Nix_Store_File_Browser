def layering_sanity_check(non_zero_entropy_packages, reduced_package_list, recursive_dependencies_dict):
    """
    Check if packages with non-zero entropy are correctly layered based on dependencies.

    Parameters:
    - non_zero_entropy_packages (list): Packages with non-zero entropy to be checked.
    - reduced_package_list (list): Packages with reduced dependencies for layering comparison.
    - recursive_dependencies_dict (dict): Dictionary with recursive dependencies for each package.

    Returns:
    - bool: True if the layering is sane, False otherwise.

    This function compares 'non_zero_entropy_packages' with 'reduced_package_list' and their
    dependencies in 'recursive_dependencies_dict'. Prints an error message and returns False
    if any package is not correctly layered. Returns True if all packages are correctly layered.
    """
    for key in non_zero_entropy_packages:
        flag = False
        for node in reduced_package_list:
            if key == node:
                flag = True
                break
            if flag is True:
                break
            for dependency in recursive_dependencies_dict[node]:
                if key == dependency:
                    flag = True
                    break
        if flag is False:
            print(f"sanity check failed: {key}")
            return False
    return True