from ultralytics import YOLO
import cv2, datetime

# Load a model
model_path = input("Enter the path to the model: ")
media_path = input("Enter the path to the media: ")

model = YOLO(model_path)  # pretrained YOLOv8n model
results = model(source=media_path, vid_stride=1, show=True, save=True, project="C:\\Users\\Levovo20x\\Documents\\GitHub\\Miru2\\training\\local_test_results\\", conf=0.75)  # return a list of Results objects
