import argparse
import json
import os
import subprocess


def update_times(routes=None):
    # list of all routes to be processed
    all_routes = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "FS",
        "G",
        "GS",
        "H",
        "J",
        "L",
        "M",
        "N",
        "Q",
        "R",
        "SI",
        "W",
        "Z",
    ]

    # if no routes are provided, use all routes
    routes = routes if routes else all_routes

    results = {}
    for route in routes:
        # ignore invalid or empty routes
        if not route or route not in all_routes:
            print(f"Ignoring invalid or empty route: {route}")
            continue

        # command to fetch stops for the route
        command = f"underground stops {route} -f %H:%M --api-key a"
        try:
            # execute the command and decode the output
            output = subprocess.check_output(command, shell=True, timeout=4).decode(
                "utf-8"
            )
            lines = output.split("\n")
            route_results = {}

            # process each line of the output, skipping the first and last two lines
            for line in lines[1:-2]:
                parts = line.split()
                station = parts[0][:-1]
                direction = parts[0][-1]
                times = parts[1:]

                # add times to the route results
                route_results.setdefault(station, {})[direction] = times
                route_results = {k: route_results[k] for k in sorted(route_results)}

            # add route results to the final results dictionary
            results[route] = route_results

        except subprocess.TimeoutExpired:
            print(f"Error: Command timed out for route {route}")
            continue

    # write the results to a JSON file in the current directory
    with open(os.path.join(os.getcwd(), "data/times.json"), "w") as f:
        json.dump(results, f, indent=3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update times for routes.")
    parser.add_argument("--routes", nargs="*", help="List of routes to update")
    args = parser.parse_args()

    update_times(args.routes)
