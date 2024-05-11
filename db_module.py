import mysql.connector
import pandas as pd
from datetime import datetime, date
# Function to connect to MySQL database
def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Mahesh@12",  # Change this to your MySQL password
        database="EDI"  # Change this to your database name
    )
    return connection

def fetch_vehicle_details(state, district, series_char, series_num):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = f"SELECT * FROM VEHICLE_DETAILS WHERE state='{state}' AND district={district} AND series_char='{series_char}' AND series_num='{series_num}'"
    cursor.execute(query)
    result = cursor.fetchall()

    # Convert result to DataFrame
    df = pd.DataFrame(result, columns=["state", "district", "series_char", "series_num", "owner_name", "owner_mob_no", "ins_valid_from", "ins_valid_to", "puc_valid_from", "puc_valid_to"])

    connection.close()

    return df

def fetch_email(state, district, series_char, series_num):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = f"SELECT owner_email FROM VEHICLE_DETAILS WHERE state='{state}' AND district={district} AND series_char='{series_char}' AND series_num='{series_num}'"
    cursor.execute(query)
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        return None

# Function to check if a date is expired
def is_expired(date_string):
    if date_string:
        if isinstance(date_string, date):
            date_string = date_string.strftime("%Y-%m-%d")
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj < datetime.now()
    return False
