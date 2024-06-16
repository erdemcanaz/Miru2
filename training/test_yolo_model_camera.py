from ultralytics import YOLO
import cv2, datetime

# Load a model
model_path = input("Enter the path to the model: ")

# Use webcam feed
media_path = 0  # 0 represents the default webcam device

model = YOLO(model_path)  # pretrained YOLOv8n model
results = model(source=media_path, vid_stride=1, show=True, save=False, project="C:\\Users\\Levovo20x\\Documents\\GitHub\\Miru2\\training\\local_test_results\\")  # return a list of Results objects
