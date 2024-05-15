import os
import xml.etree.ElementTree as ET

def convert_voc_to_yolo(voc_label_folder, yolo_label_folder, image_folder, class_names_file):
    # Read the class names
    with open(class_names_file, 'r') as f:
        class_names = f.read().strip().split('\n')
    
    # Create the YOLO label folder if it doesn't exist
    os.makedirs(yolo_label_folder, exist_ok=True)

    # Iterate over all XML files in the Pascal/VOC label folder
    for voc_file in os.listdir(voc_label_folder):
        if not voc_file.endswith('.xml'):
            continue

        # Parse the XML file
        voc_path = os.path.join(voc_label_folder, voc_file)
        tree = ET.parse(voc_path)
        root = tree.getroot()

        # Get image dimensions
        size = root.find('size')
        img_width = int(size.find('width').text)
        img_height = int(size.find('height').text)

        # Prepare the YOLO label
        yolo_label = []

        # Iterate over each object in the XML
        for obj in root.findall('object'):
            class_name = obj.find('name').text
            if class_name not in class_names:
                continue
            class_id = class_names.index(class_name)

            bndbox = obj.find('bndbox')
            xmin = int(bndbox.find('xmin').text)
            ymin = int(bndbox.find('ymin').text)
            xmax = int(bndbox.find('xmax').text)
            ymax = int(bndbox.find('ymax').text)

            # Convert to YOLO format
            x_center = (xmin + xmax) / 2.0 / img_width
            y_center = (ymin + ymax) / 2.0 / img_height
            width = (xmax - xmin) / float(img_width)
            height = (ymax - ymin) / float(img_height)

            yolo_label.append(f"{class_id} {x_center} {y_center} {width} {height}")

        # Save the YOLO label
        yolo_file = os.path.join(yolo_label_folder, voc_file.replace('.xml', '.txt'))
        with open(yolo_file, 'w') as f:
            f.write('\n'.join(yolo_label))

        # Delete the old Pascal/VOC label
        os.remove(voc_path)

# Usage example
voc_label_folder = "data/labels"
yolo_label_folder = "local_labels"
image_folder = 'data/images'  # Needed for image dimensions
class_names_file = 'data/predefined_classes.txt'  # File containing class names, one per line

convert_voc_to_yolo(voc_label_folder, yolo_label_folder, image_folder, class_names_file)
