from ultralytics import YOLO
import cv2,math,time,os
import time,pprint,copy
import numpy as np

class PoseDetector(): 
    #keypoints detected by the model in the detection order
    KEYPOINT_NAMES = ["nose", "right_eye", "left_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow" ,"right_elbow","left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"]
    POSE_MODEL_PATHS = {
        "yolov8n":"trained_yolo_models/yolov8n-pose.pt"
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
    
    def get_face_bounding_boxes_coordinates(self, frame:np.ndarray = None, predictions:list[dict] = None, keypoint_confidence_threshold:float = 0.75) -> list[tuple[int,int],tuple[int,int]]:      
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
            
           
        return extracted_face_coordinates

          
        


    def draw_facial_keypoints_on(self, frame:np.ndarray = None, predictions:list[dict] = None, keypoint_confidence_threshold:float = 0.75) -> np.ndarray:
        if predictions is None:
            raise ValueError("No detections provided")
        
        keypoints_to_drawn = ["left_eye", "right_eye", "nose", "left_ear", "right_ear"]
        
        for detection in predictions:
            if detection["class_name"] != "person":
                continue
            for keypoint_name in keypoints_to_drawn:
                keypoint = detection["keypoints"][keypoint_name]
                if keypoint[2] > keypoint_confidence_threshold: #means detected and confidence is above threshold
                    keypoint_x = int(keypoint[0])
                    keypoint_y = int(keypoint[1])
                    cv2.circle(frame, (keypoint_x, keypoint_y), 3, (0,255,0), -1)
                else:
                    continue
            
    def draw_face_bounding_box_on(self, frame:np.ndarray = None, predictions:list[dict] = None, keypoint_confidence_threshold:float = 0.75) -> np.ndarray:
        if predictions is None:
            raise ValueError("No detections provided")
        
        facial_keypoints = ["left_eye", "right_eye", "nose", "left_ear", "right_ear"]
        
        #check which facial keypoints are detected
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
               
                cv2.circle(frame, (int(left_eye_center[0]), int(left_eye_center[1])), 3, (0, 255, 0), -1)
                cv2.circle(frame, (int(right_eye_center[0]), int(right_eye_center[1])), 3, (0, 255, 0), -1)

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

                cv2.rectangle(frame, (face_bbox_x1, face_bbox_y1), (face_bbox_x2, face_bbox_y2), (0, 255, 0), 2)

    def extract_face_bounding_frame(self, frame:np.ndarray = None, predictions:list[dict] = None, keypoint_confidence_threshold:float = 0.75) -> np.ndarray:
        extracted_faces = []
       
        if predictions is None:
            raise ValueError("No detections provided")
        
        facial_keypoints = ["left_eye", "right_eye", "nose", "left_ear", "right_ear"]
        
        #check which facial keypoints are detected
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

                extracted_faces.append(copy.deepcopy(frame[face_bbox_y1:face_bbox_y2, face_bbox_x1:face_bbox_x2]))

               
        return sorted(extracted_faces, key=lambda face: face.shape[0] * face.shape[1], reverse=True)
    
    def extract_and_draw_face_bounding_box_on(self, frame:np.ndarray = None, predictions:list[dict]=None, keypoint_confidence_threshold:float = 0.75, rect_size:int=100) -> np.ndarray:
        extracted_faces = self.extract_face_bounding_frame(frame, predictions, keypoint_confidence_threshold)

        
        # Initialize the position for the first extracted face
        top_left_x, top_left_y = 10, 10  # Starting point for the first face
        padding = 10  # Padding between faces

        for face in extracted_faces:
            #ensure that the ratio of the face is 1:1
            face_height, face_width, _ = face.shape

            if top_left_y + rect_size > frame.shape[0]:  # If the face exceeds the frame height
                continue
            
            ratio = face_height / face_width
            if ratio<0.85 or 1.15 < ratio:
              continue            
            
            face_resized = cv2.resize(face, (rect_size, rect_size))  # Adjust the size as needed

            # Calculate the position to place the face on the top-left corner
            frame[top_left_y:top_left_y + face_resized.shape[0], top_left_x:top_left_x + face_resized.shape[1]] = face_resized

            # Add stroke to the rectangle
            cv2.rectangle(frame, (top_left_x, top_left_y), (top_left_x + face_resized.shape[1], top_left_y + face_resized.shape[0]), (0, 255, 0), 2)

            # Update the position for the next face
            top_left_y += face_resized.shape[0] + padding

        return frame

    def draw_face_detection_rectangle_on(self, is_draw_scan_line:bool=False, frame:np.ndarray=None, fill_color:tuple[int,int,int]=(0,0,0), fill_alpha:float=0.5, stroke_color:tuple[int,int,int]=(0,0,0), face_bbox_coordinates:list[tuple[int,int],tuple[int,int]]=None, stripe_stroke:int=1, bold_stroke:int=5) -> np.ndarray:
        # Add the overlay to the original frame
        overlay_fill = frame.copy()
        cv2.rectangle(overlay_fill, face_bbox_coordinates[0], face_bbox_coordinates[1], fill_color, -1)
        cv2.addWeighted(overlay_fill, fill_alpha, frame, 1 - fill_alpha, 0, frame)      
    
        #draw bounding edges
        cv2.rectangle(frame, face_bbox_coordinates[0], face_bbox_coordinates[1], stroke_color, stripe_stroke)

        #draw bold corners
        width = face_bbox_coordinates[1][0] - face_bbox_coordinates[0][0]
        height = face_bbox_coordinates[1][1] - face_bbox_coordinates[0][1]

        topleft_corner = face_bbox_coordinates[0]
        topleft_1 = (topleft_corner[0]+width//3, topleft_corner[1])
        topleft_2 = (topleft_corner[0], topleft_corner[1]+height//3)                
        cv2.line(frame, topleft_corner, topleft_1, stroke_color, bold_stroke)
        cv2.line(frame, topleft_corner, topleft_2, stroke_color, bold_stroke)

        topright_corner = (face_bbox_coordinates[1][0], face_bbox_coordinates[0][1])
        topright_1 = (topright_corner[0]-width//3, topright_corner[1])
        topright_2 = (topright_corner[0], topright_corner[1]+height//3)
        cv2.line(frame, topright_corner, topright_1, stroke_color, bold_stroke)
        cv2.line(frame, topright_corner, topright_2, stroke_color, bold_stroke)

        bottomleft_corner = (face_bbox_coordinates[0][0], face_bbox_coordinates[1][1])
        bottomleft_1 = (bottomleft_corner[0]+width//3, bottomleft_corner[1])
        bottomleft_2 = (bottomleft_corner[0], bottomleft_corner[1]-height//3)
        cv2.line(frame, bottomleft_corner, bottomleft_1, stroke_color, bold_stroke)
        cv2.line(frame, bottomleft_corner, bottomleft_2, stroke_color, bold_stroke)

        bottomright_corner = face_bbox_coordinates[1]
        bottomright_1 = (bottomright_corner[0]-width//3, bottomright_corner[1])
        bottomright_2 = (bottomright_corner[0], bottomright_corner[1]-height//3)
        cv2.line(frame, bottomright_corner, bottomright_1, stroke_color, bold_stroke)
        cv2.line(frame, bottomright_corner, bottomright_2, stroke_color, bold_stroke)

        #draw scanning line 
        if is_draw_scan_line:
            percentage = time.time()%1
            if percentage < 0.5:
                del_width = int(width * 2*percentage)
            else:
                del_width = int(width * 2*(1-percentage))

            line_top = (face_bbox_coordinates[0][0]+del_width, face_bbox_coordinates[0][1])
            line_bottom = (face_bbox_coordinates[0][0]+del_width, face_bbox_coordinates[1][1])
            cv2.line(frame, line_top, line_bottom, stroke_color, stripe_stroke)
            

        return frame
         
    def draw_detected_face_bounds_on(self, frame:np.ndarray = None, predictions:list[dict]=None, keypoint_confidence_threshold:float = 0.75) -> np.ndarray:
       
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

            for face_no, face_bbox_coordinates in enumerate(extracted_face_coordinates):            
                if face_no == 0: #biggest face
                    is_draw_scan_line = True                
                    fill_alpha = 0.15    
                    stroke_color = (154,14,15)   
                    fill_color = (181,108,108)      
                else:
                    is_draw_scan_line = False
                    stroke_color = (75,75,75)
                    fill_color = (75,75,75)
                    fill_alpha = 0.4

                self.draw_face_detection_rectangle_on(frame=frame, is_draw_scan_line= is_draw_scan_line, fill_color=fill_color, fill_alpha=fill_alpha, stroke_color=stroke_color, face_bbox_coordinates=face_bbox_coordinates, stripe_stroke=3, bold_stroke=10)

        
            
         
               
                
                    
    
        

