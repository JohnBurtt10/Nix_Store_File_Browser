def sum_dicts(dict1, dict2):
    return {key: dict1.get(key, 0) + dict2.get(key, 0) for key in set(dict2.keys()).union(set(dict1.keys()))}