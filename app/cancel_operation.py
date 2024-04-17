# import os
# import pickle

# def update_file_variable_value(file_name, variable, value):
#     folder_path = "/path/to/your/folder"  # Hardcoded folder path

#     # Create folder if it doesn't exist
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)

#     file_path = os.path.join(folder_path, file_name + '.pkl')

#     # Retrieve variables from the file
#     try:
#         with open(file_path, 'rb') as f:  # Open file in binary read mode
#             loaded_data = pickle.load(f)
#     except FileNotFoundError:
#         # If file doesn't exist, create an empty dictionary
#         loaded_data = {}

#     # Update the value of the variable
#     loaded_data[variable] = value

#     # Write the modified data back to the file
#     with open(file_path, 'wb') as f:  # Open file in binary write mode
#         pickle.dump(loaded_data, f)


import os

# Hardcoded folder path
folder = "path/to/folder"

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

def file_exists(filename):
    # Combine folder path and filename
    filepath = os.path.join(folder, filename)
    return os.path.exists(filepath)

