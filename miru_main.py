import sys
import os, platform
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

# PARAMETERS ========================================================================================================
PARAM_ZOOM_FACTOR = 0.50 # length of ROI edge in terms of the frame edge length 
PARAM_ZOOM_TOPLEFT_NORMALIZED = (0.25, 0.25) # top left corner of the zoomed region in normalized coordinates
PARAM_DISPLAY_SIZE = (1920, 1080) #NOTE: DO NOT CHANGE -> fixed miru display size, do not change. Also the camera data is fetched in this size
PARAM_IMAGE_PROCESS_SIZE = (640, 360) #NOTE: DO NOT CHANGE, model input size. If you change, the model will resize the image to this size before processing it. But it is kinda more relaxing to do it beforehand :)
PARAM_KEEP_TURNED_ON_TIME = 3.5 #NOTE: this parameter shoudl be same as the one in the arduino code
PARAM_CAP_RESOLUTIONS_TO_CHECK = [# List of common couples to try as webcam resolution. Should be in descending order of preference
    (1920, 1080),
    (1280, 720),
    (1024, 768),
    (800, 600),
    (640, 480),
    (320, 240)
]
if PARAM_ZOOM_TOPLEFT_NORMALIZED[0] + PARAM_ZOOM_FACTOR > 1 or PARAM_ZOOM_TOPLEFT_NORMALIZED[1] + PARAM_ZOOM_FACTOR > 1:
    raise ValueError("Zoomed region is out of frame boundaries")

# OBJECTS ========================================================================================================
arduino_communicator_object = arduino_communicator.ArduinoCommunicator(baud_rate=9600, serial_timeout=1, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 60, verbose = False, write_delay_s=0.01,arduino_reboot_time=3)
pose_detector_object = pose_detector.PoseDetector(model_name="yolov8n")
equipment_detector_object = equipment_detector.EquipmentDetector(model_name="miru_model_03_08_2024")
slides_show_object = slides_show.SlideShow(slides_folder="scripts/slides", slide_duration_s=5)
face_manager_with_memory_object = face_tracker_memory.FaceTrackerManager()
wrist_cursor_object = wrist_cursor.WristCursor()

# UI SETUP ========================================================================================================
cv2.namedWindow('Miru', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Miru', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
last_time_ui_restart = time.time()
UI_RESTART_DURATION_SEC = 10

# INIT CAMERA ========================================================================================================
cap = None
is_linux = platform.system() == "Linux"
if is_linux:
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    print(f"V4L2 is used for camera connection because OS='{platform.system()}'")
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FPS, 30)
else:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print(f"DShow is used for camera connection because OS='{platform.system()}'")

if not cap.isOpened():
    raise ValueError("Unable to open the camera")

# Verify the codec
fourcc_actual = int(cap.get(cv2.CAP_PROP_FOURCC))
codec = (
    chr((fourcc_actual & 0xFF)),
    chr((fourcc_actual >> 8) & 0xFF),
    chr((fourcc_actual >> 16) & 0xFF),
    chr((fourcc_actual >> 24) & 0xFF)
)
codec = "".join(codec)
print(f"Camera codec: {codec}")

def check_resolution(cap, width, height):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return (actual_width, actual_height) == (width, height)

# Try resolutions until one works
selected_resolution = None
for width, height in PARAM_CAP_RESOLUTIONS_TO_CHECK:
    print(f"    Trying resolution: {width}x{height}")
    if check_resolution(cap, width, height):
        selected_resolution = (width, height)
        print(f"->Selected resolution: {width}x{height}")
        break

if not selected_resolution:
    raise ValueError("None of the common resolutions are supported by the camera.")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, selected_resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, selected_resolution[1])

# Verify the resolution
actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Camera resolution is validated to be: {actual_width}x{actual_height}")

if (actual_width, actual_height) != PARAM_DISPLAY_SIZE:
    print(f"Warning: Camera resolution does not match the display size. Expected: {PARAM_DISPLAY_SIZE}, Actual: {actual_width}x{actual_height}")

