import streamlit as st 
from influx_loader import QueryInfluxData, INFLUXDB_BUCKET_RT
from pdf_creator import pdf_race_recap_creator, create_pdf
import os
from datetime import datetime
import pandas as pd
from io import BytesIO

varMapping = pd.read_csv('InfluxDB_variables.csv')

st.title("Race recap creator :")

st.write("This app is easy to use : you have four buttons to timestamp the race moments : race start, top gate 1, bottom gate, top gate 2 and finish")
st.write("After timestamping all the marks a pdf will be created (can take few minutes) then a button 'download pdf' will appeared click on it and there you have it !")

# Timestamp buttons
if 'timestamp1' not in st.session_state:
    st.session_state['timestamp1'] = None
if 'timestamp2' not in st.session_state:
    st.session_state['timestamp2'] = None

if 'timestamp3' not in st.session_state:
    st.session_state['timestamp3'] = None

if 'timestamp4' not in st.session_state:
    st.session_state['timestamp4'] = None

if 'timestamp5' not in st.session_state:
    st.session_state['timestamp5'] = None

if st.button('Start time'):
    st.session_state['timestamp1'] = datetime.now()
    st.write(f"Timestamp 1: {st.session_state['timestamp1']}")

if st.button('Top gate 1'):
    st.session_state['timestamp2'] = datetime.now()
    st.write(f"Timestamp 2: {st.session_state['timestamp2']}")

if st.button('Bottom gate'):
    st.session_state['timestamp3'] = datetime.now()
    st.write(f"Timestamp 3: {st.session_state['timestamp3']}")

if st.button('Top gate 2'):
    st.session_state['timestamp4'] = datetime.now()
    st.write(f"Timestamp 4: {st.session_state['timestamp4']}")

if st.button('Finish line'):
    st.session_state['timestamp5'] = datetime.now()
    st.write(f"Timestamp 5: {st.session_state['timestamp5']}")

    st.session_state['timestamp1'] = datetime.strptime('2024-07-19 09:40:00', '%Y-%m-%d %H:%M:%S')
    st.session_state['timestamp2'] = datetime.strptime('2024-07-19 09:45:09', '%Y-%m-%d %H:%M:%S')
    st.session_state['timestamp3'] =  datetime.strptime('2024-07-19 09:47:56', '%Y-%m-%d %H:%M:%S')
    st.session_state['timestamp4'] =  datetime.strptime('2024-07-19 09:52:42', '%Y-%m-%d %H:%M:%S')
    st.session_state['timestamp5'] =  datetime.strptime('2024-07-19 09:56:37', '%Y-%m-%d %H:%M:%S')
    marks = pd.DataFrame(columns=['time'])
    

    marks.loc[0, 'time'] = st.session_state['timestamp2']
    marks.loc[1, 'time'] = st.session_state['timestamp3']
    marks.loc[2, 'time'] = st.session_state['timestamp4']

    
    if st.session_state['timestamp1'] and st.session_state['timestamp2'] and st.session_state['timestamp3'] and st.session_state['timestamp4'] and st.session_state['timestamp5']:
            date: str = st.session_state['timestamp1'].strftime('%Y-%m-%d')
            fromTime_: str = st.session_state['timestamp1'].strftime('%H:%M:%S')
            toTime_: str = st.session_state['timestamp5'].strftime('%H:%M:%S')
            whereTags_ = {"boat": "AC40"}
            # Convert timestamps to string format required by InfluxDB
            start_time = st.session_state['timestamp1'].isoformat() + "Z"
            end_time = st.session_state['timestamp2'].isoformat() + "Z"
            race = QueryInfluxData(INFLUXDB_BUCKET_RT, varMapping,
                                       fromTime=datetime.strptime(
                                           f"{date} {fromTime_}", "%Y-%m-%d %H:%M:%S"),
                                       toTime=datetime.strptime(
                                           f"{date} {toTime_}", "%Y-%m-%d %H:%M:%S"),
                                       freq="1s", whereTags=whereTags_)
            # st.write(len(race))
            file_path = pdf_race_recap_creator(race, marks,'race2 stats')

            title = "test_pdf"
            pdf_buffer = BytesIO()
            pdf_race_recap_creator(race, marks, pdf_buffer)
            pdf_buffer.seek(0)

            # Offer PDF for download
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"{title}.pdf",
                mime="application/pdf"
            )





