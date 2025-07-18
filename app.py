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

st.title("Amazon YXX1 Fulfillment Centre Delivery Optimizer")

st.header("Enter Delivery Addresses (1-5):")
destinations = []   # List for delivery addresses (user input)

for i in range (5): 
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

    # First API call to get optimized waypoint order (no duration_with_traffic data)
    try: 
        optimize_result = gmaps.directions(
            origin = WAREHOUSE_ADDRESS,
            destination = WAREHOUSE_ADDRESS,
            waypoints = ["optimize:true"] + destinations,
            mode='driving'
        )
        
        #Get optimized waypoint order (fastest route)
        if optimize_result and 'waypoint_order' in optimize_result[0]:
            waypoint_order = optimize_result[0]['waypoint_order']
            ordered_destinations = []
            for i in waypoint_order:
                ordered_destinations.append(destinations[i])
        else: 
            st.warning("Optimization for waypoint order failed. Using entered order.")
            ordered_destinations = destinations
    except Exception as e: 
        st.error("Error: " + str(e))
        ordered_destinations = destinations

    for hour in range(start_hour, 19):   # From 8:00 (8AM) to 18:00 (6PM)
        dt = datetime.datetime.combine(selected_date, datetime.time(hour, 0))
        if selected_date == datetime.date.today() and dt < now:
            continue
        time = int(dt.timestamp())    # Unix timestamp for Google Maps API
        departure_times.append(str(hour) + ":00")

        total_duration = 0
        leg_error = False
        route = [WAREHOUSE_ADDRESS] + ordered_destinations + [WAREHOUSE_ADDRESS]    # Full route with all waypoints starting and ending at warehouse

        # API call for each "leg" (between each destination/warehouse) 
        for i in range(len(route) - 1):
            origin = route[i]
            destination = route[i+1]
            try: 
                result = gmaps.directions(
                    origin = route[i],
                    destination = route[i+1],
                    departure_time = time,
                    traffic_model = 'best_guess',   # Google's best guess for traffic
                    mode='driving'
                )
                if result: 
                    leg = result[0]['legs'][0]
                    # If traffic data is available
                    if 'duration_in_traffic' in leg:
                        duration = leg['duration_in_traffic']['value'] / 60 #Convert to minutes
                    # No traffic data -> duration without traffic factored in
                    else:
                        duration = leg['duration']['value'] / 60
                    total_duration += duration
                else: 
                    leg_error = True
                    break
            except Exception as e:
                st.error("API Error for leg " + str(i+1))
                leg_error = True
                break
        if leg_error == False: 
            travel_times.append(total_duration)
        else:
            travel_times.append(None)
        
    # Loop through all departure times and keep the ones with durations that are not None
    valid_results = [(time, duration) for time, duration in zip (departure_times, travel_times) if duration is not None]
    if valid_results:
        optimal_time, shortest_duration = min(valid_results, key = lambda x: x[1])
        rounded_duration = round(shortest_duration)
        st.success("Optimal departure time: " + optimal_time + " (" + str(rounded_duration) + " minutes)")
        
        #Matplotlib graph
        fig, ax = plt.subplots()
        ax.plot(departure_times, travel_times, marker = 'o')
        ax.set_xlabel("Departure Time")
        ax.set_ylabel("Total Duration (minutes)")
        ax.set_title("Estimated Delivery Duration vs Departure Time")
        st.pyplot(fig)
    else:
        st.error("Error: No valid durations from API")

    # Print optimized route
    st.subheader("Optimized Delivery Route:")
    for i in range(len(ordered_destinations)):
        st.markdown(str(i+1) + ". " + ordered_destinations[i])
else:
    st.info("Enter at least one delivery address and click Optimize.")