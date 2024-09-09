import subprocess

def upload_file():
    try:
        # Define the command to be executed
        command = [
            "scp",
            "-i", "/c/Users/traum/.ssh/id_rsa",
            "output.html",
            "everyink@everythingbesidesthekitchensink.com:/home3/everyink/public_html/products/"
        ]

        # Run the command
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        # Print the command output
        print("Command Output:")
        print(result.stdout)
        
        # Check for errors
        if result.stderr:
            print("Command Error:")
            print(result.stderr)
        
        print("File uploaded successfully!")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    upload_file()
