import cv2
import numpy as np
from ultralytics import YOLO
import datetime
import uuid
import copy
import time

PARAM_IS_SAVE_LOW_CONFIDENCES_AUTOMATICALLY = False
PARAM_AUTO_SAVE_LOW_CONFIDENCE_THRESHOLD = 0.8
PARAM_AUTO_SAVE_COOLDOWN = 0.75
PARAM_SHOW_RED_CONFIDENCE_THRESHOLD = 0.8
PARAM_MAX_NUMBER_OF_FRAMES_SAVED = 3000

# Function to perform detection and draw bounding boxes
def detect_and_draw(frame)->float:     
        global PARAM_SHOW_RED_CONFIDENCE_THRESHOLD
        
        min_bbox_confidence = float("inf")

        results = model(frame, task = "detect", verbose= False)[0]        
        for i, result in enumerate(results):
            boxes = result.boxes
            box_cls_no = int(boxes.cls.cpu().numpy()[0])
            box_cls_name = model.names[box_cls_no]
            box_conf = boxes.conf.cpu().numpy()[0]
            box_xyxy = boxes.xyxy.cpu().numpy()[0]

            min_bbox_confidence = min(box_conf, min_bbox_confidence)
            color = (0, 255, 0) if box_conf > PARAM_SHOW_RED_CONFIDENCE_THRESHOLD else (0, 0, 255)
            # Draw bounding box
            cv2.rectangle(frame, (int(box_xyxy[0]), int(box_xyxy[1])), (int(box_xyxy[2]), int(box_xyxy[3])), color, 2)
            # Draw class name and confidence
            cv2.putText(frame, f"{box_cls_name} {box_conf:.2f}", (int(box_xyxy[0]), int(box_xyxy[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        return min_bbox_confidence

PARAM_ZOOM_FACTOR = 0.50 # length of ROI edge in terms of the frame edge length 
PARAM_ZOOM_TOPLEFT_NORMALIZED = (0.25, 0.25)
PARAM_FETCH_SIZE = (1920, 1080) #NOTE: DO NOT CHANGE -> fixed miru display size, do not change. Also the camera data is fetched in this size

if PARAM_ZOOM_TOPLEFT_NORMALIZED[0] + PARAM_ZOOM_FACTOR > 1 or PARAM_ZOOM_TOPLEFT_NORMALIZED[1] + PARAM_ZOOM_FACTOR > 1:
    raise ValueError("Zoomed region is out of frame boundaries")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, PARAM_FETCH_SIZE[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PARAM_FETCH_SIZE[1])

cv2.namedWindow('YOLOv8 Detection', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('YOLOv8 Detection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Load the YOLOv8 model
folder_path = "C:\\Users\\Levovo20x\\Documents\\GitHub\\Miru2\\training\\local_saved_frames"
experiment_name = input("Enter the name of your experiment: ")
model_path = input("Enter the path to the model: ")
model = YOLO(model_path)

saved_count = 0
last_time_autosave = time.time()
while True:
    min_bbox_confidence = float("inf")
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break
    print(f"Frame shape: {frame.shape}")

    if PARAM_ZOOM_FACTOR < 1:
        zoomed_region_top_left = (int(PARAM_ZOOM_TOPLEFT_NORMALIZED[0] * frame.shape[1]), int(PARAM_ZOOM_TOPLEFT_NORMALIZED[1] * frame.shape[0]))
        zoomed_region_bottom_right = (int(zoomed_region_top_left[0] + PARAM_ZOOM_FACTOR * frame.shape[1]), int(zoomed_region_top_left[1] + PARAM_ZOOM_FACTOR * frame.shape[0]))
        frame = frame[zoomed_region_top_left[1]:zoomed_region_bottom_right[1], zoomed_region_top_left[0]:zoomed_region_bottom_right[0]]

    # mirror the frame so that movements are more intuitive
    frame = cv2.flip(frame, 1) 

    # Resize frame to the desired size
    resized_frame = cv2.resize(copy.deepcopy(frame), (PARAM_FETCH_SIZE[0], PARAM_FETCH_SIZE[1]))
    print(f"Resized Frame shape: {resized_frame.shape}")
    frame_untoched = copy.deepcopy(resized_frame)

    min_bbox_confidence = detect_and_draw(resized_frame)
    cv2.putText(resized_frame, f"#Frame: {saved_count}, Auto Save: {PARAM_IS_SAVE_LOW_CONFIDENCES_AUTOMATICALLY}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    cv2.imshow('YOLOv8 Detection', resized_frame)

    # Break the loop on 'q' key press
    key = cv2.waitKey(1) & 0xFF

    is_auto_save = PARAM_IS_SAVE_LOW_CONFIDENCES_AUTOMATICALLY and min_bbox_confidence < PARAM_AUTO_SAVE_LOW_CONFIDENCE_THRESHOLD and time.time()-last_time_autosave > PARAM_AUTO_SAVE_COOLDOWN
    if key == ord('q'):
        break
    elif key == ord('m'):
        PARAM_IS_SAVE_LOW_CONFIDENCES_AUTOMATICALLY = not PARAM_IS_SAVE_LOW_CONFIDENCES_AUTOMATICALLY 
        print(f"Auto-save preference: {PARAM_IS_SAVE_LOW_CONFIDENCES_AUTOMATICALLY}")

    elif key == ord('s') or is_auto_save:
        if is_auto_save:
            last_time_autosave = time.time()
        # Save the current frame to a desired folder
        # Generate a unique ID
        saved_count += 1

        # Get the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Modify the experiment name
        unique_id = str(uuid.uuid4())
        image_name = f"{experiment_name}_{saved_count}_{current_date}_{unique_id}"

        if is_auto_save:
            print(f"Auto-saving frame with confidence {min_bbox_confidence:.2f}: {image_name}")
        else:
            print(f"Mannualy saved frame: {image_name}")

        # Save the current frame to a desired folder
        cv2.imwrite(f"{folder_path}/{image_name}.jpg", frame_untoched)

    if saved_count >= PARAM_MAX_NUMBER_OF_FRAMES_SAVED:
        print("Reached the maximum number of saved frames.")
        break

# When everything done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()
