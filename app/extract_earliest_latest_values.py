def extract_earliest_latest_values(input_dict):
    result_dict = {}
    earliest_value_timestamp_substr = None
    latest_value_timestamp_substr = None
    earliest_value = None
    latest_value = None
    for dependency, inner_dict in input_dict.items():
        # print(inner_dict)
        for job, reverse_dependencies in inner_dict.items():
            for reverse_dependency in reverse_dependencies:
                # Extract the timestamp substring
                timestamp_substr = reverse_dependency.split('-')[1]
                if earliest_value is None or timestamp_substr < earliest_value_timestamp_substr:
                    earliest_value = reverse_dependency
                    earliest_value_timestamp_substr = reverse_dependency.split(
                        '-')[1]
                if latest_value is None or timestamp_substr > latest_value_timestamp_substr:
                    latest_value = reverse_dependency
                    latest_value_timestamp_substr = reverse_dependency.split(
                        '-')[1]

            if dependency in result_dict:
                # if job in result_dict[dependency]:
                result_dict[dependency][job] = {
                    'earliest': earliest_value, 'latest': latest_value}
                # else:
            else:
                result_dict[dependency] = {}
                result_dict[dependency][job] = {
                    'earliest': earliest_value, 'latest': latest_value}
            # print(result_dict[dependency][job])

    return result_dict

# Example usage
# data = {
#     'simGazeboContainer.x86_64-linux': [
#         'v2.32.0-20240108033829-0', 'v2.32.0-20240108085003-0', 'v2.32.0-20240108164940-0',
#         'v2.32.0-20240122134922-0', 'v2.32.0-20240122145006-0'
#     ],
#     'simRobotContainer.x86_64-linux': [
#         'v2.32.0-20240108033829-0', 'v2.32.0-20240108085003-0', 'v2.32.0-20240108164940-0',
#         'v2.32.0-20240122134922-0', 'v2.32.0-20240122145006-0'
#     ]
# }

# result = extract_earliest_latest_values(data)
# print(result)
