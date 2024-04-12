from .cache_directories import *
import re

def compare_and_group_references(references1, references2):

    if (references1, references2) in compare_and_group_references_cache:
        return compare_and_group_job_cache[(references1, references2)]

    jobset1_unique_references = [item for item in references1 if (
        item not in references2) and "merged" not in item]

    jobset2_unique_references = [item for item in references2 if (
        item not in references1) and "merged" not in item]
    # Create a dictionary to group items
    grouped_items = {}

    for item in jobset1_unique_references + jobset2_unique_references:
        key = item.split('-', 1)[1]

        # Define a regular expression pattern to match timestamps
        timestamp_pattern = r'\d{14}'

        # Replace timestamps in both strings with an empty string
        str_without_timestamp = re.sub(timestamp_pattern, '', key)

        if str_without_timestamp not in grouped_items:
            grouped_items[str_without_timestamp] = {'list1': [], 'list2': []}

        if item in references1:
            grouped_items[str_without_timestamp]['list1'].append(item)
        elif item in references2:
            grouped_items[str_without_timestamp]['list2'].append(item)

    compare_and_group_job_cache[(references1, references2)] = grouped_items
    return grouped_items