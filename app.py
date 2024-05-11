import streamlit as st
from twilio.rest import Client
from utils import *
from db_module import *

# Streamlit UI
def main():
    st.title("License Plate Detection App")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
    if uploaded_file is not None:
        with st.spinner('Processing video...'):
            results_csv = process_video(uploaded_file)
        st.success("License plate details extracted successfully!")
        st.write("Download the results CSV file:")
        st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
                           file_name="license_plate_results.csv", mime="text/csv")
        # Display the fetched vehicle details
        st.write("Vehicle Details:")
        df = pd.read_csv(results_csv)
        for car_id, group in df.groupby('car_id'):
            max_score_row = group.loc[group['license_number_score'].idxmax()]
            license_plate_number = max_score_row['license_number']
            st.write(f"License Plate Number: {license_plate_number}")
            # Extract state, district, series_char, and series_num from the license plate number
            state = license_plate_number[:2]
            district = int(license_plate_number[2:4])
            series_char = license_plate_number[4:6]
            series_num = license_plate_number[6:]
            # Fetch vehicle details from the database
            vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
            if not vehicle_details.empty:
                # Check insurance and PUC expiration dates for each row
                today = datetime.now().date()
                has_fine = False
                for index, row in vehicle_details.iterrows():
                    ins_expired = row['ins_valid_to'] < today
                    puc_expired = row['puc_valid_to'] < today
                    if ins_expired or puc_expired:
                        has_fine = True
                        # Send SMS message about the fine

                        # Twilio Code to send SMS
                        
                        break  # Once a fine is found, no need to check further
                if has_fine:
                    st.write("Fine For Not Having Active Insurance or PUC")
                else:
                    st.write("No fine detected for this vehicle.")
            else:
                st.write("No details found for the provided license plate number.")


if __name__ == "__main__":
    main()
