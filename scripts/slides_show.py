import os, time
import cv2
import numpy as np
import copy

class SlideShow():

    def __init__(self, slides_folder:str = None, slide_duration_s:float = 5):
        #SLIDES RELATED
        self.last_time_slide_changed = 0
        self.current_slide_index = 0

        self.opacity = 0.0

        self.SLIDE_DURATION_S = slide_duration_s
        self.SLIDE_IMAGES = []
        for filename in os.listdir(slides_folder):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                slide_path = os.path.join(slides_folder, filename)
                slide_image = cv2.imread(slide_path)
                self.SLIDE_IMAGES.append(slide_image)

        if len(self.SLIDE_IMAGES) == 0:
            raise Exception("No slide images found in the given folder")
    
    def should_change_slide(self) -> bool:
        time_elapsed = time.time() - self.last_time_slide_changed
        if time_elapsed >= self.SLIDE_DURATION_S:
            return True
    
    def update_current_slide(self):
        self.current_slide_index = (self.current_slide_index + 1) % len(self.SLIDE_IMAGES)
        self.last_time_slide_changed = time.time()

    def get_slide_images(self, width:int, height:int) -> list[np.ndarray]:
        return_slide_frame = cv2.resize(copy.deepcopy(self.SLIDE_IMAGES[self.current_slide_index]), (width, height))
        return return_slide_frame
    
    def increase_opacity(self):
        self.opacity = min(1.0, self.opacity + 0.03)

    def decrease_opacity(self):        
        self.opacity = max(0.0, self.opacity - 0.05)

    def draw_slide_on_top_of_frame(self, frame:np.ndarray, slide_frame:np.ndarray):
        return_frame = copy.deepcopy(frame)
        cv2.addWeighted(slide_frame, self.opacity, return_frame, 1 - self.opacity, 0, return_frame)
        return return_frame
    

    


