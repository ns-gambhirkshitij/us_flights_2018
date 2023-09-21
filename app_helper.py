import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

@st.cache_resource
def load_data():
    df = pd.read_csv('flight_data.csv')
    airports = pd.read_csv('airports.csv')

    # Origin Coordinates + Origin Airport Names

    df = df.merge(airports, left_on='Origin', right_on='IATA', how='left')
    df.rename(columns={'LATITUDE': 'origin_latitude', 'LONGITUDE': 'origin_longitude', 'AIRPORT': 'origin_airport_name'}, inplace=True)
    df.drop(columns=['IATA', 'CITY', 'STATE', 'COUNTRY'], inplace=True)
    df.origin_airport_name = df.Origin + " - " + df.origin_airport_name

    # Destination Coordinates

    df = df.merge(airports, left_on='Dest', right_on='IATA', how='left')
    df.rename(columns={'LATITUDE': 'dest_latitude', 'LONGITUDE': 'dest_longitude', 'AIRPORT': 'dest_airport_name'}, inplace=True)
    df.drop(columns=['IATA', 'CITY', 'STATE', 'COUNTRY'], inplace=True)
    df.dest_airport_name = df.Dest + " - " + df.dest_airport_name

    # Airline Names

    airlines = [('WN', 'Southwest Airlines Co.'), ('DL', 'Delta Air Lines Inc.'), ('AA', 'American Airlines Inc.'),
                ('UA', 'United Air Lines Inc.'), ('B6', 'JetBlue Airways'), ('AS', 'Alaska Airlines Inc.'),
                ('NK', 'Spirit Air Lines'), ('G4', 'Allegiant Air'), ('F9', 'Frontier Airlines Inc.'),
                ('HA', 'Hawaiian Airlines Inc.'), ('SY', 'Sun Country Airlines d/b/a MN Airlines'), ('VX', 'Virgin America')]

    airline_tags, airline_names = zip(*airlines)

    airlines = pd.DataFrame({'airline_tags': airline_tags, 'airline_names': airline_names})

    df = df.merge(airlines, left_on='AirlineCompany', right_on='airline_tags', how = 'left')
    df.rename(columns={'airline_names': 'airline_name'}, inplace = True)
    df.drop(columns = ['airline_tags'], inplace = True)
    df.airline_name = df.AirlineCompany + " - " + df.airline_name

    return df, airports

def format_number(value):
    if abs(value) >= 1e9:
        # If the value is in billions (e.g., 2 billion)
        formatted_value = f'{value / 1e9:.2f}B'
    elif abs(value) >= 1e6:
        # If the value is in millions (e.g., 2 million)
        formatted_value = f'{value / 1e6:.2f}M'
    elif abs(value) >= 1e3:
        # If the value is in thousands (e.g., 2 thousand)
        formatted_value = f'{value / 1e3:.2f}k'
    else:
        # For values less than 1000, format with up to 2 decimal places
        formatted_value = f'{value:.2f}'
    
    return formatted_value