from typing import List, Dict, Tuple #for python3.8 compatibility
import numpy as np
import time
import picasso

class WristCursor:

    def __init__(self):
        self.PARAM_WRIST_UP_FACTOR = 0.8 # cursor should be above the wrist by this factor for better UX

        self.WRIST_DETECTION_THRESHOLD = 0.60 # if the confidence of the wrist detection is below this value, it will be ignored
        self.DETECTION_TIMEOUT_S = 0.75 # if the wrist is not detected for this amount of time in seconds, the cursor will be hidden
        self.WIDTH_NORMALIZED_CURSOR_SIZE = 0.03 # width of the cursor in the normalized coordinates were base is frame width
        self.NORMALIZED_OPAQUE_CURSOR_REGION = [0.5,0,1,1]

        self.last_time_wrist_updated = [0,0] # left wrist, right wrist last update time
        self.normalized_wrist_coordinates = [[0,0],[0,0]] # left wrist, right wrist
        self.normalized_cursor_coordinates = [[0,0], [0,0]] # left cursor, right cursor

    def update_wrist_cursor_position(self, main_face_pose_detection_id:str="", pose_pred_dicts:List[Dict]=None, predicted_frame:np.ndarray=None):
        #0.1 up the wrist

        # UPDATE WRIST POSITIONS AND LAST DETECTION TIMES
        for pose_pred_dict in pose_pred_dicts:
            if pose_pred_dict["detection_id"] == main_face_pose_detection_id:

                if pose_pred_dict["keypoints"]["left_wrist"][2] > self.WRIST_DETECTION_THRESHOLD: 
                    left_wrist_resized = pose_pred_dict["keypoints"]["left_wrist"]
                    self.normalized_wrist_coordinates[0] = [left_wrist_resized[0]/predicted_frame.shape[1], left_wrist_resized[1]/predicted_frame.shape[0]]
                    self.last_time_wrist_updated[0] = time.time()
                    self.normalized_cursor_coordinates[0] = self.normalized_wrist_coordinates[0]
                    self.normalized_cursor_coordinates[0][1] = max(0,self.normalized_cursor_coordinates[0][1] - self.PARAM_WRIST_UP_FACTOR)
                if pose_pred_dict["keypoints"]["right_wrist"][2] >  self.WRIST_DETECTION_THRESHOLD:
                    right_wrist_resized = pose_pred_dict["keypoints"]["right_wrist"]
                    self.normalized_wrist_coordinates[1] = [right_wrist_resized[0]/predicted_frame.shape[1], right_wrist_resized[1]/predicted_frame.shape[0]]
                    self.normalized_cursor_coordinates[1] =self.normalized_wrist_coordinates[1]
                    self.normalized_cursor_coordinates[1][1] = max(0,self.normalized_cursor_coordinates[1][1] - self.PARAM_WRIST_UP_FACTOR)                                                            
                    self.last_time_wrist_updated[1] = time.time()

                break


    def draw_wrist_cursor_on_frame(self, frame:np.ndarray=None):
        cursor_image_edge_length = int(frame.shape[1]*self.WIDTH_NORMALIZED_CURSOR_SIZE)

        cursor_center_x = int(self.normalized_cursor_coordinates[0][0]*frame.shape[1])
        cursor_center_y = int(self.normalized_cursor_coordinates[0][1]*frame.shape[0])
        
        cursor_topleft_x = max(0,int(cursor_center_x - cursor_image_edge_length/2))
        cursor_topleft_y = max(0, int(cursor_center_y - cursor_image_edge_length/2))

        if self.normalized_cursor_coordinates[0][0] > self.NORMALIZED_OPAQUE_CURSOR_REGION[0] and self.normalized_cursor_coordinates[0][0] < self.NORMALIZED_OPAQUE_CURSOR_REGION[2] and self.normalized_cursor_coordinates[0][1] > self.NORMALIZED_OPAQUE_CURSOR_REGION[1] and self.normalized_cursor_coordinates[0][1] < self.NORMALIZED_OPAQUE_CURSOR_REGION[3]:
            #opaque cursor
            picasso.draw_image_on_frame(frame=frame, image_name="wrist_mouse_icon", x=cursor_topleft_x, y=cursor_topleft_y, width=cursor_image_edge_length, height=cursor_image_edge_length, maintain_aspect_ratio = True)
        else:  
            #transparent cursor          
            picasso.draw_image_on_frame(frame=frame, image_name="wrist_mouse_icon", x=cursor_topleft_x, y=cursor_topleft_y, width=cursor_image_edge_length, height=cursor_image_edge_length, maintain_aspect_ratio = True)

        pass