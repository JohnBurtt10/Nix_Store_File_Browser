import os

# Hardcoded folder path
folder = "app/processes"

def create_file(filename):
    try:
        # Check if the folder exists, if not, create it
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Combine folder path and filename
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w') as f:
            # You can optionally write something into the file here
            f.write("This is a new file.")
        # print(f"File '{filename}' created successfully in folder '{folder}'.")
    except IOError:
        print(f"Error: Unable to create file '{filename}' in folder '{folder}'.")

def delete_file(filename):
    try:
        # Combine folder path and filename
        filepath = os.path.join(folder, filename)
        
        # Check if file exists before attempting deletion
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"File '{filename}' deleted successfully from folder '{folder}'.")
        else:
            print(f"File '{filename}' does not exist in folder '{folder}'.")
    except Exception as e:
        print(f"Error: Unable to delete file '{filename}' from folder '{folder}': {e}")


def file_exists(filename):
    # Combine folder path and filename
    filepath = os.path.join(folder, filename)
    return os.path.exists(filepath)

