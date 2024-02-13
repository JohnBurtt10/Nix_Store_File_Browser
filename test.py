jobsets = ['v2.32.0-20240202033843-022','b','c','d']
key = tuple(["v2.32.0-20240202033843-022"])
cache = {key: {'sdk-2.32.0-20240202033843-0': {'014mzqkfzkqjjl3ig2bx8zks3srplnlp-python3.10-ipaddress-1.0.23': ['v2.32.0-20240202033843-0']}}}

cache_value = None
result_n = 0
remaining_jobsets = []
matching_sublist = None
for key in cache:
    print(key)
for n in range(len(jobsets), 0, -1):
    prefix = jobsets[:n]
    matching_sublist = next(
        (key for key in cache if prefix == key[:len(prefix)]), None)
    for key in cache:
        key = list(key)
        if prefix == key[:len(prefix)]:
            matching_sublist = prefix
            break  # If you only want to print the first matching sublist, you can break out of the loop
    if matching_sublist is not None:
        print("breaking")
        result_n = n
        remaining_jobsets = jobsets[result_n:]
        break

print("The highest value of n is:", result_n)
print("Remaining elements:", remaining_jobsets)
print("Matching sublist in my_second_list:", matching_sublist)
print(f"{cache[tuple(matching_sublist)]}")