from scripts import pose_detector
from scripts import face_tracker
from scripts import arduino_communicator

import cv2

arduino_communicator_object = arduino_communicator.ArduinoCommunicator(baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 10, verbose = False, write_delay_s=0.01)
pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")
face_tracker_object = face_tracker.HumanFaceTracker()

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    # Read frame from webcam
    ret, frame = cap.read()

    # Arduino communication test
    arduino_communicator_object.ensure_connection()
    if arduino_communicator_object.get_connection_status() == False:
        cv2.putText(frame, "Arduino connection failed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "Arduino connection successful", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
    pred_dicts = pose_detector_object.predict_frame_and_return_detections(frame,bbox_confidence=0.5)    
    face_bbox_coords = pose_detector_object.get_face_bounding_boxes_coordinates(frame = frame, predictions= pred_dicts, keypoint_confidence_threshold = 0.85)
    
    face_tracker_object.update_detected_faces(frame=frame, detected_face_bbox_coords=face_bbox_coords)
    face_tracker_object.draw_faces_on_frame(frame=frame)

    if face_tracker_object.should_turn_on_turnstiles():
        arduino_communicator_object.send_activate_turnstile_signal()
    else:
        arduino_communicator_object.send_ping_to_arduino()

    # Display frame
    cv2.imshow("Webcam", frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close window
cap.release()
cv2.destroyAllWindows()