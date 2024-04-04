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

# def sum_2d_dicts_of_dicts(dict1, dict2):
#     result = {}
    
#     # Iterate over rows (outer keys)
#     for row_key in dict1.keys() | dict2.keys():
#         # Initialize row in result dictionary
#         result[row_key] = {}
        
#         # Iterate over columns (inner keys)
#         for col_key in dict1.get(row_key, {}).keys() | dict2.get(row_key, {}).keys():
#             # Sum corresponding values if present in both dictionaries
#             value1 = dict1.get(row_key, {}).get(col_key, 0)
#             value2 = dict2.get(row_key, {}).get(col_key, 0)
#             result[row_key][col_key] = value1 + value2
    
#     return result
