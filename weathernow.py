import requests
import pandas as pd
import streamlit as st
from math import radians ,cos, sin, asin, sqrt
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from datetime import datetime
def havesine(lat1,lon1,lat2,lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1
    return(6371*2*asin(sqrt(sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2)))
loc_button = Button(label="Get Location",width=0,background ="#000000")
loc_button.js_on_event("button_click", CustomJS(code="""
    navigator.geolocation.getCurrentPosition(
        (loc) => {
            document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))})"""))
result = streamlit_bokeh_events(
    loc_button,
    events="GET_LOCATION",
    key="get_location",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)
lat,lon = 0,0
lats,lons = [],[]
op2 = ['central','north','east','south','west']
if result:
    if "GET_LOCATION" in result:
        lat = result.get("GET_LOCATION")['lat']
        lon = result.get("GET_LOCATION")['lon']
        map_data = pd.DataFrame({'lat':[lat],'lon':[lon]})      
if lat != 0 and lon != 0:
    times = ['2 hour weather forecast','24 hour weather forecast','4 day weather forecast']
    chooseforecast = st.selectbox("Choose a forecast",times)
    weather = requests.get("https://api.data.gov.sg/v1/environment/"+chooseforecast.replace(' ','-'))
    if chooseforecast == times[0]:
        dist = pd.DataFrame.from_dict(weather.json()['area_metadata'])
        for i in range(dist.shape[0]):
            dist.loc[i,'label_location'] = havesine(lat,lon,dist.loc[i,'label_location']['latitude'],dist.loc[i,'label_location']['longitude'])
        dist = dist.sort_values('label_location')
        weatherdf = pd.DataFrame.from_dict(weather.json()['items'][0]['forecasts'])
        curarea = st.selectbox("Select your location",dist['name'])
        weatherdf = weatherdf.set_index("area")
        st.write("The weather now is: " + str(weatherdf.loc[curarea,'forecast']))
    elif chooseforecast == times[1]:
        times = ['Morning','Afternoon','Night']
        optime = st.selectbox("Choose a time to look at",times)
        for i in range(len(op2)):
            st.write("The weather now in the "+op2[i]+' is: '+weather.json()['items'][0]['periods'][times.index(optime)]['regions'][op2[i]]) 
    elif chooseforecast == times[2]:
        for i in range(4):
            st.write(datetime.strftime(datetime.strptime(weather.json()['items'][0]['forecasts'][i]['date'],'%Y-%m-%d'),'%d %B %Y')+': '+weather.json()['items'][0]['forecasts'][i]['forecast'])
