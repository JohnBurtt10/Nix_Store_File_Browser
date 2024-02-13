def sum_dicts(dict1, dict2):
    return {key: dict1.get(key, 0) + dict2.get(key, 0) for key in set(dict2.keys()).union(set(dict1.keys()))}

def sum_dicts_of_lists(dict1, dict2):
    return {key: list(set(dict1.get(key, [])) | set(dict2.get(key, []))) for key in set(dict2.keys()).union(set(dict1.keys()))}