from scripts import pose_detector
from scripts import equipment_detector
from scripts import face_tracker
from scripts import face_tracker_2
from scripts import arduino_communicator
from scripts import slides_show

import cv2
import pprint

arduino_communicator_object = arduino_communicator.ArduinoCommunicator(baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 10, verbose = False, write_delay_s=0.01)
pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")
equipment_detector_object = equipment_detector.EquipmentDetector(model_name="net_google_mask")
face_tracker_object = face_tracker.HumanFaceTracker()
face_tracker_2_object = face_tracker_2.FaceManager()
slides_show_object = slides_show.SlideShow(slides_folder="scripts/slides", slide_duration_s=5)

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Create a window named 'Object Detection' and set the window to fullscreen if desired
cv2.namedWindow('Miru', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Miru', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # Read frame from webcam
    ret, frame = cap.read()

    # Arduino communication test
    # arduino_communicator_object.ensure_connection()
    # if arduino_communicator_object.get_connection_status() == False:
    #     cv2.putText(frame, "Arduino connection failed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    # else:
    #     cv2.putText(frame, "Arduino connection successful", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
    equipment_detector_object.predict_frame(frame, bbox_confidence=0.65)
    equipment_formatted_predictions = equipment_detector_object.return_formatted_predictions_list()

    pose_pred_dicts = pose_detector_object.predict_frame_and_return_detections(frame,bbox_confidence=0.5)        
    face_bbox_coords = pose_detector_object.return_formatted_predictions_list(frame = frame, predictions= pose_pred_dicts, keypoint_confidence_threshold = 0.85)
    
    face_and_equipment_detections = face_bbox_coords + equipment_formatted_predictions
    face_tracker_2_object.update_current_faces(face_and_equipment_detections)


    face_tracker_2_object.draw_faces_on_frame(frame=frame)
    
    # face_tracker_object.update_detected_faces(frame=frame, detected_face_bbox_coords=face_bbox_coords, equipment_detections= equipment_pred_dicts) # during initialization of detected faces, their rule appliences are also evaluated.
    # face_tracker_object.draw_faces_on_frame(frame=frame)

    # if face_tracker_object.should_turn_on_turnstiles():
    #     arduino_communicator_object.send_activate_turnstile_signal()
    # else:
    #     arduino_communicator_object.send_ping_to_arduino()


    # slide related operations
    if slides_show_object.should_change_slide():
        slides_show_object.update_current_slide()

    if face_tracker_2_object.get_number_of_active_faces() == 0:
        slides_show_object.increase_opacity()
    else:
        slides_show_object.decrease_opacity()

    slide_frame = slides_show_object.get_slide_images(width=frame.shape[1], height=frame.shape[0])

    # Draw slide on top of frame
    frame = slides_show_object.draw_slide_on_top_of_frame(frame=frame, slide_frame=slide_frame)

    # Show frame
    cv2.imshow("Miru", frame)        
    if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
        break

# Release all sources
arduino_communicator_object.shutdown_connection()
cap.release()
cv2.destroyAllWindows()