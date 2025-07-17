import streamlit as st
import googlemaps
import datetime
import matplotlib.pyplot as plt
#Environment variable imports
from dotenv import load_dotenv
import os

#Google Maps API setup 
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

WAREHOUSE_ADDRESS = 'Amazon Fulfillment Centre (YXX1)' 

st.title("Amazon Fulfillment Centre Delivery Optimizer")

st.header("Enter Delivery Addresses (1-5):")
destinations = []   # List for delivery addresses (user input)

for i in range (0, 5): 
    address = st.text_input("Delivery Address " + str(i+1))
    if address:
        destinations.append(address)

selected_date = st.date_input("Select Delivery Date:", datetime.date.today())

if st.button("Optimize Route and Time") and destinations: 
    departure_times = []    # List of departure times
    travel_times = []   # List of total travel time for each departure time

    now = datetime.datetime.now()
    start_hour = 8
    if selected_date == datetime.date.today():
        start_hour = now.hour + 1

    for hour in range(start_hour, 19):   # From 8:00 (8AM) to 18:00 (6PM)
        dt = datetime.datetime.combine(selected_date, datetime.time(hour, 0))
        if selected_date == datetime.date.today() and dt < now:
            continue
        time = int(dt.timestamp())    # Unix timestamp for Google Maps API
        departure_times.append(str(hour) + ":00")

        try: 
            directions_result = gmaps.directions(
                origin = WAREHOUSE_ADDRESS,
                destination = WAREHOUSE_ADDRESS,
                waypoints = ["optimize:true"] + destinations,  # Optimize waypoint order for fastest route
                departure_time = time,
                traffic_model = 'best_guess',   # Google's best guess for traffic
                mode='driving'
            )

            if directions_result:
                # Sum of duration of all "legs" of route (divided by 60 to convert from seconds to minutes)
                total_duration = sum(leg.get('duration_in_traffic', leg['duration'])['value']   #Get leg's "duration in traffic" value, or fallback to duration (without traffic)
                                     for leg in directions_result[0]['legs']) / 60  
                travel_times.append(total_duration)
            else:
                travel_times.append(None)
        except Exception as e: 
            st.error("API Error" + str(e))
            travel_times.append(None)
        
    # Loop through all departure times and keep the ones with durations that are not None
    valid_results = [(time, duration) for time, duration in zip (departure_times, travel_times) if duration is not None]
    if valid_results:
        optimal_time, shortest_duration = min(valid_results, key = lambda x: x[1])
        rounded_duration = round(shortest_duration)
        st.success("Optimal departure time: " + optimal_time + " (" + str(rounded_duration) + "minutes)")
        
        #Matplotlib graph
        fig, ax = plt.subplots()
        ax.plot(departure_times, travel_times, marker = 'o')
        ax.set_xlabel("Departure Time")
        ax.set_ylabel("Total Duration (minutes)")
        ax.set_title("Estimated Delivery Duration vs Departure Time")
        st.pyplot(fig)
    else:
        st.error("Error: No valid durations from API")
else:
    st.info("Enter at least one delivery address and click Optimize.")