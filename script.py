import glob
import os
import subprocess
import shutil

def main():
    in_files = glob.glob("*.in")

    # Create an output folder named "output" if it doesn't exist.
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for in_file in in_files:
        print(f"Running {in_file}...")
        # Run main.py with the current .in file.
        subprocess.run(["python3", "/home/evan/Documents/Code/Operating Systems/Project 1/main.py", in_file], check=True)
        
        # Determine the expected output file name by replacing .in with .out.
        output_file = in_file.replace(".in", ".out")
        
        if os.path.exists(output_file):
            destination = os.path.join(output_folder, output_file)
            shutil.move(output_file, destination)
            print(f"Moved {output_file} to {destination}.")
        else:
            print(f"Error: Expected output file {output_file} not found for {in_file}.")

if __name__ == "__main__":
    main()
