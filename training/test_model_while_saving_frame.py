import cv2
import numpy as np
from ultralytics import YOLO
import datetime
import uuid

import copy

# Load the YOLOv8 model
folder_path = "C:\\Users\\Levovo20x\\Documents\\GitHub\\Miru2\\training\\local_saved_frames"
experiment_name = input("Enter the name of your experiment: ")
model_path = input("Enter the path to the model: ")
model = YOLO(model_path)

# Function to perform detection and draw bounding boxes
def detect_and_draw(frame):
        results = model(frame, task = "detect", verbose= False)[0]
        min_confidence_threshold = 0.80
        for i, result in enumerate(results):
            boxes = result.boxes
            box_cls_no = int(boxes.cls.cpu().numpy()[0])
            box_cls_name = model.names[box_cls_no]
            box_conf = boxes.conf.cpu().numpy()[0]
            box_xyxy = boxes.xyxy.cpu().numpy()[0]

            min_confidence_threshold = min(min_confidence_threshold, box_conf)
            # Draw bounding box

            color = (0, 255, 0) if box_conf > min_confidence_threshold else (0, 0, 255)
            cv2.rectangle(frame, (int(box_xyxy[0]), int(box_xyxy[1])), (int(box_xyxy[2]), int(box_xyxy[3])), color, 2)

            # Draw class name and confidence
            cv2.putText(frame, f"{box_cls_name} {box_conf:.2f}", (int(box_xyxy[0]), int(box_xyxy[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Loop to continuously get frames

saved_count = 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    frame_untoched = copy.deepcopy(frame)

    if not ret:
        print("Error: Could not read frame.")
        break

    # Detect and draw bounding boxes
    detect_and_draw(frame)

    # Draw counter
    cv2.putText(frame, f"Saved frames: {saved_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('YOLOv8 Detection', frame)

    # Break the loop on 'q' key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Save the current frame to a desired folder
        # Generate a unique ID
        saved_count += 1

        # Get the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Modify the experiment name
        unique_id = str(uuid.uuid4())
        image_name = f"{experiment_name}_{saved_count}_{current_date}_{unique_id}"
        print(f"Saved frame: {image_name}")

        # Save the current frame to a desired folder
        cv2.imwrite(f"{folder_path}/{image_name}.png", frame_untoched)

# When everything done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()
