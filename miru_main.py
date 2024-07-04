import sys
import os

# Determine the absolute path to the directory containing your scripts folder
project_directory = os.path.dirname(os.path.abspath(__file__))
scripts_directory = os.path.join(project_directory, 'scripts')

# Add the scripts directory to the sys.path
sys.path.append(scripts_directory)

# Now you can import your scripts using absolute paths
import pose_detector
import equipment_detector
#import face_tracker
import face_tracker_2
import arduino_communicator
import slides_show


import cv2
import pprint

arduino_communicator_object = arduino_communicator.ArduinoCommunicator(baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 10, verbose = False, write_delay_s=0.01)
pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")
equipment_detector_object = equipment_detector.EquipmentDetector(model_name="net_google_mask_28_06_2024")
#face_tracker_object = face_tracker.HumanFaceTracker()
face_tracker_2_object = face_tracker_2.FaceManager()
slides_show_object = slides_show.SlideShow(slides_folder="scripts/slides", slide_duration_s=5)

# Open webcam
cap = cv2.VideoCapture(0)# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW for windows to fast turn on
cap.set(3, 640)
cap.set(4, 360)

# Create a window named 'Object Detection' and set the window to fullscreen if desired
cv2.namedWindow('Miru', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Miru', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        continue

    #Arduino communication test
    arduino_communicator_object.ensure_connection()
    arduino_communicator_object.draw_arduino_connection_status_icon(frame)

    equipment_detector_object.predict_frame(frame, bbox_confidence=0.6)
    equipment_formatted_predictions = equipment_detector_object.return_formatted_predictions_list()

    if len(equipment_formatted_predictions) > 0:
        print()
        pprint.pprint(equipment_formatted_predictions)

    pose_pred_dicts = pose_detector_object.predict_frame_and_return_detections(frame,bbox_confidence=0.5)        
    face_bbox_coords = pose_detector_object.return_formatted_predictions_list(frame = frame, predictions= pose_pred_dicts, keypoint_confidence_threshold = 0.85)
    
    face_and_equipment_detections = face_bbox_coords + equipment_formatted_predictions    
    face_tracker_2_object.update_current_faces(face_and_equipment_detections)
    face_tracker_2_object.draw_faces_on_frame(frame=frame) 

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
    frame = cv2.resize(frame, (1920, 1080))
    cv2.imshow("Miru", frame)        
    if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
        break

# Release all sources
arduino_communicator_object.shutdown_connection()
cap.release()
cv2.destroyAllWindows()