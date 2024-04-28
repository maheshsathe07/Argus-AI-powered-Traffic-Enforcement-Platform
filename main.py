# import cv2
# import numpy as np
# from ultralytics import YOLO
# from ultralytics import models
# from sort.sort import *
# from util import get_car, read_license_plate, write_csv
# import matplotlib.pyplot as plt
# from PIL import Image
#
# mot_tracker = Sort()
#
# results = {}
#
# # load models
# coco_model = YOLO('models/yolov8n.pt')
# licence_plate_detector = YOLO('models/LicencePlateModel.pt')
#
# # load video
# cap = cv2.VideoCapture("video1.mp4")
#
# vehicles = [2,3,5,7]
#
# # read frames
# frame_nmr = -1
# ret = True
# while ret:
#     frame_nmr+=1
#     ret, frame = cap.read()
#     print(frame.shape)
#     # plt.imshow(frame)
#     # plt.show()
#     if ret:
#         # if frame_nmr > 1000:
#         #     break
#         results[frame_nmr] = {}
#         # Resize frame to match the required input size (1, 3, 224, 128)
#         # resized_frame = cv2.resize(frame, (224, 224))
#         # new_width = int(224 * (frame.shape[1] / frame.shape[0]))
#         # resized_frame = cv2.resize(frame, (new_width, 128))
#         # plt.imshow(resized_frame)
#         # plt.show()
#
#         # detect vehicle
#         detections = coco_model(frame)[0]
#         detections_ = []
#         for detection in detections.boxes.data.tolist():
#             x1, y1, x2, y2, score, class_id = detection
#             if int(class_id) in vehicles:
#                 # print(int(class_id))
#                 detections_.append([x1, y1, x2, y2, score])
#                 # print(detections_)
#                 # print(detections)
#
#         # track vehicles
#         track_ids = mot_tracker.update(np.asarray(detections_))
#         # print(track_ids)
#
#         # detect license plates
#         license_plates = licence_plate_detector(frame)[0]
#         # print(license_plates)
#         # plt.imshow(license_plates)
#         # plt.show()
#         for license_plate in license_plates.boxes.data.tolist():
#             x1, y1, x2, y2, score, class_id = license_plate
#
#             # assign license plate to a vehicle
#             xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
#
#             if car_id!=-1:
#
#                 # crop license plate
#                 license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
#                 # plt.imshow(license_plate_crop)
#                 # plt.show()
#                 # process license plate
#                 license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
#                 # plt.imshow(license_plate_crop_gray)
#                 # plt.show()
#                 _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
#                 # plt.imshow(license_plate_crop_thresh)
#                 # plt.show()
#
#                 # read license plate
#                 license_plate_text, license_plate_score = read_license_plate(license_plate_crop_thresh)
#
#                 if license_plate_text is not None:
#                     # Scale back bounding box coordinates to original frame size
#                     x1_orig, y1_orig, x2_orig, y2_orig = int(x1 * frame.shape[1] / 128), int(y1 * frame.shape[0] / 224), int(x2 * frame.shape[1] / 128), int(y2 * frame.shape[0] / 224)
#                     results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
#                                                   'license_plate': {'bbox': [x1_orig, y1_orig, x2_orig, y2_orig],
#                                                                     'text': license_plate_text,
#                                                                     'bbox_score': score,
#                                                                     'text_score': license_plate_score}}
#                     # print(results)
#
#
# # write results
# write_csv(results, 'temp/test.csv')
#


import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics import models
from sort.sort import *
from util import get_car, read_license_plate, write_csv
import matplotlib.pyplot as plt
from PIL import Image

mot_tracker = Sort()

results = {}

# load models
coco_model = YOLO('models/yolov8n.pt')
licence_plate_detector = YOLO('models/LicencePlateModel.pt')

# load video
cap = cv2.VideoCapture("video1.mp4")

vehicles = [2, 3, 5, 7]

# read frames
frame_nmr = -1
while True:
    frame_nmr += 1
    ret, frame = cap.read()
    if not ret:
        break  # Exit the loop if reading frame fails

    print(frame.shape)
    # plt.imshow(frame)
    # plt.show()

    # if frame_nmr > 1000:
    #     break

    results[frame_nmr] = {}

    # Resize frame to match the required input size (1, 3, 224, 128)
    # resized_frame = cv2.resize(frame, (224, 224))
    # new_width = int(224 * (frame.shape[1] / frame.shape[0]))
    # resized_frame = cv2.resize(frame, (new_width, 128))
    # plt.imshow(resized_frame)
    # plt.show()

    # detect vehicle
    detections = coco_model(frame)[0]
    detections_ = []
    for detection in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = detection
        if int(class_id) in vehicles:
            detections_.append([x1, y1, x2, y2, score])

    # track vehicles
    track_ids = mot_tracker.update(np.asarray(detections_))

    # detect license plates
    license_plates = licence_plate_detector(frame)[0]
    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate

        # assign license plate to a vehicle
        xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

        if car_id != -1:

            # crop license plate
            license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

            # process license plate
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

            # read license plate
            license_plate_text, license_plate_score = read_license_plate(license_plate_crop_thresh)

            if license_plate_text is not None:
                # Scale back bounding box coordinates to original frame size
                x1_orig, y1_orig, x2_orig, y2_orig = int(x1 * frame.shape[1] / 128), int(y1 * frame.shape[0] / 224), int(x2 * frame.shape[1] / 128), int(y2 * frame.shape[0] / 224)
                results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                              'license_plate': {'bbox': [x1_orig, y1_orig, x2_orig, y2_orig],
                                                                'text': license_plate_text,
                                                                'bbox_score': score,
                                                                'text_score': license_plate_score}}

# write results
write_csv(results, 'temp/test.csv')
