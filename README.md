# Amazon Fulfillment Centre Delivery Optimizer
This project is a Python-based web application that helps users determine the most optimal route and time for deliveries starting and ending at Amazon's new YXX1 Fulfillment Centre in British Columbia. The tool considers real-time traffic data and optimizes both the route order and departure times, displaying results in an interactive dashboard.

## Features
- Can take up to 5 user-specified delivery destinations
- Computes optimal waypoint order for efficient routing
- Retrieves real-time traffic-aware travel durations
- Compares total route duration for different times of the day (8 AM–6 PM) to determine optimal departure time
- Displays delivery duration trends vs. departure times in a line chart

### Example 1
<img src="images/example1.png" width="450">
<img src="images/example2.png" width="450">
<img src="images/example3.png" width="450">

### Example 2
<img src="images/example4.png" width="450">
<img src="images/example5.png" width="450">
<img src="images/example6.png" width="450">

## Technologies
- Python
- Streamlit
- Google Maps Directions API
- Matplotlib
- dotenv

## Installation Guide

### 1️. Clone the repository
```bash
git clone https://github.com/rodmansin/AmazonDeliveryOptimizer.git
cd AmazonDeliveryOptimizer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up .env file
Add your Google Maps Directions API key in the .env file (replace your-key-here with your key):
```bash
GOOGLE_MAPS_API_KEY=your-key-here
```

### 4. Run the app
```bash 
streamlit run app.py
```

## Notes
- Traffic predictions may not be available for distant future dates.
- Separate API calls are made for each leg to factor in traffic data (for some reason, Google Maps Directions API does not return 'duration_in_traffic' when there are additional waypoints other than origin and destination). This may lead to increased API usage and quota consumption with up to 67 API calls per run.