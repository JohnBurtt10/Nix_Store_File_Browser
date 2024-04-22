import sys
from app import app, socketio
from app.generate_layers_sanity_check import generate_layers_sanity_check
from cleanup_directory import cleanup_directory
from empty_directory import empty_directory

if __name__ == '__main__':
    # Check if two command line arguments are provided
    # if len(sys.argv) != 3:
    #     print("Usage: python script.py <integer_value> <true|false>")
    #     sys.exit(1)

    # # Extract the command line arguments
    # try:
    #     int_value = int(sys.argv[1])
    # except ValueError:
    #     print("First argument must be an integer")
    #     sys.exit(1)

    # bool_value = sys.argv[2].lower() == "true"

    cleanup_directory("container_layer_view")

    empty_directory("app/processes")

    # Run the Flask application with SocketIO
    # socketio.run(app, host='0.0.0.0', port=int_value, debug=bool_value)

    if False and not generate_layers_sanity_check():
        print(f"generate layers sanity check failed")

    socketio.run(app, host='0.0.0.0', debug=True)
