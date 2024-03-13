from search_for_dependency import search_for_dependency
from write_to_file import write_list_to_file
from tqdm import tqdm

def layering_sanity_check(hydra, low_entropy, packages_without_dependencies, output_directory, timestamp):
    """
    Perform a layering sanity check on the given parameters.

    Args:
    - hydra (Hydra): The hydra information.
    - low_entropy (dict): A dictionary representing low entropy data.
    - packages_without_dependencies (list): A list of packages without dependencies.
    - output_directory (str): The directory where the output should be written.
    - timestamp (str): The timestamp for the output file.

    Returns:
    - bool: True if the layering sanity check passes meaning every package in the entropy trench is either in the layer
    or recursively depends on one that is, False otherwise.

    Note:
    The function uses a progress bar ('tqdm') to track the completion of the sanity check.

    Example:
    ```
    hydra = 
    low_entropy = {'layer1': 'data1', 'layer2': 'data2', 'layer1': 'data3'}
    packages_without_dependencies = ['package1', 'package2']
    output_directory = "/path/to/output"
    timestamp = "20220223"
    result = layering_sanity_check(hydra, low_entropy, packages_without_dependencies, output_directory, timestamp)
    print(result)
    # Output: False
    ```

    """
    my_list = []
    curr_key = None
    flag = False
    with tqdm(total=len(low_entropy), desc="Completing layering sanity check", unit="packages") as pbar:
        for outer_key in low_entropy:
            if curr_key is None:
                curr_key = outer_key
            else:
                if curr_key != outer_key:
                    if flag is False:
                        print(f"outer_key: {curr_key}")
                        write_list_to_file(my_list, "bad", output_directory, timestamp)
                        return False
                    else:
                        flag = False
                    my_list = []
                    curr_key = outer_key
            my_list.append(low_entropy[outer_key])
            for node_without_arrow in packages_without_dependencies:
                if search_for_dependency(hydra, outer_key[0], node_without_arrow) or (node_without_arrow == outer_key[0]):
                    flag = True
                    break
            pbar.update(1)
    return True