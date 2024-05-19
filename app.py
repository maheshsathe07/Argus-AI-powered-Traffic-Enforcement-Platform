# import streamlit as st
# from twilio.rest import Client
# from utils import *
# from db_module import *

# # Streamlit UI
# def main():
#     st.title("License Plate Detection App")
#     uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
#     if uploaded_file is not None:
#         with st.spinner('Processing video...'):
#             results_csv = process_video(uploaded_file)
#         st.success("License plate details extracted successfully!")
#         st.write("Download the results CSV file:")
#         st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
#                            file_name="license_plate_results.csv", mime="text/csv")
#         # Display the fetched vehicle details
#         st.write("Vehicle Details:")
#         df = pd.read_csv(results_csv)
#         for car_id, group in df.groupby('car_id'):
#             max_score_row = group.loc[group['license_number_score'].idxmax()]
#             license_plate_number = max_score_row['license_number']
#             st.write(f"License Plate Number: {license_plate_number}")
#             # Extract state, district, series_char, and series_num from the license plate number
#             state = license_plate_number[:2]
#             district = int(license_plate_number[2:4])
#             series_char = license_plate_number[4:6]
#             series_num = license_plate_number[6:]
#             # Fetch vehicle details from the database
#             vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
#             if not vehicle_details.empty:
#                 # Check insurance and PUC expiration dates for each row
#                 today = datetime.now().date()
#                 has_fine = False
#                 for index, row in vehicle_details.iterrows():
#                     ins_expired = row['ins_valid_to'] < today
#                     puc_expired = row['puc_valid_to'] < today
#                     if ins_expired or puc_expired:
#                         has_fine = True
#                         # Send SMS message about the fine

#                         # Twilio Code to send SMS
#                         account_sid = 'Account_SID'
#                         auth_token = 'Auth_Token'
#                         client = Client(account_sid, auth_token)
#                         to_number_with_country_code = "+91" + str(row['owner_mob_no'])
#                         message = client.messages.create(
#                             from_='Generated_No.',
#                             body='Fine For Not Having Active Insurance or PUC',
#                             to=to_number_with_country_code
#                         )
                        
#                         break  # Once a fine is found, no need to check further
#                 if has_fine:
#                     st.write("Fine For Not Having Active Insurance or PUC")
#                 else:
#                     st.write("No fine detected for this vehicle.")
#             else:
#                 st.write("No details found for the provided license plate number.")


# if __name__ == "__main__":
#     main()



import streamlit as st
import pandas as pd
from twilio.rest import Client
from datetime import datetime
import tempfile
import cv2
import time
from utils import process_video
from db_module import fetch_vehicle_details

def main():
    st.title("AI Powered Traffic Enforcement Platform")

    mode = st.selectbox("Select Mode", ["Upload Video", "Real-Time Video"])

    if mode == "Upload Video":
        uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
        if uploaded_file is not None:
            with st.spinner('Processing video...'):
                results_csv = process_video(uploaded_file)
            st.success("License plate details extracted successfully!")
            st.write("Download the results CSV file:")
            st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
                               file_name="license_plate_results.csv", mime="text/csv")
            display_vehicle_details(results_csv)
    elif mode == "Real-Time Video":
        if st.button('Start Recording'):
            st.warning("Recording will stop automatically after 20 seconds.")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                record_video(temp_video.name, 20)
                with st.spinner('Processing video...'):
                    results_csv = process_video(open(temp_video.name, "rb"))
                st.success("License plate details extracted successfully!")
                st.write("Download the results CSV file:")
                st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
                                   file_name="license_plate_results.csv", mime="text/csv")
                display_vehicle_details(results_csv)

def display_vehicle_details(results_csv):
    st.write("Vehicle Details:")
    df = pd.read_csv(results_csv)
    for car_id, group in df.groupby('car_id'):
        max_score_row = group.loc[group['license_number_score'].idxmax()]
        license_plate_number = max_score_row['license_number']
        st.write(f"License Plate Number: {license_plate_number}")
        state = license_plate_number[:2]
        district = int(license_plate_number[2:4])
        series_char = license_plate_number[4:6]
        series_num = license_plate_number[6:]
        vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
        if not vehicle_details.empty:
            today = datetime.now().date()
            has_fine = False
            for index, row in vehicle_details.iterrows():
                ins_expired = row['ins_valid_to'] < today
                puc_expired = row['puc_valid_to'] < today
                if ins_expired or puc_expired:
                    has_fine = True
                    account_sid = 'Your Twilio Account SID'
                    auth_token = 'Your Twilio Authentication Token'
                    client = Client(account_sid, auth_token)
                    to_number_with_country_code = "+91" + str(row['owner_mob_no'])
                    message = client.messages.create(
                        from_='Your Twilio No.',
                        body='Fine For Not Having Active Insurance or PUC',
                        to=to_number_with_country_code
                    )
                    break
            if has_fine:
                st.write("Fine For Not Having Active Insurance or PUC")
            else:
                st.write("No fine detected for this vehicle.")
        else:
            st.write("No details found for the provided license plate number.")

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

if __name__ == "__main__":
    main()

