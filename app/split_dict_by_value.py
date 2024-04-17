def split_dict_by_value(my_dict, entropy_dict):
    matching_values = {}
    non_matching_values = {}

    for key in my_dict:
        if key.split('-', 1)[1] in entropy_dict:
            matching_values[key] = my_dict[key]
        else:
            non_matching_values[key] = my_dict[key]

    return matching_values, non_matching_values