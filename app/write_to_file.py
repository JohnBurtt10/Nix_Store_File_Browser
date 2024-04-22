import os
import json

# TODO: change the timestamp to be subdirectory

def write_dict_to_file(dictionary, extra_info, directory, timestamp):

    # Create the file name with the timestamp and extra information
    file_name = f'dict_output_{extra_info}.txt'

    # Join the directory path with the file name
    file_path = os.path.join(directory, timestamp, file_name)

    os.makedirs(directory+'/'+timestamp, exist_ok=True)

    # Open the file for writing
    with open(file_path, 'w') as file:
        for key, value in dictionary.items():
            file.write(f'{key}: {value}\n')
        # Write the dictionary to the file in JSON format
        # json.dump(dictionary, file, indent=2)

def write_variable_to_file(variable, extra_info, directory, timestamp):

    # Create the file name with the timestamp and extra information
    file_name = f'output_{extra_info}.txt'

    # Join the directory path with the file name
    file_path = os.path.join(directory, timestamp, file_name)

    os.makedirs(directory+'/'+timestamp, exist_ok=True)

    # Open the file for writing
    with open(file_path, 'w') as file:
        # Write the variable's value to the file
        file.write(variable)

def write_list_to_file(my_list, extra_info, directory, timestamp):

    # Create the file name with the timestamp and extra information
    file_name = f'list_output_{extra_info}.json'

    # Join the directory path with the file name
    file_path = os.path.join(directory, timestamp, file_name)

    os.makedirs(directory+'/'+timestamp, exist_ok=True)

    # Open the file for writing
    with open(file_path, 'a') as file:
        # Write the list to the file in JSON format
        json.dump(my_list, file, indent=2)

def write_list_to_python_file(my_list, extra_info, directory, timestamp):

    # Create the file name with the timestamp and extra information
    file_name = f'list_output_{extra_info}.py'

    # Join the directory path with the file name
    file_path = os.path.join(directory, timestamp, file_name)

    os.makedirs(os.path.join(directory, timestamp), exist_ok=True)

    # Open the file for writing
    with open(file_path, 'w') as file:
        # Write the list to the file in Python format
        file.write(f'{extra_info} = {json.dumps(my_list, indent=2)}\n')

def write_dict_to_python_file(my_dict, extra_info, directory, timestamp):

    # Create the file name with the timestamp and extra information
    file_name = f'dict_output_{extra_info}.py'

    # Join the directory path with the file name
    file_path = os.path.join(directory, timestamp, file_name)

    os.makedirs(os.path.join(directory, timestamp), exist_ok=True)

    # Open the file for writing
    with open(file_path, 'w') as file:
        # Write the list to the file in Python format
        file.write(f'{extra_info} = {json.dumps(my_dict, indent=2)}\n')


def write_layer_to_file(image_names, overhead, packages, directory, count, timestamp):
    # Create a dictionary to store the information
    output_data = {
        'image_names': image_names,
        'overhead': overhead,
        'packages': packages
    }

    # Create the file name with the timestamp and extra information
    file_name = f'list_output_{count}.json'

    # Join the directory path with the file name
    file_path = os.path.join(directory, timestamp, file_name)

    os.makedirs(os.path.join(directory, timestamp), exist_ok=True)

    # Open the file for writing
    with open(file_path, 'a') as file:
        # Write the data to the file in JSON format
        json.dump(output_data, file, indent=2)



