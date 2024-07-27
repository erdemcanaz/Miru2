from typing import List, Dict, Tuple #for python3.8 compatibility
import pprint
import picasso 
import numpy as np
import cv2
import time

class Face:
    def __init__(self, age_limit:int = 3, sample_size:int = 5, face_bbox:List[Tuple[int,int,int,int,str]] = None):
        self.AGE_LIMIT = age_limit
        self.SAMPLE_SIZE = sample_size
        self.EQUIPMENT_CONFIDENCE_THRESHOLDS = {
            "hair_net":[0.10,0.35],
            "beard_net":[0.10,0.35],
            "safety_goggles":[0.10,0.35],
            "blue_surgical_mask":[0.25,0.50],
            "white_surgical_mask":[0.25,0.50],
        }

        self.age:int = 0 #number of iterations since the face was last detected
        self.face_bbox:list = face_bbox #coordinates of the face bounding box in the format (x1,y1,x2,y2)
        self.face_bbox_transformed:list = None #coordinates of the face bounding box in the format (x1,y1,x2,y2) in the original frame size
        
        self.obeyed_rules = {
            "is_hairnet_worn": False,
            "is_safety_google_worn": False,
            "is_beard_present": False,
            "is_beardnet_worn": False,
            "is_surgical_mask_worn": False,
        }

        self.equipment_detection_confidence_samples = {
            "hair_net":[0]*self.SAMPLE_SIZE,
            "beard_net":[0]*self.SAMPLE_SIZE,
            "safety_goggles":[0]*self.SAMPLE_SIZE,
            "blue_surgical_mask":[0]*self.SAMPLE_SIZE,
            "white_surgical_mask":[0]*self.SAMPLE_SIZE
        }                
        
    def get_face_bbox(self) -> List[Tuple[int,int,int,int,str]]:
        return self.face_bbox
    
    def get_bbox_area(self) -> int:
        return (self.face_bbox[2] - self.face_bbox[0]) * (self.face_bbox[3] - self.face_bbox[1])
    
    def update_face_bbox(self, face_bbox:List[Tuple[int,int,int,int,str]]):
        self.age = 0
        self.face_bbox = face_bbox
  
    def transform_class_name(self, equipment_class:str = None, equipment_bbox:List[Tuple[int,int,int,int,str]] = None) -> str:
        # The object detection model can classify various types of equipment under the same class.
        # For example, both white hairnets and white beard nets are classified as "white_hairnet".
        # This function transforms the general class name into a list of more specific class names.
        
        if equipment_class in ["white_surgical_mask", "blue_surgical_mask"]:
            return equipment_class
        elif equipment_class == "safety_goggles":
            return equipment_class             
        elif equipment_class in ["white_net", "blue_net"]:
            center_of_face = (self.face_bbox[0] + self.face_bbox[2])//2, (self.face_bbox[1] + self.face_bbox[3])//2
            center_of_net = (equipment_bbox[0] + equipment_bbox[2])//2, (equipment_bbox[1] + equipment_bbox[3])//2
            if center_of_face[1] > center_of_net[1]:#net is above face, so it should be hairnet
                return "hair_net"
            else:
                return "beard_net"

    def append_detection_confidences(self, update_dict:Dict):
        for detection_class, confidence in update_dict.items():
            self.equipment_detection_confidence_samples[detection_class].pop(0)        
            self.equipment_detection_confidence_samples[detection_class].append(confidence)        

    def update_obeyed_rules(self) -> None:
       
        self.obeyed_rules = {
            "is_hairnet_worn": False,
            "is_safety_google_worn": False,
            "is_beard_present": False,
            "is_beardnet_worn": False,
            "is_surgical_mask_worn": False,
        }

        hairnet_mean_confidence = sum(self.equipment_detection_confidence_samples["hair_net"]) / len(self.equipment_detection_confidence_samples["hair_net"])
        beardnet_mean_confidence = sum(self.equipment_detection_confidence_samples["beard_net"]) / len(self.equipment_detection_confidence_samples["beard_net"])
        safety_goggles_mean_confidence = sum(self.equipment_detection_confidence_samples["safety_goggles"]) / len(self.equipment_detection_confidence_samples["safety_goggles"])
        blue_surgical_mask_mean_confidence = sum(self.equipment_detection_confidence_samples["blue_surgical_mask"]) / len(self.equipment_detection_confidence_samples["blue_surgical_mask"])
        white_surgical_mask_mean_confidence = sum(self.equipment_detection_confidence_samples["white_surgical_mask"]) / len(self.equipment_detection_confidence_samples["white_surgical_mask"])

        #hairnet
        if self.obeyed_rules["is_hairnet_worn"] and hairnet_mean_confidence < self.EQUIPMENT_CONFIDENCE_THRESHOLDS["hair_net"][0]:
                self.obeyed_rules["is_hairnet_worn"] = False
        elif not self.obeyed_rules["is_hairnet_worn"] and hairnet_mean_confidence > self.EQUIPMENT_CONFIDENCE_THRESHOLDS["hair_net"][1]:
                self.obeyed_rules["is_hairnet_worn"] = True

        #safety goggles
        if self.obeyed_rules["is_safety_google_worn"] and safety_goggles_mean_confidence < self.EQUIPMENT_CONFIDENCE_THRESHOLDS["safety_goggles"][0]:
                self.obeyed_rules["is_safety_google_worn"] = False
        elif not self.obeyed_rules["is_safety_google_worn"] and safety_goggles_mean_confidence > self.EQUIPMENT_CONFIDENCE_THRESHOLDS["safety_goggles"][1]:
                self.obeyed_rules["is_safety_google_worn"] = True

        #beardnet
        if self.obeyed_rules["is_beardnet_worn"] and beardnet_mean_confidence < self.EQUIPMENT_CONFIDENCE_THRESHOLDS["beard_net"][0]:
                self.obeyed_rules["is_beardnet_worn"] = False
        elif not self.obeyed_rules["is_beardnet_worn"] and beardnet_mean_confidence > self.EQUIPMENT_CONFIDENCE_THRESHOLDS["beard_net"][1]:
                self.obeyed_rules["is_beardnet_worn"] = True

        #surgical mask
        if self.obeyed_rules["is_surgical_mask_worn"] and (blue_surgical_mask_mean_confidence < self.EQUIPMENT_CONFIDENCE_THRESHOLDS["blue_surgical_mask"][0] and white_surgical_mask_mean_confidence < self.EQUIPMENT_CONFIDENCE_THRESHOLDS["white_surgical_mask"][0]):
                self.obeyed_rules["is_surgical_mask_worn"] = False
        elif not self.obeyed_rules["is_surgical_mask_worn"] and (blue_surgical_mask_mean_confidence > self.EQUIPMENT_CONFIDENCE_THRESHOLDS["blue_surgical_mask"][1] or white_surgical_mask_mean_confidence > self.EQUIPMENT_CONFIDENCE_THRESHOLDS["white_surgical_mask"][1]):
                self.obeyed_rules["is_surgical_mask_worn"] = True

        #beard detection
        if True:
            self.obeyed_rules["is_beard_present"] = False #TODO: Implement beard detection

    def increase_age(self):
        self.age += 1

    def should_be_deleted(self) -> bool:
        return self.age > self.AGE_LIMIT

    def is_allowed_to_pass(self) -> bool:
        if not (self.obeyed_rules["is_hairnet_worn"] and self.obeyed_rules["is_safety_google_worn"]):
            return False
        if self.obeyed_rules["is_beard_present"] and not (self.obeyed_rules["is_beardnet_worn"] or self.obeyed_rules["is_surgical_mask_worn"]):
            return False
            
        return True

    def draw_face(self, frame: np.ndarray = None, is_main_face: bool = None, stripe_stroke: int = 1, bold_stroke: int = 5, coordinate_transform_coefficients=[1, 1]):
        self.face_bbox_transformed = [
            int(self.face_bbox[0] * coordinate_transform_coefficients[0]),
            int(self.face_bbox[1] * coordinate_transform_coefficients[1]),
            int(self.face_bbox[2] * coordinate_transform_coefficients[0]),
            int(self.face_bbox[3] * coordinate_transform_coefficients[1])
        ]
        
        stroke_color = (108, 208, 142) if is_main_face and self.is_allowed_to_pass() else (82, 82, 255) if is_main_face else (186, 186, 186)
        is_draw_scan_line = is_main_face
        self.__draw_face_detection_rectangle_on(frame, stroke_color, stripe_stroke, bold_stroke, is_draw_scan_line)
        
        max_height = (self.face_bbox_transformed[3] - self.face_bbox_transformed[1]) // 4 + 1
        x_shift = 25
        top_right_corner = (self.face_bbox_transformed[2], self.face_bbox_transformed[1])
        y_shift = 0
        colors = {
            True: "green_" if is_main_face else "grey_",
            False: "red_" if is_main_face else "grey_"
        }
        
        equipment_rules = [
            ("hairnet", self.obeyed_rules["is_hairnet_worn"]),
            ("goggles", self.obeyed_rules["is_safety_google_worn"]),
            ("surgical_mask", self.obeyed_rules["is_surgical_mask_worn"]),
            ("beardnet", self.obeyed_rules["is_beardnet_worn"])
        ]
        
        rules_to_show_only_if_present = ["surgical_mask", "beardnet"] #Some equipments are not mandatory, but should be shown if present
        for equipment, equipment_presence in equipment_rules:
                if equipment_presence == False and (equipment in rules_to_show_only_if_present): 
                    continue

                if equipment_presence == False and not is_main_face:
                    continue

                picasso.draw_image_on_frame(frame, f"{colors[equipment_presence]}{equipment}", top_right_corner[0] + x_shift, top_right_corner[1] + y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
                y_shift += max_height

        if is_main_face:
            max_width = (self.face_bbox[2] - self.face_bbox[0]) // 5
            max_height = (self.face_bbox[3] - self.face_bbox[1]) // 5
            self.__add_approval_disapproval_icons(frame, self.is_allowed_to_pass(), max_width, max_height)

    def __draw_face_detection_rectangle_on(self, frame: np.ndarray, stroke_color: Tuple[int, int, int], stripe_stroke: int, bold_stroke: int, is_draw_scan_line: bool = False) -> np.ndarray:
        # Draw bounding edges
        cv2.rectangle(frame, (self.face_bbox_transformed[0], self.face_bbox_transformed[1]), (self.face_bbox_transformed[2], self.face_bbox_transformed[3]), stroke_color, stripe_stroke)

        # Draw bold corners
        bbox_coordinates = [(self.face_bbox_transformed[0], self.face_bbox_transformed[1]), (self.face_bbox_transformed[2], self.face_bbox_transformed[3])]
        width = bbox_coordinates[1][0] - bbox_coordinates[0][0]
        height = bbox_coordinates[1][1] - bbox_coordinates[0][1]

        corners = [
            (bbox_coordinates[0], (bbox_coordinates[0][0] + width // 3, bbox_coordinates[0][1]), (bbox_coordinates[0][0], bbox_coordinates[0][1] + height // 3)),
            ((bbox_coordinates[1][0], bbox_coordinates[0][1]), (bbox_coordinates[1][0] - width // 3, bbox_coordinates[0][1]), (bbox_coordinates[1][0], bbox_coordinates[0][1] + height // 3)),
            ((bbox_coordinates[0][0], bbox_coordinates[1][1]), (bbox_coordinates[0][0] + width // 3, bbox_coordinates[1][1]), (bbox_coordinates[0][0], bbox_coordinates[1][1] - height // 3)),
            (bbox_coordinates[1], (bbox_coordinates[1][0] - width // 3, bbox_coordinates[1][1]), (bbox_coordinates[1][0], bbox_coordinates[1][1] - height // 3))
        ]

        for corner, line1_end, line2_end in corners:
            cv2.line(frame, corner, line1_end, stroke_color, bold_stroke)
            cv2.line(frame, corner, line2_end, stroke_color, bold_stroke)

        # Draw scanning line
        if is_draw_scan_line:
            percentage = time.time() % 1
            del_width = int(width * 2 * (percentage if percentage < 0.5 else 1 - percentage))

            line_top = (bbox_coordinates[0][0] + del_width, bbox_coordinates[0][1])
            line_bottom = (bbox_coordinates[0][0] + del_width, bbox_coordinates[1][1])
            cv2.line(frame, line_top, line_bottom, stroke_color, stripe_stroke)
            
        return frame

    def __add_approval_disapproval_icons(self, frame: np.ndarray, is_approved: bool, max_width: int, max_height: int) -> np.ndarray:
        icon_name = "approval" if is_approved else "disapproval"
        x_position = self.face_bbox_transformed[0] - max_width // 2
        y_position = self.face_bbox_transformed[1] - max_height // 2
        picasso.draw_image_on_frame(frame, icon_name, x=x_position, y=y_position, width=max_width, height=max_height, maintain_aspect_ratio=True)

class FaceTrackerManager:
    def __init__(self, face_update_overlap_threshold:float = 0.5, equipment_update_overlap_threshold:float = 0.5):
        self.FACE_UPDATE_OVERLAP_THRESHOLD = face_update_overlap_threshold #minimum overlap between face bboxes to be considered the same face
        self.EQUIPMENT_UPDATE_OVERLAP_THRESHOLD = equipment_update_overlap_threshold #minimum overlap between face bbox and equipment bbox to be considered the same face
        self.face_objects = []

    def get_number_of_active_faces(self) -> int:
        return len(self.face_objects)
    
    def __calculate_overlap(self, bbox1:List[Tuple[int,int,int,int,str]], bbox2:List[Tuple[int,int,int,int,str]]) -> float: 
        # Returns how much percentage of bbox2 inside bbox1 
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])

        intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)
        bbox2_area = (bbox2[2] - bbox2[0] + 1) * (bbox2[3] - bbox2[1] + 1)
        return intersection_area / bbox2_area

    def update_face_bboxes(self, face_bboxes: List[Tuple[int, int, int, int]]):
        matched_face_bboxes = []
        for face_bbox in face_bboxes:
            best_match = None
            max_overlap = 0
            for face in self.face_objects:
                overlap = self.__calculate_overlap(face.get_face_bbox(), face_bbox)
                if overlap > max_overlap:
                    best_match = face
                    max_overlap = overlap

            if max_overlap > self.FACE_UPDATE_OVERLAP_THRESHOLD:
                best_match.update_face_bbox(face_bbox)
                matched_face_bboxes.append(face_bbox)

        # Create new face objects for unmatched face bboxes
        for face_bbox in face_bboxes:
            if face_bbox not in matched_face_bboxes:
                self.face_objects.append(Face(face_bbox=face_bbox))

        # Increase age of all faces
        faces_to_delete = []
        for face in self.face_objects:
            face.increase_age()
            if face.should_be_deleted():
                faces_to_delete.append(face)

        # Delete faces that are too old
        for face in faces_to_delete:
            self.face_objects.remove(face)
    
    def update_face_equipments_detection_confidences_and_obeyed_rules(self, equipment_predictions: List[Tuple[str, float, Tuple[int, int, int, int,str]]]):
            for face in self.face_objects:                
                detected_equipments = {
                    "hair_net":0,
                    "beard_net":0,
                    "safety_goggles":0,
                    "blue_surgical_mask":0,
                    "white_surgical_mask":0
                }

                for equipment_prediction in equipment_predictions:
                    equipment_class = equipment_prediction[0]      
                    equipment_bbox = equipment_prediction[2]
                    if self.__calculate_overlap(face.get_face_bbox(), equipment_bbox) > self.EQUIPMENT_UPDATE_OVERLAP_THRESHOLD:
                        transformed_class_name = face.transform_class_name(equipment_class, equipment_bbox)
                        detected_equipments[transformed_class_name] = max(equipment_prediction[1], detected_equipments[transformed_class_name])

                face.append_detection_confidences(detected_equipments)
                face.update_obeyed_rules()

    def draw_faces_on_frame(self, frame:np.ndarray, main_face_id:str = "", coordinate_transform_coefficients=[1,1]) -> np.ndarray:     
        for face in self.face_objects:
            if main_face_id == face.get_face_bbox()[4]:
                face.draw_face(frame=frame, is_main_face = True, stripe_stroke = 2, bold_stroke= 10, coordinate_transform_coefficients=coordinate_transform_coefficients)
            else:                
                face.draw_face(frame=frame, is_main_face = False, coordinate_transform_coefficients=coordinate_transform_coefficients)
    
        #picasso.draw_image_on_frame(frame=frame, image_name="information", x=50, y=50, width=100, height=100, maintain_aspect_ratio=True)
    
    def get_main_face_detection_id(self, main_face_according_to:str = "AREA", frame = None) -> str:
        main_face = None
        if main_face_according_to == "AREA":
            max_area = 0
            for face in self.face_objects:
                face_area = face.get_bbox_area()
                if face_area > max_area:
                    max_area = face_area
                    main_face = face
            if main_face is None:
                return ""
            return main_face.get_face_bbox()[4]
        elif main_face_according_to == "CLOSEST_TO_CENTER":
            if frame is None:
                return ""
            min_distance = float("inf")
            for face in self.face_objects:
                center_of_face = (face.get_face_bbox()[0] + face.get_face_bbox()[2])//2, (face.get_face_bbox()[1] + face.get_face_bbox()[3])//2
                distance = (center_of_face[0] - frame.shape[1]//2)**2 + (center_of_face[1] - frame.shape[0]//2)**2
                if distance < min_distance:
                    min_distance = distance
                    main_face = face

            if main_face is None:
                return ""
            return main_face.get_face_bbox()[4]
        else:
            return ""
    
    def should_turn_on_turnstiles(self, main_face_id:str = "") -> bool:
        print(f"Main face id: {main_face_id}")
        for face in self.face_objects:
            if main_face_id == face.get_face_bbox()[4]:
                print("Face is allowed to pass") if face.is_allowed_to_pass() else print("Face is not allowed to pass")
                return face.is_allowed_to_pass()
        else: # if for is completed without break
            print("No face detected")
            return False
        


             

                        

  