# MAIN LOOP ========================================================================================================
last_time_turnstile_activated = 0
while True:      
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        frame = picasso.get_image_as_frame(image_name="camera_connection_error_page", width=PARAM_DISPLAY_SIZE[0], height=PARAM_DISPLAY_SIZE[1], maintain_aspect_ratio=False)
        cv2.imshow("Miru", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
            break
        continue #Otherwise, the frame will result in an error since it also has alpha channel during object detection, never let this frame to be processed
    
    if frame.shape[1] != PARAM_DISPLAY_SIZE[0] or frame.shape[0] != PARAM_DISPLAY_SIZE[1]:
        # Since camera supposed to be in the same resolution as the display, this should not happen. But if it happens, resize the frame
        frame = cv2.resize(frame, (PARAM_DISPLAY_SIZE[0], PARAM_DISPLAY_SIZE[1]))

    #apply digital zoom to the frame. Essepically useful for detecting small objects at a distance
    if PARAM_ZOOM_FACTOR < 1:
        zoomed_region_top_left = (int(PARAM_ZOOM_TOPLEFT_NORMALIZED[0] * frame.shape[1]), int(PARAM_ZOOM_TOPLEFT_NORMALIZED[1] * frame.shape[0]))
        zoomed_region_bottom_right = (int(zoomed_region_top_left[0] + PARAM_ZOOM_FACTOR * frame.shape[1]), int(zoomed_region_top_left[1] + PARAM_ZOOM_FACTOR * frame.shape[0]))
        frame = frame[zoomed_region_top_left[1]:zoomed_region_bottom_right[1], zoomed_region_top_left[0]:zoomed_region_bottom_right[0]]
        
    # mirror the frame so that the movements are more intuitive
    frame = cv2.flip(frame, 1) 

    # Resize frame to the desired processing size of the model
    resized_frame = cv2.resize(copy.deepcopy(frame), (PARAM_IMAGE_PROCESS_SIZE[0], PARAM_IMAGE_PROCESS_SIZE[1]))

    #Arduino communication test
    arduino_communicator_object.ensure_connection()
    is_arduino_connected = arduino_communicator_object.get_connection_status()       
    is_turnstile_on = time.time() - last_time_turnstile_activated < PARAM_KEEP_TURNED_ON_TIME   

    # Predict poses-wrist cursor and equipments
    pose_pred_dicts = pose_detector_object.predict_frame_and_return_detections(resized_frame,bbox_confidence=0.35)   
    face_bbox_coords = pose_detector_object.return_face_bboxes_list(frame = resized_frame, predictions= pose_pred_dicts, keypoint_confidence_threshold = 0.80)
    face_manager_with_memory_object.update_face_bboxes(face_bbox_coords)    
    main_face_pose_detection_id = face_manager_with_memory_object.get_main_face_detection_id(main_face_according_to = "CLOSEST_TO_CENTER", frame = resized_frame)

    wrist_cursor_object.update_wrist_cursor_position(main_face_pose_detection_id=main_face_pose_detection_id, pose_pred_dicts=pose_pred_dicts, predicted_frame=resized_frame)
    wrist_cursor_object.update_wrist_cursor_mode()
    
    equipment_detector_object.predict_frame(resized_frame, bbox_confidence=0.35)
    equipment_formatted_predictions = equipment_detector_object.return_formatted_predictions_list()
    face_manager_with_memory_object.update_face_equipments_detection_confidences_and_obeyed_rules(equipment_formatted_predictions)
    
    # slide related operations 
    if slides_show_object.should_change_slide():
        slides_show_object.update_current_slide()
        
    if face_manager_with_memory_object.get_number_of_active_faces() == 0:
        slides_show_object.increase_opacity()
    else:
        slides_show_object.decrease_opacity()

    # Send signals to arduino
    if face_manager_with_memory_object.should_turn_on_turnstiles( main_face_id = main_face_pose_detection_id ) or wrist_cursor_object.get_mode() == "pass_me_activated":
        arduino_communicator_object.send_activate_turnstile_signal()
        last_time_turnstile_activated = time.time()
    else:
        arduino_communicator_object.send_ping_to_arduino()

    # SHOW FRAME ========================================================================================================  
    frame = cv2.resize(frame, (PARAM_DISPLAY_SIZE[0], PARAM_DISPLAY_SIZE[1])) # resize the frame to the display size (1920x1080)
    
    wrist_cursor_object.draw_buttons_on_frame(frame)

    coordinate_transform_coefficients = (frame.shape[1] / PARAM_IMAGE_PROCESS_SIZE[0], frame.shape[0] / PARAM_IMAGE_PROCESS_SIZE[1]) # to transform the coordinates of the face bounding boxes to the original frame size from the resized frame size
    face_manager_with_memory_object.draw_faces_on_frame(frame, main_face_id = main_face_pose_detection_id, coordinate_transform_coefficients=coordinate_transform_coefficients)

    wrist_cursor_object.draw_wrist_cursor_on_frame(frame)

    if is_arduino_connected:
        print("Arduino is connected")
        picasso.draw_image_on_frame(frame=frame, image_name="arduino_connection_blue", x=10, y=10, width=100, height=100, maintain_aspect_ratio=False)
    else:
        print("Arduino is not connected")
        picasso.draw_image_on_frame(frame=frame, image_name="arduino_connection_grey", x=10, y=10, width=100, height=100, maintain_aspect_ratio=False)
    
    # draw turnstile status icon
    if is_turnstile_on and arduino_communicator_object.get_connection_status():
        picasso.draw_image_on_frame(frame=frame, image_name="turnstile_blue", x=120, y=10, width=100, height=100, maintain_aspect_ratio=False)
    else:
        picasso.draw_image_on_frame(frame=frame, image_name="tursntile_grey", x=120, y=10, width=100, height=100, maintain_aspect_ratio=False)

    # Cursor related UI modifications       
    if wrist_cursor_object.get_mode() == "how_to_use_activated":

        # Shrink UI
        PARAM_CLEARANCE_X = 10
        PARAM_CLEARANCE_Y = 10
        PARAM_RESIZING_FACTOR = 5
        ui_shrinked = cv2.resize(copy.deepcopy(frame), (frame.shape[1] // PARAM_RESIZING_FACTOR, frame.shape[0] // PARAM_RESIZING_FACTOR))
        x_position = frame.shape[1] - ui_shrinked.shape[1] - PARAM_CLEARANCE_X
        y_position = frame.shape[0] - ui_shrinked.shape[0] - PARAM_CLEARANCE_Y

        picasso.draw_image_on_frame(frame=frame, image_name="miru_how_to_use_page", x=0, y=0, width=frame.shape[1], height=frame.shape[0], maintain_aspect_ratio=False)
        
        # Place the shrunk UI at the bottom right with clearance
        frame[y_position:y_position + ui_shrinked.shape[0], x_position:x_position + ui_shrinked.shape[1]] = ui_shrinked

    elif is_turnstile_on or wrist_cursor_object.get_mode() in ["pass_me_holding", "pass_me_activated"]:
        wrist_cursor_object.display_pass_me_holding_percentage(frame, is_arduion_connected=is_arduino_connected, is_turnstile_on=is_turnstile_on)

    # Draw slide on top of frame according to the opacity
    slide_frame = slides_show_object.get_slide_images(width=frame.shape[1], height=frame.shape[0]) 
    frame = slides_show_object.draw_slide_on_top_of_frame(frame=frame, slide_frame=slide_frame)

    if time.time() - last_time_ui_restart > UI_RESTART_DURATION_SEC:
        cv2.destroyAllWindows()
        cv2.namedWindow('Miru', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Miru', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        last_time_ui_restart = time.time()           

    cv2.imshow("Miru", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):   # Break loop if 'q' is pressed
        break

# Release all sources
arduino_communicator_object.shutdown_connection()
cap.release()
cv2.destroyAllWindows()