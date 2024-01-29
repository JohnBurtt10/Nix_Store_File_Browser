def extract_section(raw_data, keyword, delimiter=':'):
    """
    Extracts a section from raw data based on a keyword and delimiter.

    Parameters:
    - raw_data (str): The raw data to extract from.
    - keyword (str): The keyword indicating the start of the section.
    - delimiter (str): The delimiter separating the keyword and the content.

    Returns:
    - section_content (list): The content of the section as a list of strings.
    """
    # Split the raw data into lines
    lines = raw_data.split('\n')

    # Initialize section_content as an empty list
    section_content = []

    # Iterate through each line and find the line with the specified keyword
    for line in lines:
        if line.startswith(keyword):
            # Extract the section content and split it into a list
            section_content = line.split(delimiter, 1)[-1].strip().split()

    return section_content