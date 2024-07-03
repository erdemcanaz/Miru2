import cv2, datetime
from pathlib import Path

script_path = Path(__file__).absolute()
script_folder = script_path.parent.absolute()

media_path = script_folder / "test_image.png"
image = cv2.imread(str(media_path))
cv2.imshow("Image", image)