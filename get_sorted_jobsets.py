import re
# Custom key function to extract timestamp from version string
def extract_timestamp(version_string):
    match = re.search(r'\d{14}', version_string)
    if match:
        return match.group()
    return ''

def get_sorted_jobsets(hydra, project_name):

    # return ['v2.32.0-20240214033837-0', 'v2.32.0-20240214065018-0', 'v2.32.0-20240214124953-0', 'v2.32.0-20240214134929-0', 'v2.32.0-20240214145009-0', 'v2.32.0-20240214154930-0', 'v2.32.0-20240214174934-0', 'v2.32.0-20240214194932-0', 'v2.32.0-20240214214930-0', 'v2.32.0-20240215033837-0', 'v2.32.0-20240215125016-0']
    
    jobsets = hydra.get_jobsets(project_name)

    # Sorting the list of version strings based on the timestamp
    sorted_jobsets = sorted(jobsets, key=extract_timestamp)
    
    return sorted_jobsets