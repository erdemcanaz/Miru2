from typing import List, Dict, Tuple #for python3.8 compatibility
import numpy as np
import time
import picasso

class WristCursor:

    def __init__(self):
        self.PARAM_WRIST_UP_FACTOR = 0.08 # cursor should be above the wrist by this factor for better UX
        self.CURSOR_SMOOTHING_FACTOR = 0.4 # smoothing factor for cursor movement

        self.WRIST_DETECTION_THRESHOLD = 0.70 # if the confidence of the wrist detection is below this value, it will be ignored
        self.DETECTION_TIMEOUT_S = 0.75 # if the wrist is not detected for this amount of time in seconds, the cursor will be hidden
        self.WIDTH_NORMALIZED_CURSOR_SIZE = 0.03 # width of the cursor in the normalized coordinates were base is frame width
        self.NORMALIZED_OPAQUE_CURSOR_REGION = [0.8, 0, 1, 0.5]

        self.last_time_wrist_updated = [0,0] # wrist-1, wrist-2 last update time
        self.normalized_wrist_coordinates = [[0,0],[0,0]] # wrist-1, wrist-2
        self.normalized_cursor_coordinates = [[0,0], [0,0]] # cursor-1, cursor-2

    def update_wrist_cursor_position(self, main_face_pose_detection_id:str="", pose_pred_dicts:List[Dict]=None, predicted_frame:np.ndarray=None):
        #0.1 up the wrist

        # UPDATE WRIST POSITIONS AND LAST DETECTION TIMES
        for pose_pred_dict in pose_pred_dicts:
            if pose_pred_dict["detection_id"] == main_face_pose_detection_id:


                if pose_pred_dict["keypoints"]["left_wrist"][2] > self.WRIST_DETECTION_THRESHOLD: 
                    left_wrist_resized = pose_pred_dict["keypoints"]["left_wrist"]

                    new_left_wrist_x = left_wrist_resized[0] / predicted_frame.shape[1]
                    new_left_wrist_y = left_wrist_resized[1] / predicted_frame.shape[0]

                    self.normalized_wrist_coordinates[0][0] = self.CURSOR_SMOOTHING_FACTOR * new_left_wrist_x + (1 - self.CURSOR_SMOOTHING_FACTOR) * self.normalized_wrist_coordinates[0][0]
                    self.normalized_wrist_coordinates[0][1] = self.CURSOR_SMOOTHING_FACTOR * new_left_wrist_y + (1 - self.CURSOR_SMOOTHING_FACTOR) * self.normalized_wrist_coordinates[0][1]

                    self.normalized_cursor_coordinates[0] = self.normalized_wrist_coordinates[0]
                    self.normalized_cursor_coordinates[0][1] = max(0,self.normalized_cursor_coordinates[0][1] - self.PARAM_WRIST_UP_FACTOR)

                    self.last_time_wrist_updated[0] = time.time()

                if pose_pred_dict["keypoints"]["right_wrist"][2] >  self.WRIST_DETECTION_THRESHOLD:               
                    right_wrist_resized = pose_pred_dict["keypoints"]["right_wrist"]

                    new_right_wrist_x = right_wrist_resized[0] / predicted_frame.shape[1]
                    new_right_wrist_y = right_wrist_resized[1] / predicted_frame.shape[0]

                    self.normalized_wrist_coordinates[1][0] = self.CURSOR_SMOOTHING_FACTOR * new_right_wrist_x + (1 - self.CURSOR_SMOOTHING_FACTOR) * self.normalized_wrist_coordinates[1][0]
                    self.normalized_wrist_coordinates[1][1] = self.CURSOR_SMOOTHING_FACTOR * new_right_wrist_y + (1 - self.CURSOR_SMOOTHING_FACTOR) * self.normalized_wrist_coordinates[1][1]

                    self.normalized_cursor_coordinates[1] = self.normalized_wrist_coordinates[1]
                    self.normalized_cursor_coordinates[1][1] = max(0,self.normalized_cursor_coordinates[1][1] - self.PARAM_WRIST_UP_FACTOR)

                    self.last_time_wrist_updated[1] = time.time()

                break

    def draw_wrist_cursor_on_frame(self, frame:np.ndarray=None, draw_cursor_1:bool=True, draw_cursor_2:bool=True, apply_timeout:bool=True):
        for i in range(2):
            if i == 0 and not draw_cursor_1:
                continue
            elif i == 1 and not draw_cursor_2:
                continue
            elif apply_timeout and time.time() - self.last_time_wrist_updated[i] > self.DETECTION_TIMEOUT_S:
                continue

            cursor_image_edge_length = int(frame.shape[1]*self.WIDTH_NORMALIZED_CURSOR_SIZE)

            cursor_center_x = int(self.normalized_cursor_coordinates[i][0]*frame.shape[1])
            cursor_center_y = int(self.normalized_cursor_coordinates[i][1]*frame.shape[0])
            
            cursor_topleft_x = max(0,int(cursor_center_x - cursor_image_edge_length/2))
            cursor_topleft_y = max(0, int(cursor_center_y - cursor_image_edge_length/2))

            is_x_inside_opaque_region = self.NORMALIZED_OPAQUE_CURSOR_REGION[0] < self.normalized_cursor_coordinates[i][0] < self.NORMALIZED_OPAQUE_CURSOR_REGION[2]
            is_y_inside_opaque_region = self.NORMALIZED_OPAQUE_CURSOR_REGION[1] < self.normalized_cursor_coordinates[i][1] < self.NORMALIZED_OPAQUE_CURSOR_REGION[3]

            if is_x_inside_opaque_region and is_y_inside_opaque_region:
                # Opaque cursor
                picasso.draw_image_on_frame(frame=frame, image_name="wrist_mouse_icon", x=cursor_topleft_x, y=cursor_topleft_y, width=cursor_image_edge_length, height=cursor_image_edge_length, maintain_aspect_ratio = True)
            else:
                picasso.draw_image_on_frame(frame=frame, image_name="wrist_mouse_icon_transparent", x=cursor_topleft_x, y=cursor_topleft_y, width=cursor_image_edge_length, height=cursor_image_edge_length, maintain_aspect_ratio = True)
