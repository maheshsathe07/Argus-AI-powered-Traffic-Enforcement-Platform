import cv2
import time
import string
import easyocr
import os
import numpy as np
import tempfile
import shutil
from ultralytics import YOLO
from sort.sort import Sort
from datetime import datetime

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'A': '4', 'G': '6', 'S': '5'}
dict_int_to_char = {'0': 'O', '1': 'I', '3': 'J', '4': 'A', '6': 'G', '5': 'S'}

def get_mapped_state(code):
    if code.startswith('Y'):
        return 'MH'
    return state_mappings.get(code, 'Unknown')

# Example dictionary with existing mappings
state_mappings = {
    'HH': 'MH',  # Maharashtra
    'LL': 'DL',  # Delhi
    'OO': 'OD',  # Odisha
    'II': 'UP',  # Uttar Pradesh
    'GG': 'GJ',  # Gujarat
    'YI': 'MH',
    'YH': 'MH',
    'Y|': 'MH',
    'NH': 'MH',
    # Other mappings as necessary
}

def replace_state_code(text):
    if len(text) >= 2:
        state_code = text[:2]
        mapped_state = get_mapped_state(state_code)
        if mapped_state != 'Unknown':
            text = mapped_state + text[2:]
    return text

# Function to write CSV results
def write_csv(results, output_path):
    with open(output_path, 'w') as f:
        f.write('frame_nmr,car_id,car_bbox,license_plate_bbox,license_plate_bbox_score,license_number,license_number_score\n')
        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                if 'car' in results[frame_nmr][car_id] and 'license_plate' in results[frame_nmr][car_id] and 'text' in results[frame_nmr][car_id]['license_plate']:
                    f.write(f"{frame_nmr},{car_id},"
                            f"[{results[frame_nmr][car_id]['car']['bbox'][0]} {results[frame_nmr][car_id]['car']['bbox'][1]} {results[frame_nmr][car_id]['car']['bbox'][2]} {results[frame_nmr][car_id]['car']['bbox'][3]}],"
                            f"[{results[frame_nmr][car_id]['license_plate']['bbox'][0]} {results[frame_nmr][car_id]['license_plate']['bbox'][1]} {results[frame_nmr][car_id]['license_plate']['bbox'][2]} {results[frame_nmr][car_id]['license_plate']['bbox'][3]}],"
                            f"{results[frame_nmr][car_id]['license_plate']['bbox_score']},"
                            f"{results[frame_nmr][car_id]['license_plate']['text']},"
                            f"{results[frame_nmr][car_id]['license_plate']['text_score']}\n")

# Function to check if the license plate format complies
def license_complies_format(text):
    if len(text) != 10:
        return False
    checks = [
        (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char),
        (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char),
        (text[2] in '0123456789' or text[2] in dict_char_to_int),
        (text[3] in '0123456789' or text[3] in dict_char_to_int),
        (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char),
        (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char),
        (text[6] in '0123456789' or text[6] in dict_char_to_int),
        (text[7] in '0123456789' or text[7] in dict_char_to_int),
        (text[8] in '0123456789' or text[8] in dict_char_to_int),
        (text[9] in '0123456789' or text[9] in dict_char_to_int)
    ]
    return all(checks)

# Function to format the license plate
def format_license(text):
    mapping = {0: dict_int_to_char, 1: dict_int_to_char, 4: dict_int_to_char, 5: dict_int_to_char,
               2: dict_char_to_int, 3: dict_char_to_int, 6: dict_char_to_int, 7: dict_char_to_int, 8: dict_char_to_int,
               9: dict_char_to_int}
    return ''.join(mapping[j].get(text[j], text[j]) for j in range(10))

def read_license_plate(license_plate_crop):
    detections = reader.readtext(license_plate_crop)
    for detection in detections:
        bbox, text, score = detection
        text = ''.join(ch for ch in text if ch.isalnum()).upper()

        # Check and replace state code if needed
        if len(text) >= 2:
            state_code = text[:2]
            if state_code in state_mappings:
                text = state_mappings[state_code] + text[2:]
                text = replace_state_code(text) 

        if license_complies_format(text):
            return format_license(text), score
    return None, None

def get_car(license_plate, vehicle_track_ids):
    x1, y1, x2, y2, score, class_id = license_plate
    for j, (xcar1, ycar1, xcar2, ycar2, car_id) in enumerate(vehicle_track_ids):
        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            return vehicle_track_ids[j]
    return -1, -1, -1, -1, -1

# Function to process the video
def process_video(video_path):
    vehicles = [2, 3, 5, 7]
    results = {}
    mot_tracker = Sort()

    temp_dir = tempfile.mkdtemp()
    temp_video_path = os.path.join(temp_dir, "temp_video.mp4")
    shutil.copy(video_path, temp_video_path)

    cap = cv2.VideoCapture(temp_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for the output video
    out = cv2.VideoWriter('output_video.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    coco_model = YOLO('models/yolov8n.pt')
    licence_plate_detector = YOLO('models/LicencePlateModel.pt')

    frame_nmr = -1
    while True:
        frame_nmr += 1
        # if frame_nmr > 30:  # Limiting to 30 frames for demonstration purposes
        #     break
        ret, frame = cap.read()
        if not ret:
            break

        results[frame_nmr] = {}

        detections = coco_model(frame)[0]
        detections_ = [[x1, y1, x2, y2, score] for x1, y1, x2, y2, score, class_id in detections.boxes.data.tolist() if int(class_id) in vehicles]

        # Check if detections are not empty before updating tracker
        if len(detections_) > 0:
            track_ids = mot_tracker.update(np.asarray(detections_))
        else:
            track_ids = np.empty((0, 5))

        license_plates = licence_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
            if car_id != -1:
                license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2)]
                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

                license_plate_text, license_plate_score = read_license_plate(license_plate_crop_thresh)
                if license_plate_text:
                    results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, xcar2]},
                                                  'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                    'text': license_plate_text,
                                                                    'bbox_score': score,
                                                                    'text_score': license_plate_score}}
                    # Draw bounding box for the car
                    cv2.rectangle(frame, (int(xcar1), int(ycar1)), (int(xcar2), int(ycar2)), (255, 0, 0), 2)
                    # Draw bounding box for the license plate
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    # Put the license plate text on the frame
                    cv2.putText(frame, license_plate_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        out.write(frame)

    cap.release()
    out.release()

    csv_path = os.path.join(temp_dir, 'test.csv')
    write_csv(results, csv_path)
    return csv_path, 'output_video.mp4'

def record_video(output_path, duration):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
    
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
    cap.release()
    out.release()


# Functions for API
def parse_date(date_str):
    for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return datetime(1970, 1, 1).date()
def get_vehicle_info(registration_number):
    url = "https://rto-vehicle-information-verification-india.p.rapidapi.com/api/v1/rc/vehicleinfo"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "YOUR API KEY",
        "X-RapidAPI-Host": "YOUR RAPIDAPI HOST"
    }
    payload = {
        "reg_no": registration_number,
        "consent": "Y",
        "consent_text": "I hereby declare my consent agreement for fetching my information via AITAN Labs API"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        vehicle_info = response.json()['result']
        return vehicle_info
    else:
        return None

