import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, date

# Function to connect to MySQL database
def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Mahesh@12",
        database="EDI"
    )
    return connection

# Function to fetch vehicle details based on input values
def fetch_vehicle_details(state, district, series_char, series_num):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = f"SELECT * FROM VEHICLE_DETAILS WHERE state='{state}' AND district={district} AND series_char='{series_char}' AND series_num='{series_num}'"
    cursor.execute(query)
    result = cursor.fetchall()

    connection.close()

    return result

# Function to check if a date is expired
def is_expired(date_string):
    if date_string:
        if isinstance(date_string, date):
            date_string = date_string.strftime("%Y-%m-%d")
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj < datetime.now()
    return False

# Streamlit UI
def main():
    st.title("Vehicle Details Lookup")
    
    # Input fields
    state = st.text_input("Enter State (2 characters)")
    district = st.number_input("Enter District (2 digits)", min_value=0, max_value=99, step=1)
    series_char = st.text_input("Enter Series Character (2 characters)")
    series_num = st.text_input("Enter Series Number (4 characters)")

    # Button to fetch details
    if st.button("Fetch Details"):
        if len(state) == 2 and 0 <= district <= 99 and len(series_char) == 2 and len(series_num) == 4:
            vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
            if vehicle_details:
                st.write("Vehicle Details:")
                df = pd.DataFrame(vehicle_details, columns=["State", "District", "Series Character", "Series Number", "Owner Name", "Owner Mobile No", "Insurance Valid From", "Insurance Valid To", "PUC Valid From", "PUC Valid To"])
                
                # Check if insurance or PUC is expired
                current_date = datetime.now().strftime("%Y-%m-%d")
                df['Insurance Expired'] = df['Insurance Valid To'].apply(is_expired)
                df['PUC Expired'] = df['PUC Valid To'].apply(is_expired)
                
                st.dataframe(df)
            else:
                st.write("No details found for the provided input.")
        else:
            st.error("Input values do not meet the requirements. Please check the input limits.")

if __name__ == "__main__":
    main()