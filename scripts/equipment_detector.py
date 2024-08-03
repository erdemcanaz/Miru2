from ultralytics import YOLO
import copy 
from typing import List, Dict, Tuple #for python3.8 compatibility

class EquipmentDetector():

    EQUIPMENT_MODEL_PATHS = {
        "miru_model_03_08_2024": "trained_yolo_models/miru_model_03_08_2024.pt",
    }
    def __init__(self, model_name : str = None) -> None:
        self.MODEL_PATH = EquipmentDetector.EQUIPMENT_MODEL_PATHS[model_name]
        self.yolo_object = YOLO(self.MODEL_PATH)
        self.recent_prediction_results = []
    
    def __get_empty_prediction_dict_template(self) -> dict:
        empty_prediction_dict = {   
                    "DETECTOR_TYPE":"Equipment Detector",                             # which detector made this prediction
                    "frame_shape": [0,0],                                       # [0,0], [height , width] in pixels
                    "class_name":"",                                            # hard_hat, no_hard_hat
                    "bbox_confidence":0,                                        # 0.0 to 1.0
                    "bbox_xyxy_px":[0,0,0,0],                                   # [x1,y1,x2,y2] in pixels
                    "bbox_center_px": [0,0],                                    # [x,y] in pixels
        }
        return empty_prediction_dict
    
    def predict_frame(self, frame, bbox_confidence = 0.5) -> None:
        self.recent_prediction_results = []
        
        results = self.yolo_object(frame, task = "detect", verbose= False)[0]
        for i, result in enumerate(results):
            boxes = result.boxes
            box_cls_no = int(boxes.cls.cpu().numpy()[0])
            box_cls_name = self.yolo_object.names[box_cls_no]           
            box_conf = boxes.conf.cpu().numpy()[0]
            if box_conf < bbox_confidence:
                continue
            box_xyxy = boxes.xyxy.cpu().numpy()[0]

            prediction_dict_template = self.__get_empty_prediction_dict_template()
            prediction_dict_template["frame_shape"] = list(results.orig_shape)
            prediction_dict_template["class_name"] = box_cls_name
            prediction_dict_template["bbox_confidence"] = box_conf
            prediction_dict_template["bbox_xyxy_px"] = box_xyxy # Bounding box in the format [x1,y1,x2,y2]
            prediction_dict_template["bbox_center_px"] = [ (box_xyxy[0]+box_xyxy[2])/2, (box_xyxy[1]+box_xyxy[3])/2]
            
            self.recent_prediction_results.append(prediction_dict_template)
        
    def return_formatted_predictions_list(self) -> List[Dict]:
        formatted_predictions_list = [] # each element of this list is of the form ["tpye", (x1, y1, x2, y2)]
        for prediction in self.recent_prediction_results:
            formatted_predictions_list.append(copy.deepcopy([prediction["class_name"], prediction["bbox_confidence"], tuple(map(int, prediction["bbox_xyxy_px"]))]))

        return formatted_predictions_list


    
