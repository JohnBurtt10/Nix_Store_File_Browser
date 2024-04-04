import pickle

def update_file_variable_value(variable, value):
    # Retrieve variables from the file
    try:
        with open('data.pkl', 'rb') as f:  # Open file in binary read mode
            loaded_data = pickle.load(f)
    except FileNotFoundError:
        # If file doesn't exist, create an empty dictionary
        loaded_data = {}

    # Update the value of 'cancel' variable
    loaded_data[variable] = value

    # print(f"updating {variable} to {value}")

    # Write the modified data back to the file
    with open('data.pkl', 'wb') as f:  # Open file in binary write mode
        pickle.dump(loaded_data, f)