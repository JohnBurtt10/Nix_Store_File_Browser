def check_intersection(list1, list2):
    # Convert lists to sets for faster intersection operation
    set1 = set(list1)
    set2 = set(list2)

    # Check if there is any intersection between the two sets
    if set1.intersection(set2):
        return True
    else:
        return False


def remove_common_elements(list1, list2):
    # Convert lists to sets for faster intersection operation
    set1 = set(list1)
    set2 = set(list2)

    # Remove common elements from list1
    result = [x for x in list1 if x not in set2]

    return result