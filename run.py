import sys
from app import app, socketio

if __name__ == '__main__':
    # Check if two command line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <integer_value> <true|false>")
        sys.exit(1)

    # Extract the command line arguments
    try:
        int_value = int(sys.argv[1])
    except ValueError:
        print("First argument must be an integer")
        sys.exit(1)

    bool_value = sys.argv[2].lower() == "true"

    # Run the Flask application with SocketIO
    socketio.run(app, port=int_value, debug=bool_value)
