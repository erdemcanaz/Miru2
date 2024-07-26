import os
import cv2
from ultralytics import YOLO
import time

def label_images(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Loop through all images in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path)
            
            # Perform detection
            results = model.predict(image)
            
            # Get the name of the image file without extension
            file_stem = os.path.splitext(filename)[0]
            
            # Prepare the label file path
            label_file_path = os.path.join(output_folder, f"{file_stem}.txt")
            
            if len(results) == 0:
                print(f"No objects detected in {filename}")
                time.sleep(2)
                continue

            with open(label_file_path, 'w') as label_file:
                # Write labels to the file in YOLO format
                for result in results:
                    for box in result.boxes:
                        class_id = int(box.cls)
                        xc, yc, w, h = box.xywhn[0]
                        label_file.write(f"{class_id} {xc} {yc} {w} {h}\n")
            
            print(f"Processed {filename}")

# Example usage
model_path = input("Enter the path to the model file: ")
model = YOLO(model_path)
input_folder = input("Enter the path to the input folder: ")
output_folder = input("Enter the path to the output folder: ")
label_images(input_folder, output_folder)
