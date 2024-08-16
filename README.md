# Project: Nearest Train Station Finder

## Overview
This project is a command-line tool that helps you find the nearest train station to your current location, the next train times, and the closest stations to the nearest station. It uses the Google Maps API for geolocation and various JSON files for station and route data. I (Avi Herman) use it to feed data to a Wayland widgets for Arch Linux which displays train times and station information.

## Files
- `main.py`: The main script that runs the application.
- `getStopData.py`: Contains the `update_times` function used to update train times.
- `data/stations.json`: JSON file containing station data.
- `data/route_stops.json`: JSON file containing route stops data.
- `data/times.json`: JSON file containing train times data.

## Dependencies
- Python 3.x
- `googlemaps` library
- `underground` CLI tool

## Installation
1. Install the required Python packages:
    ```sh
    pip install googlemaps
    ```

3. Install the `underground` CLI tool:
    ```sh
    pip install underground
    ```

## Configuration
1. Obtain a Google Maps API key from the [Google Cloud Console](https://console.cloud.google.com/).
2. Replace the placeholder API key in `main.py` with your actual API key:
    ```python
    gmaps = googlemaps.Client(key="YOUR_API_KEY")
    ```

## Usage
1. To find the nearest station to your current location:
    ```sh
    python main.py
    ```

2. To find the nearest station using a specific station ID:
    ```sh
    python main.py STATION_ID
    ```

## Output
The results will be written to a `results.json` file in the current directory, containing:
- The nearest station and the next train times.
- Information about the 4 closest stations to the nearest station.

## Example
```sh
python main.py
```
Output:
```json
{
    "station_name": {
        "Nearest Station Name": {
            "Route 1": {
                "North-Bound": ["12:30", "12:45", "13:00"],
                "South-Bound": ["12:35", "12:50", "13:05"]
            }
        }
    },
    "4_other_closest_stations": {
        "Closest Station 1": {
            "station_id": "ID1",
            "synonymous_station_ids": ["ID1", "ID2"],
            "routes": ["Route 1", "Route 2"],
            "distance_in_miles": 0.5
        },
        ...
    }
}
