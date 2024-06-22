import cv2
import numpy as np

IMAGE_PATHS = {
    "approval": "src/images/icons/approval.png",
    "disapproval": "src/images/icons/disapproval.png",

    "grey_hairnet": "src/images/icons/grey_hairnet.png",
    "green_hairnet": "src/images/icons/green_hairnet.png",
    "red_hairnet": "src/images/icons/red_hairnet.png",
    "blue_hairnet": "src/images/icons/blue_hairnet.png",

    "grey_goggles": "src/images/icons/grey_goggles.png",
    "green_goggles": "src/images/icons/green_goggles.png",
    "red_goggles": "src/images/icons/red_goggles.png",
    "blue_goggles": "src/images/icons/blue_goggles.png",

    "grey_beardnet": "src/images/icons/grey_beardnet.png",
    "green_beardnet": "src/images/icons/green_beardnet.png",
    "red_beardnet": "src/images/icons/red_beardnet.png",
    "blue_beardnet": "src/images/icons/blue_beardnet.png",

    "grey_surgical_mask": "src/images/icons/grey_surgicalmask.png",
    "green_surgical_mask": "src/images/icons/green_surgicalmask.png",
    "red_surgical_mask": "src/images/icons/red_surgicalmask.png",
    "blue_surgical_mask": "src/images/icons/blue_surgicalmask.png",
}


def draw_image_on_frame(frame:np.ndarray=None, image_name:str=None, x:int=None, y:int=None, width:int=100, height:int=100, maintain_aspect_ratio:bool = True):
    global IMAGE_PATHS
    image_path = IMAGE_PATHS[image_name]
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Resize image
    if maintain_aspect_ratio:
        im_height, im_width = image.shape[0], image.shape[1]
        scale = min((width / im_width), (height / im_height))
        image = cv2.resize(image, (int(im_width * scale), int(im_height * scale)), interpolation=cv2.INTER_AREA)
    else:
        image = cv2.resize(image, (width, height),interpolation=cv2.INTER_AREA)


    # Draw image on frame
    frame_height, frame_width = frame.shape[0], frame.shape[1]
    resized_image_height, resized_image_width = image.shape[0], image.shape[1]

    roi_x1 = x
    roi_x2 = min(max(x + resized_image_width, 0), frame_width)
    roi_y1 = y
    roi_y2 = min(max(y + resized_image_height, 0), frame_height)

    if roi_x1<0 or roi_y1<0 or (roi_x2 - roi_x1 <= 0) or (roi_y2 - roi_y1 <= 0):
        return
    
    frame_roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
    image_roi = image[0:(roi_y2-roi_y1), 0:(roi_x2-roi_x1)]
    
    if image.shape[2]==4:                                   # If image has alpha channel           
        b, g, r, a = cv2.split(image_roi)                   # Split the icon into its channels            
        image_alpha = a / 255.0                             # Normalize the alpha channel to be in the range [0, 1]
        
        for c in range(0, 3):                               # Loop over the RGB channels
            frame_roi[:, :, c] = (frame_roi[:, :, c] * (1 - image_alpha) + image_roi[:, :, c] * image_alpha).astype(np.uint8)

    else:
        frame[roi_y1:roi_y2, roi_x1:roi_x2] = image_roi