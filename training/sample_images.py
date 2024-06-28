import cv2
import cv2
import os
import random
import shutil

# Set the source and destination folders
source_folder = input("Enter the source folder path: ")
destination_folder = input("Enter the destination folder path: ")
p = float(input("Enter the sampling probability: "))

# Get the list of image files in the source folder
image_files = [f for f in os.listdir(source_folder) if f.endswith('.jpg') or f.endswith('.png')]

# Iterate over the image files
for image_file in image_files:
    # Generate a random number between 0 and 1
    random_number = random.random()
    
    # Check if the random number is less than the probability
    if random_number < p:

        # Construct the source and destination paths
        source_path = os.path.join(source_folder, image_file)
        destination_path = os.path.join(destination_folder, image_file)
        
        # Copy the image file to the destination folder
        shutil.copyfile(source_path, destination_path)

        print(f"Image file {image_file} copied to {destination_folder}")