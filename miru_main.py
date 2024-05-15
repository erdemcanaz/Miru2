from scripts import pose_detector
import cv2
import pprint


pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    # Read frame from webcam
    ret, frame = cap.read()

    r = pose_detector_object.predict_frame_and_return_detections(frame,bbox_confidence=0.5)    
    #pprint.pprint(r)
    #pose_detector_object.draw_facial_keypoints_on(frame = frame, predictions = r, keypoint_confidence_threshold = 0.5)
    #pose_detector_object.draw_face_bounding_box_on(frame = frame, predictions = r, keypoint_confidence_threshold = 0.5)
    pose_detector_object.extract_and_draw_face_bounding_box_on(frame = frame, predictions = r, keypoint_confidence_threshold = 0.85,rect_size=200)
    

    # Display frame
    cv2.imshow("Webcam", frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close window
cap.release()
cv2.destroyAllWindows()