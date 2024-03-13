from search_for_dependency import search_for_dependency
from write_to_file import write_list_to_file
from tqdm import tqdm

def layering_sanity_check(hydra, low_entropy, packages_without_dependencies, output_directory, timestamp):
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
                if search_for_dependency(hydra, node_without_arrow,  outer_key[0]) or (node_without_arrow == outer_key[0]):
                    flag = True
                    break
            pbar.update(1)
    return True