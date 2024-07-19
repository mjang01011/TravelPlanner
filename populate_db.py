from utils import load_keys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timezone
import uuid
from bson.binary import Binary

client = MongoClient(load_keys()["mongo_uri"], server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client["TravelPlanner"]
users_collection = db["users"]

# Example user data
user_data = {
    "uid": Binary(uuid.uuid4().bytes, 4),
    "username": "user",
    "password": "asd123",
    "email": "john.doe@example.com",
    "queries": [
        {
            "qid": Binary(uuid.uuid4().bytes, 4),
            "query": "I want to do a 2 day roadtrip within LA. I want to visit the famous attractions along the route.",
            "timestamp": datetime.now(timezone.utc),
            "itinerary" : """
                - **Day 1:**
                - Start at your hotel in downtown Los Angeles.
                - Drive to Griffith Observatory (2800 E Observatory Rd, Los Angeles, CA 90027) to enjoy panoramic views of the city and the Hollywood Sign.
                - Head to Hollywood Walk of Fame (Hollywood Blvd & N Highland Ave, Los Angeles, CA 90028) to see the stars on the sidewalk and the TCL Chinese Theatre.
                - Visit The Getty Center (1200 Getty Center Dr, Los Angeles, CA 90049) to explore art collections and beautiful gardens.
                - End the day at Santa Monica Pier (200 Santa Monica Pier, Santa Monica, CA 90401) to enjoy the sunset and amusement park rides.

                - **Day 2:**
                - Start at your hotel in Santa Monica.
                - Drive to Venice Beach (1800 Ocean Front Walk, Venice, CA 90291) to experience the bohemian atmosphere and street performers.
                - Explore the iconic Rodeo Drive (Rodeo Dr, Beverly Hills, CA 90210) for luxury shopping and celebrity sightings.
                - Visit The Griffith Park (4730 Crystal Springs Dr, Los Angeles, CA 90027) for hiking trails and the Los Angeles Zoo.
                - End the road trip with a visit to The Original Farmers Market (6333 W 3rd St, Los Angeles, CA 90036) for diverse food options and unique shopping experiences.
                """,
            "list_of_places": {'start': 'Hotel in downtown Los Angeles', 'end': 'Hotel in Santa Monica', 
                               'stops': ['Griffith Observatory, 2800 E Observatory Rd, Los Angeles, CA 90027', 'Hollywood Walk of Fame, Hollywood Blvd & N Highland Ave, Los Angeles, CA 90028', 'The Getty Center, 1200 Getty Center Dr, Los Angeles, CA 90049', 'Santa Monica Pier, 200 Santa Monica Pier, Santa Monica, CA 90401', 
                                         'Venice Beach, 1800 Ocean Front Walk, Venice, CA 90291', 'Rodeo Drive, Rodeo Dr, Beverly Hills, CA 90210', 'Griffith Park, 4730 Crystal Springs Dr, Los Angeles, CA 90027', 'The Original Farmers Market, 6333 W 3rd St, Los Angeles, CA 90036'], 'transit': 'driving', 
                               'extra_stops': ['The Broad, 221 S Grand Ave, Los Angeles, CA 90012', 'Walt Disney Concert Hall, 111 S Grand Ave, Los Angeles, CA 90012', 'LACMA (Los Angeles County Museum of Art), 5905 Wilshire Blvd, Los Angeles, CA 90036', 'Griffith Park Observatory, 4730 Crystal Springs Dr, Los Angeles, CA 90027', 
                                               'The Hollywood Bowl, 2301 N Highland Ave, Los Angeles, CA 90068', 'Malibu Pier, 23000 Pacific Coast Hwy, Malibu, CA 90265', 'Getty Villa, 17985 Pacific Coast Hwy, Pacific Palisades, CA 90272', 'Third Street Promenade, Santa Monica, CA 90401', 'Abbot Kinney Boulevard, Venice, CA 90291']}
        },
        {
            "qid": Binary(uuid.uuid4().bytes, 4),
            "query": "I want to do a 3 day roadtrip within New York. I want to visit the famous attractions along the route.",
            "timestamp": datetime.now(timezone.utc),
            "itinerary": """
                - Day 1:
                - Start at Times Square, Manhattan, NY 10036
                    - Explore Times Square and take in the vibrant atmosphere
                    - Visit the Empire State Building at 20 W 34th St, New York, NY 10118
                    - Walk through Central Park and enjoy the greenery
                    - Head to the Museum of Modern Art at 11 W 53rd St, New York, NY 10019
                - End the day at Rockefeller Center, 45 Rockefeller Plaza, New York, NY 10111

                - Day 2:
                - Start at Statue of Liberty National Monument, New York, NY 10004
                    - Take a ferry to visit the Statue of Liberty and Ellis Island
                - Head to One World Trade Center, 285 Fulton St, New York, NY 10007
                    - Visit the One World Observatory for panoramic views of the city
                    - Explore the 9/11 Memorial & Museum at 180 Greenwich St, New York, NY 10007
                - End the day at Brooklyn Bridge, New York, NY 10038
                    - Walk across the Brooklyn Bridge and enjoy the views of the city skyline

                - Day 3:
                - Start at The Metropolitan Museum of Art, 1000 5th Ave, New York, NY 10028
                    - Explore the extensive art collections at the Met
                - Head to Times Square for some last-minute shopping and souvenirs
                - End the trip with a visit to Broadway for a show at one of the famous theaters

                - End of the 3-day trip in NY.
            """,
            'list_of_places':  {'start': 'Times Square, Manhattan, NY 10036', 'end': 'Broadway, New York, NY', 
                                'stops': ['Empire State Building, 20 W 34th St, New York, NY 10118', 'Central Park, New York, NY', 'Museum of Modern Art, 11 W 53rd St, New York, NY 10019', 'Rockefeller Center, 45 Rockefeller Plaza, New York, NY 10111', 'Statue of Liberty National Monument, New York, NY 10004', 
                                          'One World Trade Center, 285 Fulton St, New York, NY 10007', '9/11 Memorial & Museum, 180 Greenwich St, New York, NY 10007', 'Brooklyn Bridge, New York, NY 10038', 'The Metropolitan Museum of Art, 1000 5th Ave, New York, NY 10028'], 'transit': 'walking', 
                                'extra_stops': ['Central Park Zoo, E 64th St, New York, NY 10021', 'The High Line, New York, NY', 'Grand Central Terminal, 89 E 42nd St, New York, NY 10017', 'Times Square, New York, NY', 'Carnegie Hall, 881 7th Ave, New York, NY 10019', 'Battery Park, New York, NY', 
                                                'Chinatown, New York, NY', 'The Vessel, 20 Hudson Yards, New York, NY 10001', 'Madison Square Garden, 4 Pennsylvania Plaza, New York, NY 10001', 'The Cloisters, 99 Margaret Corbin Dr, New York, NY 10040']}
        }
    ],
    
}

result = users_collection.insert_one(user_data)
print(f"User inserted with id: {result.inserted_id}")
