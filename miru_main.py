import sys
import os
import copy 

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

import cv2
import pprint

arduino_communicator_object = arduino_communicator.ArduinoCommunicator(baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 10, verbose = False, write_delay_s=0.01)
pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")
equipment_detector_object = equipment_detector.EquipmentDetector(model_name="net_google_mask_28_06_2024")
slides_show_object = slides_show.SlideShow(slides_folder="scripts/slides", slide_duration_s=5)

face_manager_with_memory_object = face_tracker_memory.FaceTrackerManager()

# Open webcam
PARAM_CAMERA_FETCH_SIZE = (1280, 720) # fixed miru display and fetch size, do not change
PARMA_IMAGE_PROCESS_SIZE = (640, 360)
coordinate_transform_coefficients = (PARAM_CAMERA_FETCH_SIZE[0] / PARMA_IMAGE_PROCESS_SIZE[0], PARAM_CAMERA_FETCH_SIZE[1] / PARMA_IMAGE_PROCESS_SIZE[1]) # to transform the coordinates of the face bounding boxes to the original frame size from the resized frame size
cap = cv2.VideoCapture(0)# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW for windows to fast turn on
cap.set(3, PARAM_CAMERA_FETCH_SIZE[0])
cap.set(4, PARAM_CAMERA_FETCH_SIZE[1])

# Create a window named 'Object Detection' and set the window to fullscreen if desired
cv2.namedWindow('Miru', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Miru', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    mode = "normal"

    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame")
        continue
    
    frame = cv2.flip(frame, 1) # mirror the frame 
    
    coordinate_transform_coefficients = (frame.shape[1] / PARMA_IMAGE_PROCESS_SIZE[0], frame.shape[0] / PARMA_IMAGE_PROCESS_SIZE[1]) # to transform the coordinates of the face bounding boxes to the original frame size from the resized frame size
    resized_frame = cv2.resize(copy.deepcopy(frame), (PARMA_IMAGE_PROCESS_SIZE[0], PARMA_IMAGE_PROCESS_SIZE[1]))

    #print(f"frame shape: {frame.shape}, resized frame shape: {resized_frame.shape}, coordinate_transform_coefficients: {coordinate_transform_coefficients}")

    pose_pred_dicts = pose_detector_object.predict_frame_and_return_detections(resized_frame,bbox_confidence=0.35)   
    face_bbox_coords = pose_detector_object.return_face_bboxes_list(frame = resized_frame, predictions= pose_pred_dicts, keypoint_confidence_threshold = 0.80)
    face_manager_with_memory_object.update_face_bboxes(face_bbox_coords)    

    wrist_detections = [] 
    for person in pose_pred_dicts:
        if person["keypoints"]["left_wrist"][2] > 0.80: 
            wrist_detections.append(person["keypoints"]["left_wrist"])
        if person["keypoints"]["right_wrist"][2] > 0.80:
            wrist_detections.append(person["keypoints"]["right_wrist"])

    wrist_x = 0
    wrist_y = 0
    show_wrist_cursor = False
    for wrist in wrist_detections:
        print(f"wrist: {wrist}")
        wrist_x_p = int(wrist[0]*coordinate_transform_coefficients[0])
        wrist_y_p = max(0,int(wrist[1]*coordinate_transform_coefficients[1]-100))

        if not(wrist_x_p > 900 and wrist_y_p < 360):           
            break

        wrist_x = wrist_x_p
        wrist_y = wrist_y_p        
        show_wrist_cursor = True

        if wrist_x > 1040 and wrist_x < 1280 and wrist_y > 0 and wrist_y < 170:
            mode = "how_to_use"

        if wrist_x > 1040 and wrist_x < 1280 and wrist_y > 170 and wrist_y < 340:
            mode = "pass_me"

    if mode == "normal":
        picasso.draw_image_on_frame(frame=frame, image_name="nasil_kullanirim_unclicked", x=1050, y=30, width=200, height=100, maintain_aspect_ratio = True)
        picasso.draw_image_on_frame(frame=frame, image_name="beni_gecir_unclicked", x=1050, y=192, width=200, height=100, maintain_aspect_ratio = True)
    elif mode == "how_to_use":
        picasso.draw_image_on_frame(frame=frame, image_name="nasil_kullanirim_clicked", x=1050, y=30, width=200, height=100, maintain_aspect_ratio = True)
        picasso.draw_image_on_frame(frame=frame, image_name="beni_gecir_unclicked", x=1050, y=192, width=200, height=100, maintain_aspect_ratio = True)
    elif mode == "pass_me":
        picasso.draw_image_on_frame(frame=frame, image_name="nasil_kullanirim_unclicked", x=1050, y=30, width=200, height=100, maintain_aspect_ratio = True)
        picasso.draw_image_on_frame(frame=frame, image_name="beni_gecir_clicked", x=1050, y=192, width=200, height=100, maintain_aspect_ratio = True)
    if show_wrist_cursor: picasso.draw_image_on_frame(frame=frame, image_name="wrist_mouse_icon", x=wrist_x, y=wrist_y, width=60, height=60, maintain_aspect_ratio = True)

    equipment_detector_object.predict_frame(resized_frame, bbox_confidence=0.35)
    equipment_formatted_predictions = equipment_detector_object.return_formatted_predictions_list()
    face_manager_with_memory_object.update_face_equipments_detection_confidences_and_obeyed_rules(equipment_formatted_predictions)

    face_manager_with_memory_object.draw_faces_on_frame(frame, coordinate_transform_coefficients=coordinate_transform_coefficients)

    #Arduino communication test
    arduino_communicator_object.ensure_connection()
    arduino_communicator_object.draw_arduino_connection_status_icon(frame)

    # Send signals to arduino
    if face_manager_with_memory_object.should_turn_on_turnstiles():
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

    # Show frame    
    cv2.imshow("Miru", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
        break

# Release all sources
arduino_communicator_object.shutdown_connection()
cap.release()
cv2.destroyAllWindows()