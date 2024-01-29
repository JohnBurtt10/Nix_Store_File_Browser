import subprocess
import json

def get_direct_dependencies(path):
    # Get path-info using nix
    command = ["nix", "path-info", path, "--json"]
    result = subprocess.run(command, capture_output=True, text=True)

    # Parse JSON output
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for {path}: {e}")
        return

    # Extract references and recursively process them
    references = info[0].get("references", [])
    return references

def get_stripped_direct_dependencies(path):
    path_dependencies = get_direct_dependencies(path)
    # Extract the second part of each string using .split("-", 1)[1]
    stripped_path_dependencies = {item.split("-", 1)[1] for item in path_dependencies}
    return stripped_path_dependencies


def are_direct_dependencies_equal(path1, path2) -> bool:
    stripped_path1_dependencies = get_stripped_direct_dependencies(path=path1)
    stripped_path2_dependencies = get_stripped_direct_dependencies(path=path2)
    # path1_dependencies.remove(path1)
    # path2_dependencies.remove(path2)
    # Check if the sets are identical based on the condition
    return stripped_path1_dependencies == stripped_path2_dependencies

def calculate_common_direct_dependencies_ratio(path1, path2) -> float:
    stripped_path1_dependencies = get_stripped_direct_dependencies(path=path1)
    stripped_path2_dependencies = get_stripped_direct_dependencies(path=path2)

    # Calculate the ratio of common elements
    common_elements = stripped_path1_dependencies & stripped_path2_dependencies
    total_elements = len(stripped_path1_dependencies) + len(stripped_path2_dependencies)

    if total_elements == 0:
        # Avoid division by zero
        return 0.0

    ratio_common = len(common_elements) / total_elements
    return ratio_common

if __name__ == "__main__":
    # Example usage
    path1 = "/nix/store/j7ska4fw79bwbadpx8smlrnn7xjss5gz-cisimTestingToolsRos1-2.32.0-20231228230312-0.sh"
    path2 = "/nix/store/3p2swp7zw63c0f7s6i3bwjd3yssjigbk-cisimTestingToolsRos1-2.31.0-20231116202242-0.sh"

    path3 = "/nix/store/fbsicg8wfqw85xv8xb51y4hzh9znd68g-cisimTestingToolsRos1-2.32.0-20240102033847-0.sh"
    path4 = "/nix/store/0p2wmyjqvkvmrjh3mcycm7mlnd3y7gs2-cisimTestingToolsRos1-2.32.0-20240101033835-0.sh"

    path5 = "/nix/store/aj2knr7ivxkfnbj6j21khl3xk4qsgxbs-cisimTestingToolsRos1-2.32.0-20240102144952-0.sh"
    path6 = "/nix/store/zvylic5ks98p31clc2jq1144wp8gcvbb-cisimTestingToolsRos1-2.32.0-20240102154952-0.sh"

    #TODO: change variable name
    result = are_direct_dependencies_equal(path1=path5, path2=path6)
    print(f"result: {result}")