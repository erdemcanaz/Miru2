from typing import List, Dict, Tuple #for python3.8 compatibility
import pprint

class Face:
    def __init__(self, age_limit:int = 5, sample_size:int = 10, face_bbox:List[Tuple[int,int,int,int]] = None):
        self.AGE_LIMIT = age_limit
        self.SAMPLE_SIZE = sample_size
        self.age:int = 0 #number of iterations since the face was last detected
        self.face_bbox:list = face_bbox #coordinates of the face bounding box in the format (x1,y1,x2,y2)

        self.linked_detections = {
            "hair_net":[0]*self.SAMPLE_SIZE,
            "beard_net":[0]*self.SAMPLE_SIZE,
            "safety_goggles":[0]*self.SAMPLE_SIZE,
            "blue_surgical_mask":[0]*self.SAMPLE_SIZE,
            "white_surgical_mask":[0]*self.SAMPLE_SIZE
        } #detection_name: [confidence1, confidence2, ...]                  
        
    def get_face_bbox(self) -> List[Tuple[int,int,int,int]]:
        return self.face_bbox
    
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
            self.linked_detections[detection_class].pop(0)        
            self.linked_detections[detection_class].append(confidence)        

        pprint.pprint(self.linked_detections)

    def get_meaned_detection_confidence(self, detection_name:str) -> float:
        if detection_name not in self.linked_detections:
            raise ValueError(f"No detection named {detection_name} found")
               
        return sum(self.linked_detections[detection_name]) / len(self.linked_detections[detection_name]) 
    
    def increase_age(self):
        self.age += 1

    def should_be_deleted(self) -> bool:
        return self.age > self.AGE_LIMIT
    

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
    
    def update_face_equipments(self, equipment_predictions: List[Tuple[str, float, Tuple[int, int, int, int]]]):
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
                        print(f"Updating {equipment_prediction[0]} confidence for face bbox {face.get_face_bbox()}, {face.transform_class_name(equipment_class, equipment_bbox)}")
                        transformed_class_name = face.transform_class_name(equipment_class, equipment_bbox)
                        detected_equipments[transformed_class_name] = max(equipment_prediction[1], detected_equipments[transformed_class_name])

                face.append_detection_confidences(detected_equipments)


                

                        

  
