import googlemaps
import datetime

class Router:
    def __init__(self, google_maps_key):
        self.gmaps = googlemaps.Client(key=google_maps_key)
        
    # Function to get the coordinates of a given address using geocode
    def get_coords(self, input_address):
        return self.gmaps.geocode(input_address)

    # # Example usage of the function to get coordinates of the "Eiffel Tower"
    # example_coords = get_coords("Eiffel Tower")
    # print(example_coords)

    # Define a function to get coordinates for the start, end, and optional stops of a route
    def get_stop_coordinates(self, start, end, stops):
        coordinates = {}

        # Get coordinates for the start location and add to the dictionary
        coordinates["start"] = self.get_coords(start)[0]

        # Get coordinates for the end location and add to the dictionary
        coordinates["end"] = self.get_coords(end)[0]

        # If there are any stops, iterate through each stop to get its coordinates and add to the dictionary
        if stops:
            for i, stop in enumerate(stops):
                coordinates[f"stop_{i}"] = self.get_coords(stop)[0]

        # Return the dictionary containing coordinates for the start, end, and stops
        return coordinates


    # Define get_route to get the route using given coordinates and optional parameters
    def get_route(self, coordinates, start_time=None, transit_type=None, verbose=True):
        if not start_time:
            start_time = datetime.datetime.now()

        if not transit_type:
            transit_type = "driving"

        # Extract the formatted addresses of stops from the coordinates dictionary
        stops = [
            coordinates[key]["formatted_address"]
            for key in coordinates.keys()
            if "stop" in key
        ]

        # Extract the formatted address of the start location
        start = coordinates["start"]["formatted_address"]

        # Extract the formatted address of the end location
        end = coordinates["end"]["formatted_address"]

        # Get directions from Google Maps API using the start, end, and stops
        route = self.gmaps.directions(
            start,
            end,
            waypoints=stops,
            mode=transit_type,
            units="metric",
            optimize_waypoints=True,
            traffic_model="best_guess",
            departure_time=start_time,
        )

        return route
    
    def make_markers(self, route):
        directions_result = self.get_route(
            self.get_stop_coordinates(
                route["start"], route["end"], route["stops"]
            )
        )

        # Initialize an empty list to store marker points
        marker_points = []

        # Get the number of legs in the directions result
        nlegs = len(directions_result[0]["legs"])

        # Iterate over each leg in the directions result
        for i, leg in enumerate(directions_result[0]["legs"]):

            # Extract the start location and start address of the leg
            start, start_address = leg["start_location"], leg["start_address"]

            # Extract the end location and end address of the leg
            end, end_address = leg["end_location"], leg["end_address"]

            # Convert the start location latitude and longitude to floats and create a tuple
            start_loc = (float(start["lat"]), float(start["lng"]))

            # Convert the end location latitude and longitude to floats and create a tuple
            end_loc = (float(end["lat"]), float(end["lng"]))

            # Append the start location and start address to the marker points list
            marker_points.append((start_loc, start_address))

            # If this is the last leg, append the end location and end address to the marker points list
            if i == nlegs - 1:
                marker_points.append((end_loc, end_address))
        return directions_result, marker_points