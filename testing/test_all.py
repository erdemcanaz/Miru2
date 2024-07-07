#Tests to perform
print("\n================= TESTS TO PERFORM =================")
PARAM_DELAY_BETWEEN_TESTS = 1 # seconds
PARAM_DISPLAY_SIZE = (1920, 1080) # Fetching size of the webcam feed. Dependent on the webcam quality, resultant frame may be less than this size
PARAM_SHOW_UI_DURATION_INTEGER = 3 # How many seconds the cv2 frame, webcam feed, etc. should be displayed. Should be an integer

PARAM_DO_PYTHON_VERSION_TEST = True
PARAM_DO_SERIAL_LIBRARY_TEST = True 
PARAM_DO_DISPLAY_CV2_FRAME_TEST = True
PARAM_DO_WEBCAM_TEST = True
PARAM_DO_CUDA_AVAILABILITY_TEST = True
PARAM_DO_ULTRALYTICS_YOLOv8_POSE_TEST = True

print("PARAM_DELAY_BETWEEN_TESTS        :", PARAM_DELAY_BETWEEN_TESTS)
print("PARAM_DISPLAY_SIZE               :", PARAM_DISPLAY_SIZE)
print("PARAM_SHOW_UI_DURATION_INTEGER           :", PARAM_SHOW_UI_DURATION_INTEGER)
print("")
print("PARAM_DO_PYTHON_VERSION_TEST     :", PARAM_DO_PYTHON_VERSION_TEST)
print("PARAM_DO_SERIAL_LIBRARY_TEST     :", PARAM_DO_SERIAL_LIBRARY_TEST)
print("PARAM_DO_DISPLAY_CV2_FRAME_TEST  :", PARAM_DO_DISPLAY_CV2_FRAME_TEST)
print("PARAM_DO_WEBCAM_TEST             :", PARAM_DO_WEBCAM_TEST)
print("PARAM_DO_CUDA_AVAILABILITY__TEST :", PARAM_DO_CUDA_AVAILABILITY_TEST)
print("PARAM_DO_ULTRALYTICS_YOLOv8_TEST :", PARAM_DO_ULTRALYTICS_YOLOv8_POSE_TEST)

is_python_version_test_succeded = False
is_serial_library_test_succeded = False
is_display_cv2_frame_test_succeded = False
is_webcam_test_succeded = False
is_cuda_availability_test_succeded = False
is_ultralytics_yolov8_pose_test_succeded = False

# Default imports
print("\n================= DEFAULT IMPORTS =================")
print("Importing 'time' library")
import time

# Python Version Related Tests
if PARAM_DO_PYTHON_VERSION_TEST:
    time.sleep(PARAM_DELAY_BETWEEN_TESTS)
    print("\n================= PYTHON VERSION TESTS =================")
    print("NOTE: The purpose is to check python version. Miru is compatible with Python3.8. Other versions are not guaranteed to work properly\n")

    try:
        print("Importing 'sys' library")
        import sys   
        print("\nPython version:")
        python_version = sys.version
        print(python_version)        
        # Determine if the Python version is 3.8
        is_python_version_test_succeded = python_version.startswith("3.8") 

        if not is_python_version_test_succeded:
            print("\nWARNING: Python version is not 3.8. Miru is compatible with Python3.8. Other versions are not guaranteed to work properly\n")
        print("\n(+++++++++) Test completed without exception.")
    except Exception as e:
        print("EXCEPTION:")
        print(e)

# Serial Library Related Tests
if PARAM_DO_SERIAL_LIBRARY_TEST:
    time.sleep(PARAM_DELAY_BETWEEN_TESTS)
    print("\n================= SERIAL LIBRARY TESTS =================")
    print("NOTE: The purpose is to see whether the arduino is shown in the available ports or not. Thus, make sure that the arduino is connected to the computer. The test is considered succesfull only if there is atleast one port listed\n")
   
    try:
        print("Importing 'serial' library")
        import serial
        print("Importing 'serial.tools.list_ports' library")
        import serial.tools.list_ports
        print("\nGetting available ports:")
        ports = serial.tools.list_ports.comports()

        number_of_ports = len(ports)
        print("Number of available ports:", number_of_ports)
        for i, port in enumerate(ports):
            print(i, port.device)

        if number_of_ports == 0:
            is_serial_library_test_succeded = False
            print("\nWARNING: No ports are available. Make sure that the arduino is connected to the computer. test did not succeed.")

        print("\n(+++++++++) Test completed without exception.")
    except Exception as e:
        print("EXCEPTION:")
        print(e)

