import re
# Custom key function to extract timestamp from version string
def extract_timestamp(version_string):
    match = re.search(r'\d{14}', version_string)
    if match:
        return match.group()
    return ''

def get_sorted_jobsets(hydra, project_name):
    
    jobsets = hydra.get_jobsets(project_name)

    # Sorting the list of version strings based on the timestamp
    sorted_jobsets = sorted(jobsets, key=extract_timestamp)
    
    return sorted_jobsets