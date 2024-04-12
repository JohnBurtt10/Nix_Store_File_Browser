def split_dict(dictionary, num_parts):
    """
    Split a dictionary into a given number of parts.

    Args:
    - dictionary (dict): The dictionary to be split.
    - num_parts (int): The number of parts to split the dictionary into.

    Returns:
    - list: A list containing the split parts, each represented as a dictionary.

    Raises:
    - ValueError: If the number of parts is less than 1 or greater than the total number of items in the dictionary.

    Note:
    The function evenly distributes the items of the dictionary into the specified number of parts.
    Each part is represented as a separate dictionary in the resulting list.

    Example:
    ```
    my_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    num_parts = 2
    result = split_dict(my_dict, num_parts)
    print(result)
    # Output: [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]
    ```

    """
    items = list(dictionary.items())
    total_items = len(items)

    if num_parts < 1 or num_parts > total_items:
        raise ValueError("Invalid number of parts")

    part_size = total_items // num_parts
    remainder = total_items % num_parts

    result = []
    start_index = 0

    for i in range(num_parts):
        part_length = part_size + (1 if i < remainder else 0)
        end_index = start_index + part_length
        result.append(dict(items[start_index:end_index]))
        start_index = end_index

    return result

def main():
    my_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7}
    num_parts = 3
    split_parts = split_dict(my_dict, num_parts)

    for i, part in enumerate(split_parts):
        print(f"Part {i + 1}:", part)

if __name__ == "__main__":
    main()
