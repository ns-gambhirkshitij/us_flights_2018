import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

import app_helper as helper

st.set_page_config(
    page_title="US Flights 2018",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

multi_css=f'''
<style>
.stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
.stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"No Selection Made - All Data Is Used";}}
</style>
'''
st.markdown(multi_css, unsafe_allow_html=True)


### Data Load

df, airports = helper.load_data()

airlines = st.sidebar.multiselect('Select Airline(s)', df.airline_name.unique(), 
                          help = '''Select the airline(s) that you would like to view the data from. 
                                    If you do not select any, data from all airlines will be shown'''
                        )

if len(airlines) == 0:
    sub_df = df
else:
    sub_df = df[df.airline_name.isin(airlines)]


origins = st.sidebar.multiselect('Select Origin Airport(s)', sub_df.origin_airport_name.unique())

if len(origins) == 0:
    og = st.sidebar.empty()
    sub_df = sub_df
else:
    sub_df = sub_df[sub_df.origin_airport_name.isin(origins)]

destinations = st.sidebar.multiselect('Select Destination Airport(s)', sub_df.dest_airport_name.unique())

if len(destinations) == 0:
    d = st.sidebar.empty()
    sub_df = sub_df
else:
    sub_df = sub_df[sub_df.dest_airport_name.isin(destinations)]

quarters = st.sidebar.multiselect('Quarter', sub_df.Quarter.unique())

if len(quarters) == 0:
    sub_df = sub_df
else:
    sub_df = sub_df[sub_df.Quarter.isin(quarters)]

st.title('US Flights 2018 ✈️')
st.caption("""
This interactive web-app visualizes the flights in the US in 2018. 
In the sidebar on the left, select the airlines, origin airports and destination airports you would like to see data from, along with which quarter of the year you are interested in.
If no selection is made in a box, all data of that field is used. This can make the program really slow, so please make sure to select only the airlines and airports that your are interested in. And have fun!
""")
st.caption("""The original data is 9M+ rows of domestic flights in the US, but for the sake of app performance, this data has been shortened down to 100.000 rows.""")
st.caption("""Data Source: https://www.kaggle.com/datasets/zernach/2018-airplane-flights""")
st.caption('Made by Kshitij Gambhir, 24927232, UTS')

st.write("---")

if st.sidebar.button('Run Query'):

    #if len(origins) == 0:
        #og.error('Data Load Too High - Please Select A Few Origin Airports')
       # pass
   # elif len(destinations) == 0:
        #d.error('Data Load Too High - Please Select A Few Destination Airports')
        #pass
    #else:
        

    m = st.container()

    mcol1, mcol2, mcol3 = m.columns(3)

    mcol1.metric('Total Miles Travelled', helper.format_number(sub_df.Miles.sum()))
    mcol2.metric('Total Money Spent', f'USD {helper.format_number((sub_df.NumTicketsOrdered * sub_df.PricePerTicket).sum())}')
    mcol3.metric('Average Ticket Price', f'USD {helper.format_number(sub_df.PricePerTicket.mean())}')


    st.write("---")

    center_latitude = 39.91523769591209
    center_longitude = -101.47642592426148

    st.header('Routes')
    st.caption('Here, all the available routes in your selection are visualized. The green color indicates the start of the route, while red indicates the end of the route.')

    unique_pairs_df = sub_df.drop_duplicates(subset=['Origin', 'Dest'], keep='first')
    unique_pairs_df.reset_index(drop=True, inplace=True)
    unique_pairs_df['origin_coordinates'] = [list(x) for x in zip(unique_pairs_df.origin_longitude, unique_pairs_df.origin_latitude)]
    unique_pairs_df['dest_coordinates'] = [list(x) for x in zip(unique_pairs_df.dest_longitude, unique_pairs_df.dest_latitude)]

    with st.spinner('Creating Routes Plot. Please Wait...'):
        st.pydeck_chart(
            pdk.Deck(
                map_style = 'road',
                layers = [
                    pdk.Layer(
                    "GreatCircleLayer",
                    unique_pairs_df,
                    pickable=True,
                    get_stroke_width=20,
                    get_source_position="origin_coordinates",
                    get_target_position="dest_coordinates",
                    get_source_color=[21, 180, 52],
                    get_target_color=[136, 8, 8],
                    auto_highlight=True,
                )
                ],
                initial_view_state =  
                    pdk.ViewState(
                        longitude=center_longitude,
                        latitude=center_latitude,
                        zoom=3,
                        min_zoom=3,
                        max_zoom=15,
                        pitch=40.5,
                        #bearing=-27.36)
                    )

            )
        )

    st.write("---")

    p = st.container()

    pcol1, pcol2 = st.columns(2)


    

    pcol1.header('Outbound Flights')
    pcol1.caption('Here, the outbound flights are visualized. Hover over the airports with your cursor to see the exact number of outbound flights.')
    
    with st.spinner('Creating Outbound Flights Plot. Please Wait...'):
        pcol1.pydeck_chart(
            pdk.Deck(
                map_style = 'road',
                layers = [
                    pdk.Layer(
                    'HexagonLayer',  # `type` positional argument is here
                    sub_df,
                    get_position=['origin_longitude', 'origin_latitude'],
                    auto_highlight=True,
                    elevation_scale=50,
                    pickable=True,
                    elevation_range=[0, 15000],
                    extruded=True,
                    coverage=40)
                ],
                initial_view_state =  
                    pdk.ViewState(
                        longitude=center_longitude,
                        latitude=center_latitude,
                        zoom=2,
                        min_zoom=2,
                        max_zoom=15,
                        pitch=40.5,
                        #bearing=-27.36)
                    ),
                tooltip={
                    'html': '<b>Outbound Flights:</b> {elevationValue}',
                    'style': {
                        'color': 'white'
                    }
                }

            )
        )

    pcol2.header('Inbound Flights')
    pcol2.caption('Here, the inbound flights are visualized. Hover over the airports with your cursor to see the exact number of inbound flights.')

    with st.spinner('Creating Inbound Flights Plot. Please Wait...'):
        pcol2.pydeck_chart(
            pdk.Deck(
                map_style = 'road',
                layers = [
                    pdk.Layer(
                    'HexagonLayer',  # `type` positional argument is here
                    sub_df,
                    get_position=['dest_longitude', 'dest_latitude'],
                    auto_highlight=True,
                    elevation_scale=50,
                    pickable=True,
                    elevation_range=[0, 15000],
                    extruded=True,
                    coverage=40,
                    radius = 1000)
                ],
                initial_view_state =  
                    pdk.ViewState(
                        longitude=center_longitude,
                        latitude=center_latitude,
                        zoom=2,
                        min_zoom=2,
                        max_zoom=15,
                        pitch=40.5,
                        #bearing=-27.36)
                    ),
                tooltip={
                'html': '<b>Inbound Flights:</b> {elevationValue}',
                'style': {
                    'color': 'white'
                }
            }

            )
        )