# Display CV2 Frame Related Tests
if PARAM_DO_DISPLAY_CV2_FRAME_TEST:
    time.sleep(PARAM_DELAY_BETWEEN_TESTS)
    print("\n================= DISPLAYING CV2 FRAME TESTS =================")
    print("NOTE: The purpose is to display an image using 'cv2' library. It ensures that proper permissions are garanted by the DOCKER container to render an UI\n")

   

    try:
        print("Importing 'cv2' library")
        import cv2
        print("Importing 'pathlib' library")
        from pathlib import Path
        script_path = Path(__file__).absolute()
        tests_folder = script_path.parent.absolute()

        media_path = tests_folder / "test_image.png"
        image = cv2.imread(str(media_path))

        cv2.imshow("Image", image)
        cv2.waitKey(PARAM_SHOW_UI_DURATION_INTEGER*1000)
        cv2.destroyAllWindows()

        print("\n(+++++++++) Test completed without exception.")
        is_display_cv2_frame_test_succeded = True
    except Exception as e:
        print("EXCEPTION:")
        print(e)

# Test web camera
if PARAM_DO_WEBCAM_TEST:
    time.sleep(PARAM_DELAY_BETWEEN_TESTS)
    print("\n================= WEBCAM TESTS =================")
    print("NOTE: The purpose is to display the webcam feed using 'cv2' library. It ensures that the webcam is working properly and data can be fetched.\n")
    try:
        print("Importing 'cv2' library")
        import cv2

        cap = cv2.VideoCapture(0)
        cap.set(3, PARAM_DISPLAY_SIZE[0])
        cap.set(4, PARAM_DISPLAY_SIZE[1])

        start_time = time.time()
        while True:
            ret, frame = cap.read()
            cv2.imshow('Webcam', frame)
            cv2.waitKey(1)

            if time.time() - start_time > PARAM_SHOW_UI_DURATION_INTEGER:
                break

        cap.release()
        cv2.destroyAllWindows()

        print("\n(+++++++++) Test completed without exception.")
        is_webcam_test_succeded = True
    except Exception as e:
        print("EXCEPTION:")
        print(e)

# CUDA Availability Related Tests
if PARAM_DO_CUDA_AVAILABILITY_TEST:
    time.sleep(PARAM_DELAY_BETWEEN_TESTS)
    print("\n================= CUDA AVAILABILITY TESTS =================")    
    print("NOTE: The purpose validate the CUDA is available. If not, you should check the CUDA installation.\n")

    try:
        print("Importing 'torch' library")
        import torch
        print("CUDA availability:", torch.cuda.is_available())
        print("CUDA version:", torch.version.cuda)
        print("CUDA device count:", torch.cuda.device_count())
        print("CUDA device name:", torch.cuda.get_device_name(0))

        is_cuda_availability_test_succeded = torch.cuda.is_available()
        print("\n(+++++++++) Test completed without exception.")
    except Exception as e:
        print("EXCEPTION:")
        print(e)

# Ultralytics YOLOv8 Pose Test
if PARAM_DO_ULTRALYTICS_YOLOv8_POSE_TEST:
    time.sleep(PARAM_DELAY_BETWEEN_TESTS)
    print("\n================= ULTRALYTICS YOLOv8 POSE TESTS =================")
    print("NOTE: The purpose is to test the Ultralytics YOLOv8 Pose model. The test is considered succesfull if the model is loaded without any exception\n")

    try:
        print("Importing 'pathlib' library")
        from pathlib import Path
        print("Importing 'ultralytics' library")
        from ultralytics import YOLO
        script_path = Path(__file__).absolute()
        tests_folder = script_path.parent.absolute()
        yolo_model_path = tests_folder / "yolov8n-pose.pt"
        media_path = tests_folder / "test_image.png"

        print("\nLoading the YOLOv8n-Pose model:")
        yolo_model = YOLO(yolo_model_path)
        results = yolo_model(source=media_path, vid_stride=1, show=True, save=False, conf=0.5)  # return a list of Results objects
        
        time.sleep(PARAM_SHOW_UI_DURATION_INTEGER)

        print("\n(+++++++++) Test completed without exception.")
        is_ultralytics_yolov8_pose_test_succeded = True

    except Exception as e:
        print("EXCEPTION:")
        print(e)


# Summary
print("\n================= SUMMARY =================")
print("is_python_version_test_succeded          :", is_python_version_test_succeded)
print("is_serial_library_test_succeded          :", is_serial_library_test_succeded)
print("is_display_cv2_frame_test_succeded       :", is_display_cv2_frame_test_succeded)
print("is_webcam_test_succeded                  :", is_webcam_test_succeded)
print("is_cuda_availability_test_succeded       :", is_cuda_availability_test_succeded)
print("is_ultralytics_yolov8_pose_test_succeded :", is_ultralytics_yolov8_pose_test_succeded)
