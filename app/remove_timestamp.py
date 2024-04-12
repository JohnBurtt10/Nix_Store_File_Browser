import re


def remove_timestamp(string):
    if string is None:
        return None
    timestamp_pattern = r'\d{14}'

    # Replace timestamps in both strings with an empty string
    str_without_timestamp = re.sub(timestamp_pattern, '', string)
    return str_without_timestamp
