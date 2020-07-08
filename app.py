#This code will run a webapp using streamlit to analyse and visually show New York Motor Vehicle collisions

#importing all required modules for this project
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Crashes.csv")

#Assign headings for the webapp
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit Dashboard that can be used to "
"to analyze motor vehicles in NYC  🗽 💥 🚗 ")

#Loading the collision data and saving it into the cache so that data does not need to be redownloaded
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace =True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

#This block of code uses a slider option to show the various locations where collisions took place with a certain number of persons injured
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")
# hour = st.selectbox("Hour to look at", range(0,24), 1)
hour = st.slider("Hour to look at", 0,23)
# hour = st.sidebar.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" %(hour, (hour+1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

#This function draws the map that shows a 3d representation of motor vehicle collisions
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
    "latitude": midpoint[0],
    "longitude": midpoint[1],
    "zoom": 11,
    "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0,1000],
        ),
    ]
))

#This next block of code looks at accidents that took place between a certain hour period and displays this data through means of a pi chart and histogram
st.subheader("Breakdown by minute between %i:00 and%i:00" % (hour, (hour + 1) %24))
filtered = data[
        (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour<(hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y ='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of peope', ['Pedestrians', 'Cyclists', 'Motorists'])

#This block of code uses a selectbox to show the 5 most dangerous areas in new york affected by type of commute.
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending =False).dropna(how='any')[0:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending =False).dropna(how='any')[0:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending =False).dropna(how='any')[0:5])

#Allows user the functionality to show/hide the raw data being used to draw the histogram or pi chart
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
