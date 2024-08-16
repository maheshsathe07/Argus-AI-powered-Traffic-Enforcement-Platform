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
                    account_sid = 'Account SID'
                    auth_token = 'Auth Token'
                    client = Client(account_sid, auth_token)
                    # to_number_with_country_code = "+91" + str(row['owner_mob_no'])
            
                    # Craft the message with all the details
                    message_body = (
                        f"Fine Applied for Vehicle:\n"
                        f"License Plate Number: {license_plate_number}\n"
                        f"Owner Name: {row['owner_name']}\n"
                        f"Insurance Expiry: {row['ins_valid_to']}\n"
                        f"PUC Expiry: {row['puc_valid_to']}\n"
                        f"Fine Applied: {'Yes' if has_fine else 'No'}"
                    )

                    message = client.messages.create(
                        from_='Your Twilio Mobile',
                        body=message_body,
                        # to=to_number_with_country_code
                        to="Sender Mob No."
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


# Code fetching vehicles details from API
# import streamlit as st
# import pandas as pd
# from twilio.rest import Client
# from datetime import datetime
# import tempfile
# import cv2
# import time
# from utils import *
# import requests
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def main():
#     st.title("AI Powered Traffic Enforcement Platform")

#     mode = st.selectbox("Select Mode", ["Upload Video", "Real-Time Video"])

#     if mode == "Upload Video":
#         uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
#         if uploaded_file is not None:
#             with st.spinner('Processing video...'):
#                 with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
#                     temp_file.write(uploaded_file.read())
#                     temp_file_path = temp_file.name
#                 results_csv, _ = process_video(temp_file_path)
#             st.success("License plate details extracted successfully!")
#             st.write("Download the results CSV file:")
#             st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
#                                file_name="license_plate_results.csv", mime="text/csv")
#             display_vehicle_details(results_csv)
#     elif mode == "Real-Time Video":
#         if st.button('Start Recording'):
#             st.warning("Recording will stop automatically after 20 seconds.")
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
#                 record_video(temp_video.name, 20)
#                 with st.spinner('Processing video...'):
#                     results_csv, _ = process_video(temp_video.name)
#                 st.success("License plate details extracted successfully!")
#                 st.write("Download the results CSV file:")
#                 st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
#                                    file_name="license_plate_results.csv", mime="text/csv")
#                 display_vehicle_details(results_csv)

# def display_vehicle_details(results_csv):
#     st.write("Vehicle Details:")
#     df = pd.read_csv(results_csv)
#     vehicle_details_list = []
#     for car_id, group in df.groupby('car_id'):
#         max_score_row = group.loc[group['license_number_score'].idxmax()]
#         license_plate_number = max_score_row['license_number']
        
#         # Fetch vehicle details from API
#         vehicle_details = get_vehicle_info(license_plate_number)
        
#         if vehicle_details:
#             today = datetime.now().date()
#             ins_valid_to_str = vehicle_details.get('vehicle_insurance_details', {}).get('insurance_upto', '1970-01-01')
#             puc_valid_to_str = vehicle_details.get('vehicle_pucc_details', {}).get('pucc_upto', '1970-01-01')

#             ins_valid_to = parse_date(ins_valid_to_str)
#             puc_valid_to = parse_date(puc_valid_to_str)
            
#             has_fine = False
#             ins_expired = ins_valid_to < today
#             puc_expired = puc_valid_to < today
            
#             if ins_expired or puc_expired:
#                 has_fine = True
#                 account_sid = 'YOUR TWILIO ACCOUNT SID'
#                 auth_token = 'YOUR TWILIO AUTHENTICATION TOKEN'
#                 client = Client(account_sid, auth_token)
#                 to_number_with_country_code = "RECEIVER'S MOBILE NO."
#                 message_body = (f"Vehicle with license plate {license_plate_number} has expired documents.\n"
#                                 f"Owner Name: {vehicle_details['owner_name']}\n"
#                                 f"Insurance Expired: {ins_expired}\n"
#                                 f"PUC Expired: {puc_expired}\n"
#                                 f"Insurance Valid Until: {ins_valid_to}\n"
#                                 f"PUC Valid Until: {puc_valid_to}")
#                 try:
#                     message = client.messages.create(
#                         from_='TWILIO MOBILE NO.',
#                         body=message_body,
#                         to=to_number_with_country_code
#                     )
#                     logging.info(f"Message sent successfully to {to_number_with_country_code}")
#                 except Exception as e:
#                     logging.error(f"Error sending message: {e}")
                
#             vehicle_details_list.append({
#                 'License Plate Number': license_plate_number,
#                 'Owner Name': vehicle_details['owner_name'],
#                 'Insurance Expiry': ins_valid_to,
#                 'PUC Expiry': puc_valid_to,
#                 'Fine Applied': has_fine
#             })
#         else:
#             st.warning(f"No details found for the license plate number: {license_plate_number}")

#     if vehicle_details_list:
#         vehicle_details_df = pd.DataFrame(vehicle_details_list)
#         st.write(vehicle_details_df)


# if __name__ == "__main__":
#     main()
