from ultralytics import YOLO
from pathlib import Path

script_path = Path(__file__).absolute()
script_folder = script_path.parent.absolute()
miru2_folder = script_folder.parent.absolute()

model_path = miru2_folder / "trained_yolo_models" / "net_google_mask_28_06_2024.pt"
media_path = script_folder / "test_image.png"
model = YOLO(model_path)  # pretrained YOLOv8n model
results = model(source=media_path, vid_stride=1, show=False, save=False, project=None, conf=0.5)  # return a list of Results objects
