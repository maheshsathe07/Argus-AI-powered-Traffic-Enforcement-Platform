**AI-powered Traffic Enforcement Platform**

**Project Description:**

The Traffic Police Assistant is an AI-powered system designed to assist traffic police in monitoring and managing traffic. This system utilizes computer vision and deep learning techniques to detect vehicles, identify license plates, and extract license plate numbers from surveillance videos. The extracted data is then stored in a CSV file for further analysis and record-keeping.

**Key Features:**

1. **Vehicle Detection using YOLOv8 Pretrained Model:**
   - The system employs the YOLOv8 pretrained model to detect vehicles in surveillance videos.
   - YOLOv8 (You Only Look Once) is a state-of-the-art object detection model known for its accuracy and efficiency.

2. **License Plate Detection using Custom Trained YOLOv8 Model:**
   - A custom trained YOLOv8 model is used to detect license plates on detected vehicles.
   - This model is trained specifically for license plate detection to ensure high accuracy and robustness.

3. **License Plate Number Extraction using EasyOCR:**
   - EasyOCR, a powerful optical character recognition (OCR) library, is utilized to extract license plate numbers from detected license plates.
   - EasyOCR supports various languages and provides accurate text extraction even in challenging conditions.

4. **Data Storage and Management:**
   - The extracted license plate numbers along with relevant information are stored in a CSV file.
   - This CSV file serves as a database for maintaining records of detected vehicles and their license plate numbers.

5. **Missing Data Interpolation:**
   - The system implements interpolation techniques to fill in missing data in the surveillance video.
   - Interpolation helps in creating a continuous dataset by estimating values for frames where data is missing.

6. **Bounding Box Visualization:**
   - Bounding boxes are overlaid on detected vehicles and license plates for visual representation.
   - License plate numbers are displayed within bounding boxes for easy identification and analysis.

**Usage:**

1. Provide the input video containing traffic surveillance footage.
2. The system will process the video, detect vehicles, identify license plates, extract license plate numbers, and store the data in a CSV file.
3. Missing data will be interpolated to ensure a continuous dataset.
4. The output video with bounding boxes and extracted license plate numbers will be generated for visualization and analysis.

**Requirements:**

- Python 3.8+
- OpenCV
- NumPy
- Pandas
- YOLOv8 Pretrained Model
- Custom Trained YOLOv8 Model for License Plate Detection
- EasyOCR Library
- Ultralytics Library
- Streamlit

**Installation:**

1. Clone the project repository from GitHub.
2. Install the required dependencies using pip or conda.
3. Download and place the pretrained YOLOv8 model and custom trained YOLOv8 model in the appropriate directories.
4. Install the EasyOCR library using pip.
5. Ensure that all necessary files and directories are properly configured.

**Credits:**

- YOLOv8: https://github.com/WongKinYiu/yolov5
- EasyOCR: https://github.com/JaidedAI/EasyOCR

**License:**

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

**Contributors:**

Mahesh Sathe  
Piyush Waghulde  
Atharva Shinde  
Bhushan Sangle  
Om Wagh
