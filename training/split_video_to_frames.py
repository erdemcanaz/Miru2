import cv2
import uuid

def split_video_to_frames(video_path:str=None, image_export_path:str=None, frame_skip:int= 30):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    current_frame = 0

    print(f"Total frames: {total_frames}")

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow('Video', frame)
        key = cv2.waitKey(0) & 0xFF

        if key == ord('a'):
            current_frame = max(0, current_frame - 30)
        elif key == ord('q'):
            current_frame = max(0, current_frame - 150)
        elif key == ord('d'):
            current_frame = min(total_frames - 1, current_frame + 30)
        elif key == ord('e'):
            current_frame = min(total_frames - 1, current_frame + 150)
        elif key == ord('s'):
            frame_uuid = str(uuid.uuid4())
            cv2.imwrite(f'{image_export_path}/frame_{current_frame}_{frame_uuid}.jpg', frame)
            print(f"Frame {frame_uuid} saved.")
        elif key == ord('w'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Usage example
video_path = input("Enter video path: ")
image_export_path = input("Enter image export folder path: ")

split_video_to_frames(video_path=video_path, image_export_path = image_export_path, frame_skip = 70)
