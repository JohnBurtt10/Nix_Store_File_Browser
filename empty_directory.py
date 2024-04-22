import os

def empty_directory(directory):
    try:
        # Check if the directory exists
        if os.path.exists(directory):
            # Iterate over the contents of the directory
            for root, dirs, files in os.walk(directory, topdown=False):
                for file in files:
                    # Remove files
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    # Remove subdirectories
                    os.rmdir(os.path.join(root, dir))
            print(f"The directory '{directory}' has been emptied successfully.")
        else:
            print(f"The directory '{directory}' does not exist.")
    except Exception as e:
        print(f"Error: Unable to empty directory '{directory}': {e}")

# Example usage:
directory_path = "your_directory_path"
empty_directory(directory_path)
