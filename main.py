import streamlit as st 
from influx_loader import QueryInfluxData, INFLUXDB_BUCKET_RT
from pdf_creator import pdf_race_recap_creator, create_pdf
import os
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import pytz


varMapping = pd.read_csv('InfluxDB_variables.csv')

st.title("Race recap creator :")

st.write("This app is easy to use : you have four buttons to timestamp the race moments : race start, top gate 1, bottom gate, top gate 2 and finish")
st.write("After timestamping all the marks a pdf will be created (can take few minutes) then a button 'download pdf' will appeared click on it and there you have it !")
#st.session_state['timestamp1'] = datetime.strptime('2024-07-31 14:55:00', '%Y-%m-%d %H:%M:%S')
#st.session_state['timestamp2'] = datetime.strptime('2024-07-31 14:59:20', '%Y-%m-%d %H:%M:%S')
#st.session_state['timestamp3'] =  datetime.strptime('2024-07-31 15:03:42', '%Y-%m-%d %H:%M:%S')
#st.session_state['timestamp4'] =  datetime.strptime('2024-07-31 15:08:00', '%Y-%m-%d %H:%M:%S')
#st.session_state['timestamp5'] =  datetime.strptime('2024-07-31 15:10:00', '%Y-%m-%d %H:%M:%S')
# Initialize session state for timestamps
for i in range(1, 6):
    if f'timestamp{i}' not in st.session_state:
        st.session_state[f'timestamp{i}'] = None

# Function to update the timestamp
def update_timestamp(index):
    st.session_state[f'timestamp{index}'] = datetime.now()
    st.write(f"Timestamp {index}: {st.session_state[f'timestamp{index}']}")


# Buttons to update timestamps
t = st.text_input("Start time, format 14:30")
if t: 
    try:
        index=1
        timing = datetime.now()
        h_m = [int(coord) for coord in t.split(':')]
        new_datetime = datetime(timing.year, timing.month, timing.day, h_m[0], h_m[1], 0, tzinfo=pytz.utc)
        st.session_state[f'timestamp{index}'] = new_datetime
        st.write(f"Timestamp {index}: {st.session_state[f'timestamp{index}']}")
    except ValueError:
            st.error("Please enter the time in the correct format (HH:MM).")

if st.button('Top gate 1'):
    update_timestamp(2)

if st.button('Bottom gate'):
    update_timestamp(3)

if st.button('Top gate 2'):
    update_timestamp(4)

if st.button('Finish line'):
    update_timestamp(5)


    #st.session_state['timestamp1'] = datetime.strptime('2024-07-31 14:55:00', '%Y-%m-%d %H:%M:%S')
    #st.session_state['timestamp2'] = datetime.strptime('2024-07-31 14:59:20', '%Y-%m-%d %H:%M:%S')
    #st.session_state['timestamp3'] =  datetime.strptime('2024-07-31 15:03:42', '%Y-%m-%d %H:%M:%S')
    #st.session_state['timestamp4'] =  datetime.strptime('2024-07-31 15:08:00', '%Y-%m-%d %H:%M:%S')
    #st.session_state['timestamp5'] =  datetime.strptime('2024-07-31 15:10:00', '%Y-%m-%d %H:%M:%S')
    

    
    if st.session_state['timestamp1'] and st.session_state['timestamp2'] and st.session_state['timestamp3'] and st.session_state['timestamp4'] and st.session_state['timestamp5']:
            
            st.session_state['timestamp1'] = (st.session_state['timestamp1'] - timedelta(hours=2)).replace(tzinfo=None)
            #st.session_state['timestamp2'] = (st.session_state['timestamp2'] - timedelta(hours=2)).replace(tzinfo=None)
            #st.session_state['timestamp3'] = (st.session_state['timestamp3'] - timedelta(hours=2)).replace(tzinfo=None)
            #st.session_state['timestamp4'] = (st.session_state['timestamp4'] - timedelta(hours=2)).replace(tzinfo=None)
            #st.session_state['timestamp5'] = (st.session_state['timestamp5'] - timedelta(hours=2)).replace(tzinfo=None)
            marks = pd.DataFrame(columns=['time'])
    

            marks.loc[0, 'time'] = st.session_state['timestamp2']
            marks.loc[1, 'time'] = st.session_state['timestamp3']
            marks.loc[2, 'time'] = st.session_state['timestamp4']
            
            st.write(marks)
            date: str = st.session_state['timestamp1'].strftime('%Y-%m-%d')
            fromTime_: str = (st.session_state['timestamp1'] - timedelta(seconds=100)).replace(tzinfo=None).strftime('%H:%M:%S')
            toTime_: str = st.session_state['timestamp5'].strftime('%H:%M:%S')
            whereTags_ = {"boat": "AC40"}
            # Convert timestamps to string format required by InfluxDB
            start_time = st.session_state['timestamp1'].isoformat() + "Z"
            end_time = st.session_state['timestamp5'].isoformat() + "Z"
            
            data = QueryInfluxData(INFLUXDB_BUCKET_RT, varMapping,
                                       fromTime=datetime.strptime(
                                           f"{date} {fromTime_}", "%Y-%m-%d %H:%M:%S"),
                                       toTime=datetime.strptime(
                                           f"{date} {toTime_}", "%Y-%m-%d %H:%M:%S"),
                                       freq="1s", whereTags=whereTags_)
            st.write(len(race))
            race = data[data.Datetime>=st.session_state['timestamp1']]
            pre_start = data[data.Datetime<=st.session_state['timestamp1']]
            #
            # file_path = pdf_race_recap_creator(race,pre_start, marks,'race stats')

            title = f"{start_time}_race_recap_pdf"
            pdf_buffer = BytesIO()
            pdf_race_recap_creator(race, pre_start, marks, pdf_buffer)
            pdf_buffer.seek(0)

            # Offer PDF for download
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"{title}.pdf",
                mime="application/pdf"
            )





