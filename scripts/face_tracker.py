import numpy as np
import copy, time
import cv2

class HumanFaceFrame:

    def __init__(self, bbox_coordinates:list[tuple[int, int], tuple[int, int]], extracted_face_frame:np.ndarray=None):
        self.bbox_coordinates = bbox_coordinates
        self.bbox_area = abs((bbox_coordinates[1][0] - bbox_coordinates[0][0]) * (bbox_coordinates[1][1] - bbox_coordinates[0][1]))
        self.obeyed_rules_dict = self.check_obeys_to_which_rules()

    def get_bbox_area(self) -> int:
        return self.bbox_area
    
    def get_bbox_coordinates(self) -> list[tuple[int, int], tuple[int, int]]:
        return self.bbox_coordinates
    

    def check_obeys_to_which_rules(self) -> dict[str, bool]:

        #TODO: A yolov8 model should be trained to detect the following objects: hairnet, safety google, face mask and beard

        dict_of_rules = {
            "is_hairnet_worn": False,
            "is_safety_google_worn": True,
            "is_face_mask_worn": False,
            "is_beard_present": False,
        }
        return dict_of_rules
    
    def is_allowed_to_pass(self) -> bool:
        if not (self.obeyed_rules_dict["is_hairnet_worn"] and self.obeyed_rules_dict["is_safety_google_worn"]):
            return False
        
        elif not self.obeyed_rules_dict["is_face_mask_worn"] and self.obeyed_rules_dict["is_beard_present"]:
            return False
        
        elif not self.obeyed_rules_dict["is_face_mask_worn"] and not self.obeyed_rules_dict["is_beard_present"]:
            return True
         
        return True
    
    def __draw_face_detection_rectangle_on(self, is_draw_scan_line:bool=False, frame:np.ndarray=None, stroke_color:tuple[int,int,int]=(0,0,0), stripe_stroke:int=1, bold_stroke:int=5) -> np.ndarray:
    
        #draw bounding edges
        cv2.rectangle(frame, self.bbox_coordinates[0],  self.bbox_coordinates[1], stroke_color, stripe_stroke)

        #draw bold corners
        width =  self.bbox_coordinates[1][0] -  self.bbox_coordinates[0][0]
        height =  self.bbox_coordinates[1][1] -  self.bbox_coordinates[0][1]

        topleft_corner =  self.bbox_coordinates[0]
        topleft_1 = (topleft_corner[0]+width//3, topleft_corner[1])
        topleft_2 = (topleft_corner[0], topleft_corner[1]+height//3)                
        cv2.line(frame, topleft_corner, topleft_1, stroke_color, bold_stroke)
        cv2.line(frame, topleft_corner, topleft_2, stroke_color, bold_stroke)

        topright_corner = ( self.bbox_coordinates[1][0],  self.bbox_coordinates[0][1])
        topright_1 = (topright_corner[0]-width//3, topright_corner[1])
        topright_2 = (topright_corner[0], topright_corner[1]+height//3)
        cv2.line(frame, topright_corner, topright_1, stroke_color, bold_stroke)
        cv2.line(frame, topright_corner, topright_2, stroke_color, bold_stroke)

        bottomleft_corner = ( self.bbox_coordinates[0][0],  self.bbox_coordinates[1][1])
        bottomleft_1 = (bottomleft_corner[0]+width//3, bottomleft_corner[1])
        bottomleft_2 = (bottomleft_corner[0], bottomleft_corner[1]-height//3)
        cv2.line(frame, bottomleft_corner, bottomleft_1, stroke_color, bold_stroke)
        cv2.line(frame, bottomleft_corner, bottomleft_2, stroke_color, bold_stroke)

        bottomright_corner =  self.bbox_coordinates[1]
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

            line_top = ( self.bbox_coordinates[0][0]+del_width,  self.bbox_coordinates[0][1])
            line_bottom = ( self.bbox_coordinates[0][0]+del_width,  self.bbox_coordinates[1][1])
            cv2.line(frame, line_top, line_bottom, stroke_color, stripe_stroke)
            
        return frame
    
    def __add_rule_texts_on(self, frame:np.ndarray, positive_text_color:tuple[int,int,int]=(0,0,0), negative_text_color:tuple[int,int,int]=(0,0,0), text_thickness:int=1, text_size:float=0.5) -> np.ndarray:
        key_mapping ={
            "is_hairnet_worn": "Hairnet",
            "is_safety_google_worn": "Safety Google",
            "is_face_mask_worn": "Face Mask",
            "is_beard_present": "Beard",
        }

        (text_width, text_height), _ = cv2.getTextSize("x", cv2.FONT_HERSHEY_SIMPLEX, text_size, text_thickness)
        if self.is_allowed_to_pass():
            cv2.putText(frame, "ALLOWED TO PASS", (self.bbox_coordinates[0][0], self.bbox_coordinates[0][1]-text_height), cv2.FONT_HERSHEY_SIMPLEX, text_size, positive_text_color, text_thickness)
        else:
            cv2.putText(frame, "NOT ALLOWED TO PASS", (self.bbox_coordinates[0][0], self.bbox_coordinates[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, text_size, negative_text_color, text_thickness)

        for index, (rule_name_key, rule_value) in enumerate(self.obeyed_rules_dict.items()):
            if rule_value:
                rule_text = "(+) "+key_mapping[rule_name_key]
                text_color = positive_text_color
            else:
                rule_text = "(-) "+key_mapping[rule_name_key]
                text_color = negative_text_color

            (text_width, text_height), _ = cv2.getTextSize(rule_text, cv2.FONT_HERSHEY_SIMPLEX, text_size, text_thickness)
            x_position = self.bbox_coordinates[1][0] + 10  # 10 pixels to the right of the bbox top-right corner
            y_position = self.bbox_coordinates[0][1] + index * (text_height + 10)  # 10 pixels padding and line spacing

            cv2.putText(frame, rule_text, (x_position, y_position), cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, text_thickness)
   
    def draw_face(self, positive_text_color:tuple[int,int,int]=(0,255,0),negative_text_color:tuple[int,int,int]=(0,0,255),text_size:float = 0.5, text_thickness:int = 2, frame:np.ndarray=None, is_draw_scan_line:bool = True,  stroke_color: tuple[int,int,int] = (0,255,0), stripe_stroke:int=1, bold_stroke:int=5):
        self.__draw_face_detection_rectangle_on(is_draw_scan_line=is_draw_scan_line, frame=frame, stroke_color=stroke_color, stripe_stroke=stripe_stroke, bold_stroke=bold_stroke)   
        self.__add_rule_texts_on(frame=frame, positive_text_color=positive_text_color, negative_text_color=negative_text_color, text_size=text_size, text_thickness =text_thickness)

class HumanFaceTracker:

    def __init__(self):
        self.tracked_faces = []

    def update_detected_faces(self, frame:np.ndarray = None, detected_face_bbox_coords:list[list[tuple[int,int], tuple[int,int]]] = None) -> None:
        self.tracked_faces = []
        for bbox_coords in detected_face_bbox_coords:
            face_frame = copy.deepcopy(frame[bbox_coords[0][1]:bbox_coords[1][1], bbox_coords[0][0]:bbox_coords[1][0]])
            self.tracked_faces.append(HumanFaceFrame(bbox_coordinates=bbox_coords, extracted_face_frame=face_frame))

        #sort the faces in descending order of bbox area (highest area first)
        self.tracked_faces =  sorted(self.tracked_faces, key=lambda x: x.get_bbox_area(), reverse=True)

    def draw_faces_on_frame(self, frame:np.ndarray) -> np.ndarray:
        for face_index, face_object in enumerate(self.tracked_faces):
            if face_index == 0: #main face that determines whether turnstiles should open or not
                face_object.draw_face(positive_text_color = (154,14,15), negative_text_color = (0,0,135), text_size = 1, text_thickness = 2, frame=frame, is_draw_scan_line=True,  stroke_color = (154,14,15), stripe_stroke=2, bold_stroke=5)
            else: #other faces that are detected but has no effect on turnstiles
                face_object.draw_face(positive_text_color = (75,75,75), negative_text_color = (75,75,75), text_size = 0.5, text_thickness = 1, frame=frame, is_draw_scan_line=False, stroke_color = (75,75,75), stripe_stroke=1, bold_stroke=5)
        return frame
    
    def get_number_of_detected_faces(self) -> int:
        return len(self.tracked_faces)
    
    def should_turn_on_turnstiles(self) -> bool:
        if len(self.tracked_faces) == 0:
            return False
        else:
            return self.tracked_faces[0].is_allowed_to_pass()
        


    

    
    
