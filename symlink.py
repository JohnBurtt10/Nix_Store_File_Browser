import os

def get_symlink_target(path):
    try:
        target = os.readlink(path)
        return target
    except OSError as e:
        print(f"Error: {e}")
        return None

# Example usage:
symlink_path = "./result"  # Replace with the actual path to your symlink
target = get_symlink_target(symlink_path)

if target is not None:
    print(f"The symlink {symlink_path} points to: {target}")
else:
    print(f"Unable to determine the target of the symlink {symlink_path}.")
