import os
import glob

def cleanup_directory(directory_path):
    # Get a list of all files in the directory
    files = glob.glob(os.path.join(directory_path, '*.json'))
    
    # Sort files by their timestamp (using file name)
    files.sort(key=lambda x: int(os.path.basename(x)[:-5]))
    
    # Check if there are more than 100 files
    if len(files) > 100:
        # Calculate how many files need to be deleted
        num_files_to_delete = len(files) - 75
        
        # Delete the oldest files
        for i in range(num_files_to_delete):
            os.remove(files[i])

        print("Deleted", num_files_to_delete, "container_layer_view files.")

def main():
    cleanup_directory('container_layer_view')

if __name__ == '__main__':
    main()