import json
import os
import subprocess


def update_stations():
    # list of all routes to be processed
    all_routes = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "A",
        "C",
        "E",
        "B",
        "D",
        "F",
        "M",
        "N",
        "Q",
        "R",
        "W",
        "L",
        "J",
        "Z",
        "G",
        "FS",
        "GS",
        "H",
        "SI",
    ]

    results = {}

    # iterate over each route
    for route in all_routes:
        if not route:  # safeguard to ensure route is not empty
            print(f"Warning: Skipping empty route")
            continue

        # command to fetch stops for the route
        command = f"underground stops {route} -f %H:%M --api-key a"
        try:
            # execute the command and decode the output
            output = subprocess.check_output(command, shell=True, timeout=4).decode(
                "utf-8"
            )
            lines = output.split("\n")
            route_results = []

            # process each line of the output
            for line in lines[1:-2]:
                parts = line.split()
                station_id = parts[0]

                # remove trailing 'N' or 'S' from station_id
                if station_id[-1] in ["N", "S"]:
                    station_id = station_id[:-1]

                # add station_id to route_results if not already present
                if station_id not in route_results:
                    route_results.append(station_id)
                    route_results.sort()

            # add route results to the final results dictionary
            if route_results:
                results[route] = route_results
            else:
                print(f"Warning: No stations found for route {route}")

        except subprocess.TimeoutExpired:
            print(f"Error: Command timed out for route {route}")
            continue

    # write the results to a JSON file in the current directory
    with open(os.path.join(os.getcwd(), "route_stops.json"), "w") as f:
        json.dump(results, f, indent=3)


if __name__ == "__main__":
    update_stations()
