import numpy as np
import cv2 
import time
from scripts import picasso
from typing import List, Dict, Tuple #for python3.8 compatibility

class Face:

    def __init__(self):
        self.face_bbox: list = []
        self.goggles_bboxes: list = []
        self.net_bboxes: list = []
        self.surgical_mask_bboxes: list = []
        self.obeyed_rules: dict = None

    def set_face_bbox(self, bbox:Tuple[int,int,int,int]) -> None:
        self.face_bbox = bbox

    def get_face_bbox(self) -> list:
        return self.face_bbox

    def get_face_bbox_area(self) -> int:
        return abs((self.face_bbox[2] - self.face_bbox[0]) * (self.face_bbox[3] - self.face_bbox[1]))
    
    def append_net_bboxes(self, bbox:Tuple[int,int,int,int]) -> None:
        self.net_bboxes.append(bbox)
    
    def append_surical_mask_bboxes(self, bbox:Tuple[int,int,int,int]) -> None:
        self.surgical_mask_bboxes.append(bbox)

    def append_goggles_bboxes(self, bbox:Tuple[int,int,int,int]) -> None:
        self.goggles_bboxes.append(bbox)

    def update_obeys_to_which_rules(self) -> Dict[str, bool]:
        self.obeyed_rules = {
            "is_hairnet_worn": False,
            "is_safety_google_worn": False,
            "is_beard_present": False,
            "is_beardnet_worn": False,
            "is_surgical_mask_worn": False,
        }

        #TODO: implement beard detection

        if len(self.goggles_bboxes) > 0:
            self.obeyed_rules["is_safety_google_worn"] = True

        if len(self.surgical_mask_bboxes) > 0:
            self.obeyed_rules["is_surgical_mask_worn"] = True

        center_of_face = (self.face_bbox[0] + self.face_bbox[2])//2, (self.face_bbox[1] + self.face_bbox[3])//2
        for net_bbox in self.net_bboxes:
            center_of_net = (net_bbox[0] + net_bbox[2])//2, (net_bbox[1] + net_bbox[3])//2
            if center_of_face[1] > center_of_net[1]:#net is above face, so it should be hairnet
                self.obeyed_rules["is_hairnet_worn"] = True
            else:
                self.obeyed_rules["is_beardnet_worn"] = True

    def is_allowed_to_pass(self) -> bool:
        if not (self.obeyed_rules["is_hairnet_worn"] and self.obeyed_rules["is_safety_google_worn"]):
            return False
        if self.obeyed_rules["is_beard_present"] and not (self.obeyed_rules["is_beardnet_worn"] or self.obeyed_rules["is_surgical_mask_worn"]):
            return False
            
        return True

    def get_obeyed_rules_dict(self) -> Dict[str, bool]:
        return self.obeyed_rules 
        
    def test_draw_bboxes(self, frame:np.ndarray):
        cv2.rectangle(frame, (self.face_bbox[0],self.face_bbox[1]),  (self.face_bbox[2],self.face_bbox[3]), (0,255,0), 1)
        for net_bbox in self.net_bboxes:
            cv2.rectangle(frame, (net_bbox[0],net_bbox[1]),  (net_bbox[2],net_bbox[3]), (0,0,255), 1)
        for mask_bbox in self.surgical_mask_bboxes:
            cv2.rectangle(frame, (mask_bbox[0],mask_bbox[1]),  (mask_bbox[2],mask_bbox[3]), (0,0,255), 1)
        for goggles_bbox in self.goggles_bboxes:
            cv2.rectangle(frame, (goggles_bbox[0],goggles_bbox[1]),  (goggles_bbox[2],goggles_bbox[3]), (0,0,255), 1)
    
    def draw_face(self, frame:np.ndarray=None, is_main_face:bool = None, stripe_stroke:int=1, bold_stroke:int=5):
        if is_main_face:
            stroke_color = (108,208,142) if self.is_allowed_to_pass() else (82,82,255) #green or red
            self.__draw_face_detection_rectangle_on(is_draw_scan_line=True, frame=frame, stroke_color=stroke_color, stripe_stroke=stripe_stroke, bold_stroke=bold_stroke)   
            self.__add_equipment_icons_main_face(frame=frame)
            self.__add_approval_disapproval_icons(frame=frame, is_approved=self.is_allowed_to_pass(), max_width=75, max_height=75)
        
        else:
            stroke_color = (186,186,186)
            self.__draw_face_detection_rectangle_on(is_draw_scan_line=False, frame=frame, stroke_color=stroke_color, stripe_stroke=stripe_stroke, bold_stroke=bold_stroke)
            self._add_equipment_icons_secondary_faces(frame=frame)
            

        #self.__add_rule_texts_on(frame=frame, positive_text_color=positive_text_color, negative_text_color=negative_text_color, text_size=text_size, text_thickness =text_thickness)

    def __draw_face_detection_rectangle_on(self, is_draw_scan_line:bool=False, frame:np.ndarray=None, stroke_color:Tuple[int,int,int]=(0,0,0), stripe_stroke:int=1, bold_stroke:int=5) -> np.ndarray:
    
        #draw bounding edges
        cv2.rectangle(frame, (self.face_bbox[0],self.face_bbox[1]),  (self.face_bbox[2],self.face_bbox[3]), stroke_color, stripe_stroke)

        #draw bold corners
        bbox_coordinates = [(self.face_bbox[0],self.face_bbox[1] ),(self.face_bbox[2],self.face_bbox[3] )]
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
    
    def __add_rule_texts_on(self, frame:np.ndarray, positive_text_color:Tuple[int,int,int]=(0,0,0), negative_text_color:Tuple[int,int,int]=(0,0,0), text_thickness:int=1, text_size:float=0.5) -> np.ndarray:
        bbox_coordinates = [(self.face_bbox[0],self.face_bbox[1] ),(self.face_bbox[2],self.face_bbox[3] )]

        key_mapping ={
            "is_hairnet_worn": "Hairnet",
            "is_safety_google_worn": "Safety Google",
            "is_beard_present": "Beard",
            "is_beardnet_worn": "Beardnet",
            "is_surgical_mask_worn": "Surgical Mask",
        }

        (text_width, text_height), _ = cv2.getTextSize("x", cv2.FONT_HERSHEY_SIMPLEX, text_size, text_thickness)
        if self.is_allowed_to_pass():
            cv2.putText(frame, "ALLOWED TO PASS", (bbox_coordinates[0][0], bbox_coordinates[0][1]-text_height), cv2.FONT_HERSHEY_SIMPLEX, text_size, positive_text_color, text_thickness)
        else:
            cv2.putText(frame, "NOT ALLOWED TO PASS", (bbox_coordinates[0][0], bbox_coordinates[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, text_size, negative_text_color, text_thickness)

        for index, (rule_name_key, rule_value) in enumerate(self.obeyed_rules.items()):
            if rule_value:
                rule_text = "(+) "+key_mapping[rule_name_key]
                text_color = positive_text_color
            else:
                rule_text = "(-) "+key_mapping[rule_name_key]
                text_color = negative_text_color

            (text_width, text_height), _ = cv2.getTextSize(rule_text, cv2.FONT_HERSHEY_SIMPLEX, text_size, text_thickness)
            x_position = bbox_coordinates[1][0] + 10  # 10 pixels to the right of the bbox top-right corner
            y_position = bbox_coordinates[0][1] + index * (text_height + 10)  # 10 pixels padding and line spacing

            cv2.putText(frame, rule_text, (x_position, y_position), cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, text_thickness)

    def __add_equipment_icons_main_face(self,frame):
                
        max_height = int((self.face_bbox[3] - self.face_bbox[1] )/4)+1

        x_shift = 25
        top_right_corner = (self.face_bbox[2], self.face_bbox[1])
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
        max_height = int((self.face_bbox[3] - self.face_bbox[1] )/4)+1

        x_shift = 25
        top_right_corner = (self.face_bbox[2], self.face_bbox[1])
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
        x_position = self.face_bbox[0] - 20
        y_position = self.face_bbox[1] - 20
        picasso.draw_image_on_frame(frame=frame, image_name=icon_name, x=x_position, y=y_position, width=max_width, height=max_height, maintain_aspect_ratio=True)

class FaceManager:

    def __init__(self) -> None:
        self.current_face_objects = None #list of Face objects
        self.number_of_active_faces = None
            
    def __calculate_intersection(self, bbox1, bbox2)->float: 
        # Returns how much percentage of bbox2 inside bbox1 
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])

        intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)

        bbox2_area = (bbox2[2] - bbox2[0] + 1) * (bbox2[3] - bbox2[1] + 1)

        return intersection_area / bbox2_area
    
    def update_current_faces(self, face_and_equipment_detections:List[Tuple[str,Tuple[int,int,int,int]]], min_overlap: float = 0.3) -> None:
        self.current_face_objects = []       
        self.number_of_active_faces = None

        for detection in face_and_equipment_detections:
            if detection[0] == "face":
                should_create_new_face = True
                for face in self.current_face_objects:
                    overlap = self.__calculate_intersection(face.get_face_bbox(), detection[1])
                    if overlap > min_overlap:
                        should_create_new_face = False

                if should_create_new_face:
                    face_object = Face()
                    face_object.set_face_bbox(detection[1])
                    self.current_face_objects.append(face_object)

        self.number_of_active_faces = len(self.current_face_objects)
        
        #match faces with equipment detections
        for face in self.current_face_objects:
            for face_and_equipment_detection in face_and_equipment_detections:
                equipment_type = face_and_equipment_detection[0]
                equipment_bbox = face_and_equipment_detection[1]

                if equipment_type == "face":
                    continue
                        
                overlap = self.__calculate_intersection(face.get_face_bbox(), face_and_equipment_detection[1])
                
                if overlap > min_overlap:
                    if equipment_type in ["white_net", "blue_net"]:
                        face.append_net_bboxes(equipment_bbox)
                    elif equipment_type in ["white_surgical_mask", "blue_surgical_mask"]:
                        face.append_surical_mask_bboxes(equipment_bbox)
                    elif equipment_type == "safety_goggles":
                        face.append_goggles_bboxes(equipment_bbox)                

            #update obeyed rules
            face.update_obeys_to_which_rules()            

    def get_number_of_active_faces(self) -> int:
        return self.number_of_active_faces
    
    def draw_faces_on_frame(self, frame:np.ndarray) -> np.ndarray:
        
        main_face = None
        max_area = 0
        for face in self.current_face_objects:
            face_area = face.get_face_bbox_area()
            if face_area > max_area:
                max_area = face_area
                main_face = face           

        for face in self.current_face_objects:
            if face == main_face:
                face.draw_face(frame=frame, is_main_face = True)
            else:                
                face.draw_face(frame=frame, is_main_face = False)
    
        picasso.draw_image_on_frame(frame=frame, image_name="information", x=50, y=50, width=100, height=100, maintain_aspect_ratio=True)
        