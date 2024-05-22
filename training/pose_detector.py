from ultralytics import YOLO
import cv2,math,time,os
import time,pprint,copy
import numpy as np

class PoseDetector(): 
    #keypoints detected by the model in the detection order
    KEYPOINT_NAMES = ["nose", "right_eye", "left_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow" ,"right_elbow","left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"]
    POSE_MODEL_PATHS = {
        "yolov8n-pose":"trained_yolo_models/yolov8n-pose.pt"
    }

    def __init__(self, model_name: str = None ) -> None:   
        if model_name not in PoseDetector.POSE_MODEL_PATHS.keys():
            raise ValueError(f"Invalid model name. Available models are: {PoseDetector.POSE_MODEL_PATHS.keys()}")
        self.MODEL_PATH = PoseDetector.POSE_MODEL_PATHS[model_name]        
        self.yolo_object = YOLO( self.MODEL_PATH, verbose= True)        
        self.recent_prediction_results = None # This will be a list of dictionaries, each dictionary will contain the prediction results for a single detection

    def get_empty_prediction_dict_template(self) -> dict:
        empty_prediction_dict = {   
                    "DETECTOR_TYPE":"PoseDetector",                             # which detector made this prediction
                    "frame_shape": [0,0],                                       # [0,0], [height , width] in pixels
                    "class_name":"",                                            # hard_hat, no_hard_hat
                    "bbox_confidence":0,                                        # 0.0 to 1.0
                    "bbox_xyxy_px":[0,0,0,0],                                   # [x1,y1,x2,y2] in pixels
                    "bbox_center_px": [0,0],                                    # [x,y] in pixels
                    #------------------pose specific fields------------------
                    "keypoints": {                                              # Keypoints are in the format [x,y,confidence]
                        "left_eye": [0,0,0,0,0],
                        "right_eye": [0,0,0,0,0],
                        "nose": [0,0,0,0,0],
                        "left_ear": [0,0,0,0,0],
                        "right_ear": [0,0,0,0,0],
                        "left_shoulder": [0,0,0,0,0],
                        "right_shoulder": [0,0,0,0,0],
                        "left_elbow": [0,0,0,0,0],
                        "right_elbow": [0,0,0,0,0],
                        "left_wrist": [0,0,0,0,0],
                        "right_wrist": [0,0,0,0,0],
                        "left_hip": [0,0,0,0,0],
                        "right_hip": [0,0,0,0,0],
                        "left_knee": [0,0,0,0,0],
                        "right_knee": [0,0,0,0,0],
                        "left_ankle": [0,0,0,0,0],
                        "right_ankle": [0,0,0,0,0],
                    }
        }
        return empty_prediction_dict
    
    def predict_frame_and_return_detections(self, frame:np.ndarray = None, bbox_confidence:float=0.75) -> list[dict]:
        self.recent_prediction_results = []
        
        results = self.yolo_object(frame, task = "pose", verbose= False)[0]
        for i, result in enumerate(results):
            boxes = result.boxes
            box_cls_no = int(boxes.cls.cpu().numpy()[0])
            box_cls_name = self.yolo_object.names[box_cls_no]
            if box_cls_name not in ["person"]:
                continue
            box_conf = boxes.conf.cpu().numpy()[0]
            if box_conf < bbox_confidence:
                continue
            box_xyxy = boxes.xyxy.cpu().numpy()[0]

            prediction_dict_template = self.get_empty_prediction_dict_template()
            prediction_dict_template["frame_shape"] = list(results.orig_shape)
            prediction_dict_template["class_name"] = box_cls_name
            prediction_dict_template["bbox_confidence"] = box_conf
            prediction_dict_template["bbox_xyxy_px"] = box_xyxy # Bounding box in the format [x1,y1,x2,y2]
            prediction_dict_template["bbox_center_px"] = [ (box_xyxy[0]+box_xyxy[2])/2, (box_xyxy[1]+box_xyxy[3])/2]
            
            key_points = result.keypoints  # Keypoints object for pose outputs
            keypoint_confs = key_points.conf.cpu().numpy()[0]
            keypoints_xy = key_points.xy.cpu().numpy()[0]
                       
            for keypoint_index, keypoint_name in enumerate(PoseDetector.KEYPOINT_NAMES):
                keypoint_conf = keypoint_confs[keypoint_index] 
                keypoint_x = keypoints_xy[keypoint_index][0]
                keypoint_y = keypoints_xy[keypoint_index][1]
                if keypoint_x == 0 and keypoint_y == 0: #if the keypoint is not detected
                    #But this is also a prediction. Thus the confidence should not be set to zero. negative values are used to indicate that the keypoint is not detected
                    keypoint_conf = -keypoint_conf

                prediction_dict_template["keypoints"][keypoint_name] = [keypoint_x, keypoint_y , keypoint_conf]

                
            self.recent_prediction_results.append(prediction_dict_template)
        
        return self.recent_prediction_results
                
    def get_fbbox_frames(self, frame:np.ndarray = None, predictions:list[dict] = None, keypoint_confidence_threshold:float = 0.75, desired_image_edge_lengths:int = 150) -> list[np.ndarray]:
        extracted_faces = []
       
        if predictions is None:
            raise ValueError("No detections provided")
        
        extracted_face_coordinates = []
        facial_keypoints = ["left_eye", "right_eye", "nose", "left_ear", "right_ear"]

        for detection in predictions:
            if detection["class_name"] != "person":
                continue

            detected_keypoints = {
                "left_eye": False,
                "right_eye": False,
                "nose": False,
                "left_ear": False,
                "right_ear": False
            }

            for keypoint_name in facial_keypoints:
                keypoint = detection["keypoints"][keypoint_name]
                if keypoint[2] > keypoint_confidence_threshold: #means detected and confidence is above threshold
                    detected_keypoints[keypoint_name] = True                    
                else:
                    continue

            #draw face bounding box if eyes and the nose are detected
            if detected_keypoints["left_eye"] and detected_keypoints["right_eye"]:
                #print("Face detected")
                            
                frame_height, frame_width, _ = frame.shape
            
                left_eye_center = (detection["keypoints"]["left_eye"][0],detection["keypoints"]["left_eye"][1])
                right_eye_center = (detection["keypoints"]["right_eye"][0],detection["keypoints"]["right_eye"][1])               
    

                distance_between_eyes = abs(left_eye_center[0] - right_eye_center[0])
                face_center_x = (left_eye_center[0] + right_eye_center[0]) // 2
                face_center_y = (left_eye_center[1] + right_eye_center[1]) // 2

                # Define box size based on the distance between eyes
                box_width = int(4.0 * distance_between_eyes) # Adjust the multiplier as needed
                box_height = int(4.0 * distance_between_eyes) # Adjust the multiplier as needed

                # Calculate the top-left and bottom-right coordinates
                face_bbox_x1 = int(max(0, face_center_x - box_width // 2))
                face_bbox_y1 = int(max(0, face_center_y - box_height // 2))
                face_bbox_x2 = int(min(frame_width - 1, face_center_x + box_width // 2))
                face_bbox_y2 = int(min(frame_height - 1, face_center_y + box_height // 2))

                #cv2.rectangle(frame, (face_bbox_x1, face_bbox_y1), (face_bbox_x2, face_bbox_y2), (0, 255, 0), 2)

                extracted_face_coordinates.append(copy.deepcopy([(face_bbox_x1,face_bbox_y1), (face_bbox_x2,face_bbox_y2)]))

            #sort extracted faces by size
            extracted_face_coordinates = sorted(extracted_face_coordinates, key=lambda face: (face[1][0]-face[0][0]) * (face[1][1]-face[0][1]), reverse=True)
            for face_bbox_coordinates in extracted_face_coordinates:
                extracted_face = copy.deepcopy(frame[face_bbox_coordinates[0][1]:face_bbox_coordinates[1][1], face_bbox_coordinates[0][0]:face_bbox_coordinates[1][0]])
                # Resize the extracted face to a specific value
                resized_face = cv2.resize(extracted_face, (desired_image_edge_lengths, desired_image_edge_lengths))
                extracted_faces.append(resized_face)
           
        return extracted_faces

          
        
                    
    
        

