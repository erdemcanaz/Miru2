import cv2
import pose_detector
import uuid

def split_frame_with_persons_from_video(data_name:str =  None, video_path:str=None, image_export_path:str=None, frame_skip:int= 30, is_manual:bool = False, desired_image_edge_lengths:int = 200):
    pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n-pose")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {total_frames}")

    current_frame = 0
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        
        print(f"%{100*current_frame/total_frames:.2f} Frame: {current_frame}/{total_frames}")
        if not ret:
            break

        r = pose_detector_object.predict_frame_and_return_detections(frame,bbox_confidence=0.5)   
        extracted_face_frames = pose_detector_object.get_fbbox_frames(frame = frame, predictions = r, keypoint_confidence_threshold = 0.85, desired_image_edge_lengths = 200)
        
        cv2.imshow('Video', frame)

        if is_manual:
            key = cv2.waitKey(0) & 0xFF

            if key == ord('a'):
                current_frame = max(0, current_frame - frame_skip)
            elif key == ord('q'):
                current_frame = max(0, current_frame - frame_skip*5)
            elif key == ord('d'):
                current_frame = min(total_frames - 1, current_frame + frame_skip)
            elif key == ord('e'):
                current_frame = min(total_frames - 1, current_frame + frame_skip*5)
            elif key == ord('s'):
                cv2.imwrite(f'{image_export_path}/frame_{current_frame}_{frame_uuid}.jpg', frame)             
                print(f"Frame {frame_uuid} saved.")
            elif key == ord('w'):
                break
        else:
            if total_frames-1 <= current_frame + frame_skip:
                break
            else:
                current_frame += frame_skip
                frame_uuid = str(uuid.uuid4())
                if data_name is not None:
                    cv2.imwrite(f'{image_export_path}/{data_name}_frame_{current_frame}_{frame_uuid}.jpg', frame)
                else:
                    cv2.imwrite(f'{image_export_path}/frame_{current_frame}_{frame_uuid}.jpg', frame)
                print(f"Frame {frame_uuid} saved.")
                    

            key = cv2.waitKey(10) & 0xFF
            if key == ord('w'):
                break

    cap.release()
    cv2.destroyAllWindows()

#=======================================================================================================
# Usage example
if __name__ == "__main__":
    video_path = input("Enter video path: ")
    image_export_path = input("Enter image export folder path: ")
    data_name = input("Enter data-name: ")

    split_frame_with_persons_from_video(data_name= data_name, video_path=video_path, image_export_path = image_export_path, frame_skip = 50, is_manual = False, desired_image_edge_lengths= 250)
