# nix_builder.py

import subprocess


def run_nix_build(package_expression):
    try:
        # Construct the Nix build command
        nix_build_command = ["nix", "build", package_expression]

        # Run the command and capture the output
        result = subprocess.run(
            nix_build_command, check=True, capture_output=True, text=True)

        # Print the result (optional)
        print("Nix Build Output:")
        print(result.stdout)

        # Return the result
        return result.returncode, result.stdout

    except subprocess.CalledProcessError as e:
        # Handle error if the subprocess command fails
        print(f"Error: {e}")
        return e.returncode, e.stdout
