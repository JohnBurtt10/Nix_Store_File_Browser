import re

def has_timestamp(s):
    # Define the timestamp pattern as YYYYMMDDHHMMSS
    timestamp_pattern = r'\d{14}'

    # Search for the timestamp pattern in the string
    match = re.search(timestamp_pattern, s)

    # Return True if a timestamp is found, otherwise False
    return bool(match)

# Example usage
# string_to_check = "ss7f4iyn4x3yxfyaif7jcap2r3029k1k-python3.10-urllib3-2.1.0"

# if has_timestamp(string_to_check):
#     print("The string contains a timestamp.")
# else:
#     print("No timestamp found in the string.")
