import sys
import os
import copy 
import time

# Determine the absolute path to the directory containing your scripts folder
project_directory = os.path.dirname(os.path.abspath(__file__))
scripts_directory = os.path.join(project_directory, 'scripts')

# Add the scripts directory to the sys.path
sys.path.append(scripts_directory)

# Now you can import your scripts using absolute paths
import pose_detector
import equipment_detector
import arduino_communicator
import slides_show
import face_tracker_memory
import picasso
import wrist_cursor

import cv2
import pprint

arduino_communicator_object = arduino_communicator.ArduinoCommunicator(baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 10, verbose = False, write_delay_s=0.01)
pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")
equipment_detector_object = equipment_detector.EquipmentDetector(model_name="net_google_mask_28_06_2024")
slides_show_object = slides_show.SlideShow(slides_folder="scripts/slides", slide_duration_s=5)
face_manager_with_memory_object = face_tracker_memory.FaceTrackerManager()
wrist_cursor_object = wrist_cursor.WristCursor()


# Open webcam
PARAM_DISPLAY_SIZE = (1920, 1080) #NOTE: DO NOT CHANGE -> fixed miru display size, do not change. Also the camera data is fetched in this size
PARAM_IMAGE_PROCESS_SIZE = (640, 360) #NOTE: DO NOT CHANGE 


last_time_camera_connection_trial = time.time()
cap = cv2.VideoCapture(0)
cap.set(3, PARAM_DISPLAY_SIZE[0])
cap.set(4, PARAM_DISPLAY_SIZE[1])

# Create a window named 'Object Detection' and set the window to fullscreen if desired
cv2.namedWindow('Miru', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Miru', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:      
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        frame = picasso.get_image_as_frame(image_name="camera_connection_error_page", width=PARAM_DISPLAY_SIZE[0], height=PARAM_DISPLAY_SIZE[1], maintain_aspect_ratio=False)
        cv2.imshow("Miru", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
            break

        if time.time() - last_time_camera_connection_trial > 1:
            last_time_camera_connection_trial = time.time()
            cap.release()
            cap = cv2.VideoCapture(0)
            cap.set(3, PARAM_DISPLAY_SIZE[0])
            cap.set(4, PARAM_DISPLAY_SIZE[1])

        continue
    
    frame = cv2.flip(frame, 1) # mirror the frame so that when someone moves their right hand, the cursor moves to the right

    #Arduino communication test
    arduino_communicator_object.ensure_connection()
    arduino_communicator_object.draw_arduino_connection_status_icon(frame)

    coordinate_transform_coefficients = (frame.shape[1] / PARAM_IMAGE_PROCESS_SIZE[0], frame.shape[0] / PARAM_IMAGE_PROCESS_SIZE[1]) # to transform the coordinates of the face bounding boxes to the original frame size from the resized frame size
    resized_frame = cv2.resize(copy.deepcopy(frame), (PARAM_IMAGE_PROCESS_SIZE[0], PARAM_IMAGE_PROCESS_SIZE[1]))
    
    # Predict poses and equipments
    pose_pred_dicts = pose_detector_object.predict_frame_and_return_detections(resized_frame,bbox_confidence=0.35)   
    face_bbox_coords = pose_detector_object.return_face_bboxes_list(frame = resized_frame, predictions= pose_pred_dicts, keypoint_confidence_threshold = 0.80)
    face_manager_with_memory_object.update_face_bboxes(face_bbox_coords)    
    main_face_pose_detection_id = face_manager_with_memory_object.get_main_face_detection_id()

    wrist_cursor_object.update_wrist_cursor_position(main_face_pose_detection_id=main_face_pose_detection_id, pose_pred_dicts=pose_pred_dicts, predicted_frame=resized_frame)
    wrist_cursor_object.draw_wrist_cursor_on_frame(frame)
    wrist_cursor_object.update_wrist_cursor_mode()
    wrist_cursor_object.draw_buttons_on_frame(frame)
 
    equipment_detector_object.predict_frame(resized_frame, bbox_confidence=0.35)
    equipment_formatted_predictions = equipment_detector_object.return_formatted_predictions_list()
    face_manager_with_memory_object.update_face_equipments_detection_confidences_and_obeyed_rules(equipment_formatted_predictions)

    face_manager_with_memory_object.draw_faces_on_frame(frame, coordinate_transform_coefficients=coordinate_transform_coefficients)

    # Send signals to arduino
    if face_manager_with_memory_object.should_turn_on_turnstiles() or wrist_cursor_object.get_mode() == "pass_me_activated":
        arduino_communicator_object.send_activate_turnstile_signal()
    else:
        arduino_communicator_object.send_ping_to_arduino()

    # slide related operations 
    if slides_show_object.should_change_slide():
        slides_show_object.update_current_slide()

    if face_manager_with_memory_object.get_number_of_active_faces() == 0:
        slides_show_object.increase_opacity()
    else:
        slides_show_object.decrease_opacity()

    slide_frame = slides_show_object.get_slide_images(width=frame.shape[1], height=frame.shape[0])

    # Draw slide on top of frame
    frame = slides_show_object.draw_slide_on_top_of_frame(frame=frame, slide_frame=slide_frame)

    # Cursor related UI modifications       
    if wrist_cursor_object.get_mode() == "how_to_use_activated":
        PARAM_CLEARANCE_X = 10
        PARAM_CLEARANCE_Y = 10
        PARAM_RESIZING_FACTOR = 5
        # Resize the UI
        ui_shrinked = cv2.resize(copy.deepcopy(frame), (frame.shape[1] // PARAM_RESIZING_FACTOR, frame.shape[0] // PARAM_RESIZING_FACTOR))

        # Calculate position for bottom right corner with clearance
        x_position = frame.shape[1] - ui_shrinked.shape[1] - PARAM_CLEARANCE_X
        y_position = frame.shape[0] - ui_shrinked.shape[0] - PARAM_CLEARANCE_Y

        # Draw the UI on the frame at the calculated position
        picasso.draw_image_on_frame(frame=frame, image_name="miru_how_to_use_page", x=0, y=0, width=frame.shape[1], height=frame.shape[0], maintain_aspect_ratio=False)
        
        # Place the shrunk UI at the bottom right with clearance
        frame[y_position:y_position + ui_shrinked.shape[0], x_position:x_position + ui_shrinked.shape[1]] = ui_shrinked

    elif wrist_cursor_object.get_mode() in ["pass_me_holding", "pass_me_activated"]:
        wrist_cursor_object.display_pass_me_holding_percentage(frame)

    # Show frame    
    frame = cv2.resize(frame, (PARAM_DISPLAY_SIZE[0], PARAM_DISPLAY_SIZE[1])) # resize the frame to the display size (1920x1080)
    cv2.imshow("Miru", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
        break

# Release all sources
arduino_communicator_object.shutdown_connection()
cap.release()
cv2.destroyAllWindows()