# dict2 has preference
def merge_2d_dicts_with_preference(dict1, dict2):
    """
    Merge two dictionaries with a preference for values from the first dictionary.

    Args:
    - dict1 (dict): The first dictionary.
    - dict2 (dict): The second dictionary.

    Returns:
    - dict: A new dictionary combining values from both dictionaries with preference for dict1.
    """
    merged_dict = {}

    # Iterate through the keys of the first dictionary
    for key, inner_dict1 in dict1.items():
        # If the key is present in both dictionaries and the values are dictionaries, merge them
        if key in dict2 and isinstance(inner_dict1, dict) and isinstance(dict2[key], dict):
            merged_dict[key] = {**inner_dict1, **dict2[key]}
        else:
            # If the key is not present in dict2 or values are not dictionaries, take from dict1
            merged_dict[key] = inner_dict1

    # Add the keys from the second dictionary that are not present in the first dictionary
    for key, inner_dict2 in dict2.items():
        if key not in dict1:
            merged_dict[key] = inner_dict2

    return merged_dict

# # Example usage:
# dict1 = {'a': {'x': 1, 'y': 2}, 'b': {'z': 3}}
# dict2 = {'a': {'x': 10, 'z': 20}, 'c': {'w': 30}}

# result = merge_dicts_with_preference(dict1, dict2)
# print(result)

def merge_dicts_with_preference(dict1, dict2):
    """
    Merge two dictionaries with a preference for values from the second dictionary.

    Args:
    - dict1 (dict): The first dictionary.
    - dict2 (dict): The second dictionary.

    Returns:
    - dict: A new dictionary combining values from both dictionaries with preference for dict2.
    """
    merged_dict = dict1.copy()  # Start with a copy of dict1

    # Update values from dict2, overwriting existing values
    merged_dict.update(dict2)

    return merged_dict

# Example usage:
# dict1 = {'a': 1, 'b': 2, 'c': 3}
# dict2 = {'a': 10, 'd': 4, 'e': 5}

# result = merge_dicts_with_preference(dict1, dict2)
# print(result)