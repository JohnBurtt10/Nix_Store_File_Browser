def sum_2d_dicts_of_lists(dict1, dict2):
    result = {}
    
    # Combine all keys from both dictionaries
    all_keys = set(dict1.keys()).union(dict2.keys())
    
    # Iterate through all keys
    for key in all_keys:
        # Get the inner dictionaries for the current key or an empty dictionary if not present
        inner_dict1 = dict1.get(key, {})
        inner_dict2 = dict2.get(key, {})
        
        try:
        
            # Perform element-wise sum for the inner dictionaries
            result[key] = {sub_key: list(set(inner_dict1.get(sub_key, [])) | set(inner_dict2.get(sub_key, []))) 
                        for sub_key in set(inner_dict1).union(inner_dict2)}
        
        except Exception as e:
            print(f"dict1: {dict1}, dict2: {dict2}")
            print(f"inner_dict1: {inner_dict1}, inner_dict2: {inner_dict2}")
            raise e
        
    
    return result
# Example usage
dict1 = {'a': {'x': 1, 'y': 2}, 'b': {'x': 3, 'y': 4}}
dict2 = {'a': {'x': 5, 'y': 6}, 'c': {'x': 7, 'y': 8}}

# result = elementwise_sum(dict1, dict2)
# print(result)
