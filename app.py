import streamlit as st
import pandas as pd
from twilio.rest import Client
from datetime import datetime
import tempfile
import cv2
import time
from utils import *
from db_module import fetch_vehicle_details
import matplotlib.pyplot as plt
from PIL import Image
import base64

def main():
    st.title("AI Powered Traffic Enforcement Platform")

    mode = st.selectbox("Select Mode", ["Upload Video", "Real-Time Video"])

    if mode == "Upload Video":
        uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
        if uploaded_file is not None:
            with st.spinner('Processing video...'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                    temp_file.write(uploaded_file.read())
                    temp_file_path = temp_file.name
                results_csv, _ = process_video(temp_file_path)
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
                    results_csv, _ = process_video(temp_video.name)
                st.success("License plate details extracted successfully!")
                st.write("Download the results CSV file:")
                st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
                                   file_name="license_plate_results.csv", mime="text/csv")
                display_vehicle_details(results_csv)


def display_vehicle_details(results_csv):
    st.write("Vehicle Details:")
    df = pd.read_csv(results_csv)
    vehicle_details_list = []
    for car_id, group in df.groupby('car_id'):
        max_score_row = group.loc[group['license_number_score'].idxmax()]
        license_plate_number = max_score_row['license_number']
        state = license_plate_number[:2]
        district = int(license_plate_number[2:4])
        series_char = license_plate_number[4:6]
        series_num = license_plate_number[6:]
        vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
        if not vehicle_details.empty:
            today = datetime.now().date()
            for index, row in vehicle_details.iterrows():
                has_fine = False
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
                vehicle_details_list.append({
                    'License Plate Number': license_plate_number,
                    'Owner Name': row['owner_name'],
                    'Owner Mobile Number': row['owner_mob_no'],
                    'Insurance Expiry': row['ins_valid_to'],
                    'PUC Expiry': row['puc_valid_to'],
                    'Fine Applied': has_fine
                })
        else:
            st.write(f"No details found for the license plate number: {license_plate_number}")

    vehicle_details_df = pd.DataFrame(vehicle_details_list)
    st.write(vehicle_details_df)

if __name__ == "__main__":
    main()
