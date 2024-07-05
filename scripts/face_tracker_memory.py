from typing import List, Dict, Tuple #for python3.8 compatibility
import pprint
import picasso 
import numpy as np
import cv2
import time

class Face:
    def __init__(self, age_limit:int = 3, sample_size:int = 5, face_bbox:List[Tuple[int,int,int,int]] = None):
        self.AGE_LIMIT = age_limit
        self.SAMPLE_SIZE = sample_size
        self.EQUIPMENT_CONFIDENCE_THRESHOLDS = {
            "hair_net":[0.25,0.50],
            "beard_net":[0.25,0.50],
            "safety_goggles":[0.25,0.50],
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
        
    def get_face_bbox(self) -> List[Tuple[int,int,int,int]]:
        return self.face_bbox
    
    def get_bbox_area(self) -> int:
        return (self.face_bbox[2] - self.face_bbox[0]) * (self.face_bbox[3] - self.face_bbox[1])
    
    def update_face_bbox(self, face_bbox:List[Tuple[int,int,int,int]]):
        self.age = 0
        self.face_bbox = face_bbox
  
    def transform_class_name(self, equipment_class:str = None, equipment_bbox:List[Tuple[int,int,int,int]] = None) -> str:
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

        print("Safety Goggles Confidence: ", safety_goggles_mean_confidence)

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

    
    def draw_face(self, frame:np.ndarray=None, is_main_face:bool = None, stripe_stroke:int=1, bold_stroke:int=5, coordinate_transform_coefficients=[1,1]):
        self.face_bbox_transformed = [int(self.face_bbox[0]*coordinate_transform_coefficients[0]), int(self.face_bbox[1]*coordinate_transform_coefficients[1]), int(self.face_bbox[2]*coordinate_transform_coefficients[0]), int(self.face_bbox[3]*coordinate_transform_coefficients[1])]
        if is_main_face:
            stroke_color = (108,208,142) if self.is_allowed_to_pass() else (82,82,255) #green or red
            self.__draw_face_detection_rectangle_on(is_draw_scan_line=True, frame=frame, stroke_color=stroke_color, stripe_stroke=stripe_stroke, bold_stroke=bold_stroke)   
            self.__add_equipment_icons_main_face(frame=frame)

            max_width = (self.face_bbox[2] - self.face_bbox[0])//5
            max_height = (self.face_bbox[3] - self.face_bbox[1])//5
            self.__add_approval_disapproval_icons(frame=frame, is_approved=self.is_allowed_to_pass(), max_width=max_width, max_height=max_height)
        
        else:
            stroke_color = (186,186,186)
            self.__draw_face_detection_rectangle_on(is_draw_scan_line=False, frame=frame, stroke_color=stroke_color, stripe_stroke=stripe_stroke, bold_stroke=bold_stroke)
            self._add_equipment_icons_secondary_faces(frame=frame)
            
    def __draw_face_detection_rectangle_on(self, is_draw_scan_line:bool=False, frame:np.ndarray=None, stroke_color:Tuple[int,int,int]=(0,0,0), stripe_stroke:int=1, bold_stroke:int=5) -> np.ndarray:
    
        #draw bounding edges
        cv2.rectangle(frame, (self.face_bbox_transformed[0],self.face_bbox_transformed[1]),  (self.face_bbox_transformed[2],self.face_bbox_transformed[3]), stroke_color, stripe_stroke)

        #draw bold corners
        bbox_coordinates = [(self.face_bbox_transformed[0],self.face_bbox_transformed[1] ),(self.face_bbox_transformed[2],self.face_bbox_transformed[3] )]
        width =  bbox_coordinates[1][0] -  bbox_coordinates[0][0]
        height =  bbox_coordinates[1][1] -  bbox_coordinates[0][1]

        topleft_corner =  bbox_coordinates[0]
        topleft_1 = (topleft_corner[0]+width//3, topleft_corner[1])
        topleft_2 = (topleft_corner[0], topleft_corner[1]+height//3)                
        cv2.line(frame, topleft_corner, topleft_1, stroke_color, bold_stroke)
        cv2.line(frame, topleft_corner, topleft_2, stroke_color, bold_stroke)

        topright_corner = ( bbox_coordinates[1][0],  bbox_coordinates[0][1])
        topright_1 = (topright_corner[0]-width//3, topright_corner[1])
        topright_2 = (topright_corner[0], topright_corner[1]+height//3)
        cv2.line(frame, topright_corner, topright_1, stroke_color, bold_stroke)
        cv2.line(frame, topright_corner, topright_2, stroke_color, bold_stroke)

        bottomleft_corner = ( bbox_coordinates[0][0],  bbox_coordinates[1][1])
        bottomleft_1 = (bottomleft_corner[0]+width//3, bottomleft_corner[1])
        bottomleft_2 = (bottomleft_corner[0], bottomleft_corner[1]-height//3)
        cv2.line(frame, bottomleft_corner, bottomleft_1, stroke_color, bold_stroke)
        cv2.line(frame, bottomleft_corner, bottomleft_2, stroke_color, bold_stroke)

        bottomright_corner =  bbox_coordinates[1]
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

            line_top = ( bbox_coordinates[0][0]+del_width,  bbox_coordinates[0][1])
            line_bottom = ( bbox_coordinates[0][0]+del_width,  bbox_coordinates[1][1])
            cv2.line(frame, line_top, line_bottom, stroke_color, stripe_stroke)
            
        return frame

    def __add_equipment_icons_main_face(self,frame):
                
        max_height = int((self.face_bbox_transformed[3] - self.face_bbox_transformed[1] )/4)+1

        x_shift = 25
        top_right_corner = (self.face_bbox_transformed[2], self.face_bbox_transformed[1])
        y_shift = 0
        if self.obeyed_rules["is_hairnet_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="green_hairnet", x=top_right_corner[0]+x_shift, y=top_right_corner[1], width=100, height=max_height, maintain_aspect_ratio=True)
        else:
            picasso.draw_image_on_frame(frame=frame, image_name="red_hairnet", x=top_right_corner[0]+x_shift, y=top_right_corner[1], width=100, height=max_height, maintain_aspect_ratio=True)
        y_shift += max_height

        if self.obeyed_rules["is_safety_google_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="green_goggles", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
        else:
            picasso.draw_image_on_frame(frame=frame, image_name="red_goggles", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
        y_shift += max_height

        if self.obeyed_rules["is_surgical_mask_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="green_surgical_mask", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
            y_shift +=max_height

        if self.obeyed_rules["is_beardnet_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="green_beardnet", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
            y_shift += max_height

    def _add_equipment_icons_secondary_faces(self, frame:np.ndarray):
        max_height = int((self.face_bbox_transformed[3] - self.face_bbox_transformed[1] )/4)+1

        x_shift = 25
        top_right_corner = (self.face_bbox_transformed[2], self.face_bbox_transformed[1])
        y_shift = 0
        if self.obeyed_rules["is_hairnet_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="grey_hairnet", x=top_right_corner[0]+x_shift, y=top_right_corner[1], width=100, height=max_height, maintain_aspect_ratio=True)
            y_shift += max_height

        if self.obeyed_rules["is_safety_google_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="grey_goggles", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
            y_shift += max_height

        if self.obeyed_rules["is_surgical_mask_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="grey_surgical_mask", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
            y_shift +=max_height

        if self.obeyed_rules["is_beardnet_worn"]:
            picasso.draw_image_on_frame(frame=frame, image_name="grey_beardnet", x=top_right_corner[0]+x_shift, y=top_right_corner[1]+y_shift, width=100, height=max_height, maintain_aspect_ratio=True)
            y_shift += max_height

    def __add_approval_disapproval_icons(self, frame:np.ndarray, is_approved:bool, max_width:int, max_height:int) -> np.ndarray:
        icon_name = "approval" if is_approved else "disapproval"
        x_position = self.face_bbox_transformed[0] - max_width//2
        y_position = self.face_bbox_transformed[1] - max_height//2
        picasso.draw_image_on_frame(frame=frame, image_name=icon_name, x=x_position, y=y_position, width=max_width, height=max_height, maintain_aspect_ratio=True)


class FaceTrackerManager:
    def __init__(self, face_update_overlap_threshold:float = 0.5, equipment_update_overlap_threshold:float = 0.5):
        self.FACE_UPDATE_OVERLAP_THRESHOLD = face_update_overlap_threshold #minimum overlap between face bboxes to be considered the same face
        self.EQUIPMENT_UPDATE_OVERLAP_THRESHOLD = equipment_update_overlap_threshold
        self.face_objects = []

    def get_number_of_active_faces(self) -> int:
        return len(self.face_objects)
    
    def __calculate_overlap(self, bbox1:List[Tuple[int,int,int,int]], bbox2:List[Tuple[int,int,int,int]]) -> float: 
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
    
    def update_face_equipments_detection_confidences_and_obeyed_rules(self, equipment_predictions: List[Tuple[str, float, Tuple[int, int, int, int]]]):
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

    def draw_faces_on_frame(self, frame:np.ndarray, coordinate_transform_coefficients=[1,1]) -> np.ndarray:
        
        main_face = None
        max_area = 0
        for face in self.face_objects:
            face_area = face.get_bbox_area()
            if face_area > max_area:
                max_area = face_area
                main_face = face           

        for face in self.face_objects:
            if face == main_face:
                face.draw_face(frame=frame, is_main_face = True, coordinate_transform_coefficients=coordinate_transform_coefficients)
            else:                
                face.draw_face(frame=frame, is_main_face = False, coordinate_transform_coefficients=coordinate_transform_coefficients)
    
        #picasso.draw_image_on_frame(frame=frame, image_name="information", x=50, y=50, width=100, height=100, maintain_aspect_ratio=True)
        
    def should_turn_on_turnstiles(self) -> bool:
        should_turn_on = False
        max_face_area = 0

        for face in self.face_objects:
            face_area = face.get_bbox_area()
            if face_area > max_face_area:
                max_area = face_area
                should_turn_on = face.is_allowed_to_pass()

        return should_turn_on           

                        

  
