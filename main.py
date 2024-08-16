import json
import os
import sys
import time
from collections import OrderedDict
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt

import googlemaps

from getStopData import update_times


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: Distance between the two points in kilometers.
    """
    # radius of the Earth in kilometers
    R = 6371.0088

    # convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # compute differences in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # apply the haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # return the distance in kilometers
    return R * c


def load_stations():
    """
    Load station data from a JSON file in the current directory.

    Returns:
        list: A list of tuples containing station ID, name, and coordinates.
    """
    with open(os.path.join(os.getcwd(), "data/stations.json"), "r") as f:
        data = json.load(f)
        return [
            (id, info["stop_name"], *map(float, info["stop_coordinates"].split(",")))
            for id, info in data.items()
        ]


def find_nearest_station(stations, current_location):
    """
    Find the nearest station to the current location.

    Args:
        stations (list): List of station tuples.
        current_location (dict): Dictionary containing 'lat' and 'lng' keys.

    Returns:
        tuple: The nearest station tuple.
    """
    return min(
        stations,
        key=lambda station: haversine(
            current_location["lat"], current_location["lng"], station[2], station[3]
        ),
    )


def load_route_stops():
    """
    Load route stops data from a JSON file in the current directory.

    Returns:
        dict: Dictionary containing route stops data.
    """
    with open(os.path.join(os.getcwd(), "data/route_stops.json"), "r") as f:
        return json.load(f)


def find_routes_for_stop(route_stops, stop_name, stations, original_station_coords):
    """
    Find routes that include the given stop name and coordinates.

    Args:
        route_stops (dict): Dictionary containing route stops data.
        stop_name (str): Name of the stop.
        stations (list): List of station tuples.
        original_station_coords (tuple): Coordinates of the original station.

    Returns:
        list: List of routes that include the stop.
    """
    stop_ids = [
        station[0]
        for station in stations
        if station[1] == stop_name
        and haversine(
            original_station_coords[0],
            original_station_coords[1],
            station[2],
            station[3],
        )
        <= 0.2
    ]

    return [
        route
        for route, stops in route_stops.items()
        if any(stop_id in stops for stop_id in stop_ids)
    ]


def get_next_trains(nearest_station, routes, stations, exclude_times=False):
    """
    Get the next train times for the nearest station.

    Args:
        nearest_station (tuple): The nearest station tuple.
        routes (list): List of routes that include the nearest station.
        stations (list): List of station tuples.
        exclude_times (bool): Whether to exclude times from the result.

    Returns:
        dict: Dictionary containing the next train times for the nearest station.
    """
    if exclude_times:
        return {nearest_station[1]: {}}

    with open(os.path.join(os.getcwd(), "data/times.json"), "r") as f:
        times_data = json.load(f)

    now = datetime.now().strftime("%H:%M")
    result = {}
    for route, stations_times in times_data.items():
        if route not in routes:
            continue
        for station in stations:
            if station[1] != nearest_station[1]:
                continue
            station_id_str = str(station[0])
            station_times = stations_times.get(station_id_str, {})
            for direction in ["N", "S"]:
                direction_name = "North-Bound" if direction == "N" else "South-Bound"
                times = station_times.get(direction, [])
                sorted_times = sorted(
                    times, key=lambda x: datetime.strptime(x, "%H:%M")
                )
                next_times = [time for time in sorted_times if time > now][:3]
                if route not in result:
                    result[route] = OrderedDict()
                if next_times:
                    result[route][direction_name] = next_times
    return {nearest_station[1]: result}


def find_closest_stations(stations, nearest_station):
    """
    Find the closest stations to the nearest station.

    Args:
        stations (list): List of station tuples.
        nearest_station (tuple): The nearest station tuple.

    Returns:
        list: List of the closest station tuples.
    """
    sorted_stations = sorted(
        stations,
        key=lambda station: haversine(
            nearest_station[2], nearest_station[3], station[2], station[3]
        ),
    )

    closest_stations = []
    for station in sorted_stations:
        if station == nearest_station:
            continue
        if (
            station[1] == nearest_station[1]
            and haversine(
                nearest_station[2], nearest_station[3], station[2], station[3]
            )
            < 0.2
        ):
            continue
        closest_stations.append(station)
        if len(closest_stations) == 12:
            break

    print(closest_stations)
    return closest_stations


def main():
    """
    Main function to find the nearest station, routes, next trains, and closest stations.
    """
    # initialize the Google Maps client
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    gmaps = googlemaps.Client(key=api_key)

    # load station and route stop data
    stations = load_stations()
    route_stops = load_route_stops()

    if len(sys.argv) == 1:
        # geolocate the current position
        geolocate_result = gmaps.geolocate()
        current_location = geolocate_result["location"]
        nearest_station = find_nearest_station(stations, current_location)
        print(
            f"The nearest station is {nearest_station[1]} with ID {nearest_station[0]} at coordinates {nearest_station[2]}, {nearest_station[3]}"
        )
    else:
        # use the station ID provided as a command-line argument
        station_id = sys.argv[1].upper()
        nearest_station = next(
            (station for station in stations if station[0] == station_id), None
        )
        if nearest_station is None:
            print("Invalid station ID.")
            return
        print(
            f"You selected {nearest_station[1]} with ID {nearest_station[0]} located at coordinates {nearest_station[2]}, {nearest_station[3]}"
        )

    # find routes for the nearest station
    routes = find_routes_for_stop(
        route_stops,
        nearest_station[1],
        stations,
        (nearest_station[2], nearest_station[3]),
    )

    # call update_times directly instead of using threading
    update_times(routes)

    # get the next trains for the nearest station
    nearest_station_trains = get_next_trains(
        nearest_station, routes, stations, exclude_times=False
    )

    # find the closest stations to the nearest station
    closest_stations = find_closest_stations(stations, nearest_station)
    closest_stations_info = {}
    for station in closest_stations:
        distance_in_miles = round(
            haversine(nearest_station[2], nearest_station[3], station[2], station[3])
            * 0.621371,
            2,
        )
        synonymous_ids = [
            s[0]
            for s in stations
            if s[1] == station[1]
            and haversine(station[2], station[3], s[2], s[3]) <= 0.2
        ]
        routes = find_routes_for_stop(
            route_stops, station[1], stations, (station[2], station[3])
        )
        station_name = station[1].split("-")[0].strip()
        if station_name in closest_stations_info:
            station_name += f"\xa0"
        closest_stations_info[station_name] = {
            "station_id": station[0],
            "synonymous_station_ids": synonymous_ids,
            "routes": routes,
            "distance_in_miles": distance_in_miles,
        }

    # sort closest_stations_info by distance_in_miles
    sorted_closest_stations_info = OrderedDict(
        sorted(
            closest_stations_info.items(), key=lambda item: item[1]["distance_in_miles"]
        )
    )

    result = {
        "station_name": nearest_station_trains,
        "4_other_closest_stations": sorted_closest_stations_info,
    }

    # write the result to a JSON file in the current directory
    with open(os.path.join(os.getcwd(), "results.json"), "w") as f:
        json.dump(result, f, indent=4)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
