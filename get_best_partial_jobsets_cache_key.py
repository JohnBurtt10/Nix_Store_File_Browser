def get_best_partial_jobsets_cache_key(full_list, incomplete_lists):
    """
    Given a full list and a set of incomplete lists, this function identifies the incomplete list
    that has the longest matching prefix with the full list. It returns a tuple containing the best
    matching incomplete list and the remaining elements in the full list after removing the matched
    prefix.

    Parameters:
    - full_list (list): The complete list of items.
    - incomplete_lists (list): A list of incomplete lists to compare with the full list.

    Returns:
    tuple: A tuple containing two elements:
        - The best matching incomplete list (None if no match is found).
        - The remaining items in the full list after removing the matched prefix.

    Example:
    ```python
    full_list = [1, 2, 3, 4, 5]
    incomplete_lists = [[1, 2], [1, 2, 3], [3, 4]]

    result = get_best_partial_jobsets_cache_key(full_list, incomplete_lists)
    print(result)
    # Output: ([1, 2, 3], [4, 5])
    ```
    In this example, the best matching incomplete list is [1, 2, 3], and the remaining items in the
    full list are [4, 5].
    """
    longest_length = 0
    best_list = None
    remaining_jobsets = None
    if not incomplete_lists:
        return (None, full_list)
    for incomplete_list in incomplete_lists:
        length = 0
        flag = False
        for index, item in enumerate(incomplete_list):
            if index > len(full_list)-1 or item != full_list[index]:
                flag = True
                break
            length = length + 1
        if flag:
            continue
        if length > longest_length:
            longest_length = length
            best_list = incomplete_list
    if best_list is None:
        return (None, full_list)
    remaining_jobsets = [item for item in full_list if item not in best_list]
    return (best_list, remaining_jobsets)


def main():
    full_list = ['v2.32.0-20240214033837-0', 'v2.32.0-20240214065018-0', 'v2.32.0-20240214124953-0', 'v2.32.0-20240214134929-0', 'v2.32.0-20240214145009-0', 'v2.32.0-20240214154930-0', 'v2.32.0-20240214174934-0', 'v2.32.0-20240214194932-0', 'v2.32.0-20240214214930-0', 'v2.32.0-20240215033837-0', 'v2.32.0-20240215125016-0', 'v2.32.0-20240215145004-0', 'v2.32.0-20240215145250-0', 'v2.32.0-20240215154937-0', 'v2.32.0-20240215165007-0', 'v2.32.0-20240215174927-0', 'v2.32.0-20240215185010-0', 'v2.32.0-20240215194929-0', 'v2.32.0-20240215204958-0', 'v2.32.0-20240215214929-0', 'v2.32.0-20240215225018-0', 'v2.32.0-20240216033826-0', 'v2.32.0-20240216145010-0',
                 'v2.32.0-20240216154922-0', 'v2.32.0-20240216165012-0', 'v2.32.0-20240216174934-0', 'v2.32.0-20240216205023-0', 'v2.32.0-20240216214934-0', 'v2.32.0-20240217033847-0', 'v2.32.0-20240217145018-0', 'v2.32.0-20240220085005-0', 'v2.32.0-20240220145004-0', 'v2.32.0-20240220164953-0', 'v2.32.0-20240220194934-0', 'v2.32.0-20240221134933-0', 'v2.32.0-20240221144932-0', 'v2.32.0-20240221164942-0', 'v2.32.0-20240221194948-0', 'v2.32.0-20240221205003-0', 'v2.32.0-20240221214954-0', 'v2.32.0-20240221224942-0', 'v2.32.0-20240222004953-0', 'v2.32.0-20240222014947-0', 'v2.32.0-20240222145009-0', 'v2.32.0-20240222154938-0']  # Your full list
    incomplete_lists = [['v2.32.0-20240214033837-0', 'v2.32.0-20240214065018-0', 'v2.32.0-20240214124953-0', 'v2.32.0-20240214134929-0', 'v2.32.0-20240214145009-0', 'v2.32.0-20240214154930-0', 'v2.32.0-20240214174934-0', 'v2.32.0-20240214194932-0', 'v2.32.0-20240214214930-0', 'v2.32.0-20240215033837-0', 'v2.32.0-20240215125016-0'],  # Incomplete list 1
                        ['v2.32.0-20240214033837-0', 'v2.32.0-20240214065018-0',
                        'v2.32.0-20240214124953-0', 'v2.32.0-20240214134929-0'],  # Incomplete list 2
                        ['v2.32.0-20240214065018-0', 'v2.32.0-20240214124953-0', 'v2.32.0-20240214134929-0', 'v2.32.0-20240214145009-0', 'v2.32.0-20240214154930-0', 'v2.32.0-20240214174934-0', 'v2.32.0-20240214194932-0', 'v2.32.0-20240214214930-0', 'v2.32.0-20240215033837-0', 'v2.32.0-20240215125016-0', 'v2.32.0-20240215145004-0', 'v2.32.0-20240215145250-0', 'v2.32.0-20240215154937-0', 'v2.32.0-20240215165007-0', 'v2.32.0-20240215174927-0', 'v2.32.0-20240215185010-0', 'v2.32.0-20240215194929-0', 'v2.32.0-20240215204958-0', 'v2.32.0-20240215214929-0', 'v2.32.0-20240215225018-0', 'v2.32.0-20240216033826-0', 'v2.32.0-20240216145010-0', 'v2.32.0-20240216154922-0', 'v2.32.0-20240216165012-0', 'v2.32.0-20240216174934-0', 'v2.32.0-20240216205023-0', 'v2.32.0-20240216214934-0', 'v2.32.0-20240217033847-0', 'v2.32.0-20240217145018-0', 'v2.32.0-20240220085005-0', 'v2.32.0-20240220145004-0', 'v2.32.0-20240220164953-0', 'v2.32.0-20240220194934-0', 'v2.32.0-20240221134933-0', 'v2.32.0-20240221144932-0', 'v2.32.0-20240221164942-0', 'v2.32.0-20240221194948-0', 'v2.32.0-20240221205003-0', 'v2.32.0-20240221214954-0', 'v2.32.0-20240221224942-0', 'v2.32.0-20240222004953-0', 'v2.32.0-20240222014947-0', 'v2.32.0-20240222145009-0', 'v2.32.0-20240222154938-0']]  # Incomplete list 3
    
    incomplete_lists=[]

    print(f"{get_best_partial_jobsets_cache_key(full_list, incomplete_lists)}")


if __name__ == "__main__":
    main()
