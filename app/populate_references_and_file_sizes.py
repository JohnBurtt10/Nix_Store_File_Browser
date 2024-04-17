from .raw_data_utilities import extract_section

def populate_references_and_file_sizes(raw_data, references_dict, file_size_dict, jobset, job):
    store_path = extract_section(raw_data=raw_data, keyword="StorePath")[0]
    references = extract_section(raw_data=raw_data, keyword="References")
    file_size = int(extract_section(raw_data=raw_data, keyword="FileSize")[0])
    references_dict[store_path[len("/nix/store/"):]] = references
    file_size_dict[store_path[len("/nix/store/"):]] = file_size