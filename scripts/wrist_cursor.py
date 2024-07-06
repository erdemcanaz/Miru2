from typing import List, Dict, Tuple #for python3.8 compatibility
import numpy as np
import time
import picasso

class WristCursor:

    def __init__(self):
        self.PARAM_WRIST_UP_FACTOR = 0.08 # cursor should be above the wrist by this factor for better UX
        self.CURSOR_SMOOTHING_FACTOR = 0.4 # smoothing factor for cursor movement

        self.WRIST_DETECTION_THRESHOLD = 0.70 # if the confidence of the wrist detection is below this value, it will be ignored
        self.DETECTION_TIMEOUT_S = 2 # if the wrist is not detected for this amount of time in seconds, the cursor will be hidden
        self.WIDTH_NORMALIZED_CURSOR_SIZE = 0.03 # width of the cursor in the normalized coordinates were base is frame width
        self.NORMALIZED_OPAQUE_CURSOR_REGION = [0.8, 0, 1, 0.5]

        self.HOLDING_THRESHOLDS = {
            "how_to_use": 1.5,
            "pass_me": 5
        }

        self.PARAM_BUTTON_REGIONS = {
            "how_to_use": [0.775, 0.025, 0.975, 0.225],
            "pass_me": [0.775, 0.250, 0.975, 0.450]
        }

        self.MODES = (
            "both_unclicked", #0
            "how_to_use_holding", #1
            "how_to_use_activated", #2
            "pass_me_holding", #3
            "pass_me_activated" #4
            )
        self.mode = self.MODES[0]

        self.last_time_wrist_updated = [0,0] # wrist-1, wrist-2 last update time
        self.normalized_wrist_coordinates = [[0,0],[0,0]] # wrist-1, wrist-2
        self.normalized_cursor_coordinates = [[0,0], [0,0]] # cursor-1, cursor-2

        self.pass_me_started_holding_time = 0
        self.how_to_use_started_holding_time = 0


    def is_inside_normalized_region(self, region:List[Tuple[float,float,float,float]], point:List[Tuple[float,float]]):
        return region[0] < point[0] < region[2] and region[1] < point[1] < region[3]
    
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

    def draw_buttons_on_frame(self, frame:np.ndarray=None):
        #TODO: get the current mode of the cursor and operate accordingly

        # HOW TO USE BUTTON =======================
        how_to_use_x1 = int(self.PARAM_BUTTON_REGIONS["how_to_use"][0]*frame.shape[1])
        how_to_use_y1 = int(self.PARAM_BUTTON_REGIONS["how_to_use"][1]*frame.shape[0])
        how_to_use_x2 = int(self.PARAM_BUTTON_REGIONS["how_to_use"][2]*frame.shape[1])
        how_to_use_y2 = int(self.PARAM_BUTTON_REGIONS["how_to_use"][3]*frame.shape[0])
        how_to_use_width = how_to_use_x2 - how_to_use_x1
        how_to_use_height = how_to_use_y2 - how_to_use_y1

        if self.mode in ["how_to_use_holding", "how_to_use_activated"]:
            picasso.draw_image_on_frame(frame=frame, image_name="nasil_kullanirim_clicked", x=how_to_use_x1, y=how_to_use_y1, width=how_to_use_width, height=how_to_use_height, maintain_aspect_ratio = False)
        else:
            picasso.draw_image_on_frame(frame=frame, image_name="nasil_kullanirim_unclicked", x=how_to_use_x1, y=how_to_use_y1, width=how_to_use_width, height=how_to_use_height, maintain_aspect_ratio = False)
        
        # PASS ME BUTTON =======================
        pass_me_x1 = int(self.PARAM_BUTTON_REGIONS["pass_me"][0]*frame.shape[1])
        pass_me_y1 = int(self.PARAM_BUTTON_REGIONS["pass_me"][1]*frame.shape[0])
        pass_me_x2 = int(self.PARAM_BUTTON_REGIONS["pass_me"][2]*frame.shape[1])
        pass_me_y2 = int(self.PARAM_BUTTON_REGIONS["pass_me"][3]*frame.shape[0])
        pass_me_width = pass_me_x2 - pass_me_x1
        pass_me_height = pass_me_y2 - pass_me_y1     

        if self.mode in ["pass_me_holding", "pass_me_activated"]:
            picasso.draw_image_on_frame(frame=frame, image_name="beni_gecir_clicked", x=pass_me_x1, y=pass_me_y1, width=pass_me_width, height=pass_me_height, maintain_aspect_ratio = False)
        else:
            picasso.draw_image_on_frame(frame=frame, image_name="beni_gecir_unclicked", x=pass_me_x1, y=pass_me_y1, width=pass_me_width, height=pass_me_height, maintain_aspect_ratio = False)

    def update_wrist_cursor_mode(self):

        is_cursor_1_active = True if (time.time()-self.last_time_wrist_updated[0]) < self.DETECTION_TIMEOUT_S else False
        is_cursor_2_active = True if (time.time()-self.last_time_wrist_updated[1]) < self.DETECTION_TIMEOUT_S else False

        # first check how_to_use is clicked or not, then pass_me

        is_on_how_to_use = is_cursor_1_active and self.is_inside_normalized_region(self.PARAM_BUTTON_REGIONS["how_to_use"], self.normalized_cursor_coordinates[0])
        is_on_how_to_use = is_on_how_to_use or (is_cursor_2_active and self.is_inside_normalized_region(self.PARAM_BUTTON_REGIONS["how_to_use"], self.normalized_cursor_coordinates[1]))

        is_on_pass_me = is_cursor_1_active and self.is_inside_normalized_region(self.PARAM_BUTTON_REGIONS["pass_me"], self.normalized_cursor_coordinates[0])
        is_on_pass_me = is_on_pass_me or (is_cursor_2_active and self.is_inside_normalized_region(self.PARAM_BUTTON_REGIONS["pass_me"], self.normalized_cursor_coordinates[1]))

        if is_on_how_to_use:
            if self.mode not in  ["how_to_use_holding","how_to_use_activated"]:
                self.how_to_use_started_holding_time = time.time()
                self.mode = "how_to_use_holding"
            elif time.time() - self.how_to_use_started_holding_time > self.HOLDING_THRESHOLDS["how_to_use"]:
                self.mode = "how_to_use_activated"

        elif is_on_pass_me:
            if self.mode not in ["pass_me_holding","pass_me_activated"]:
                self.pass_me_started_holding_time = time.time()
                self.mode = "pass_me_holding"
            elif time.time() - self.pass_me_started_holding_time > self.HOLDING_THRESHOLDS["pass_me"]:
                self.mode = "pass_me_activated"
        else:
            self.mode = "both_unclicked"

    def get_mode(self):
        return self.mode