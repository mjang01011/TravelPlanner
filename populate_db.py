from utils import load_keys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timezone

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
    "user_id": "john_doe",
    "password_hash": "hashed_password_here",
    "email": "john.doe@example.com",
    "created_at": datetime.now(timezone.utc),
    "last_login": datetime.now(timezone.utc),
    "queries": [
        {
            "query": "I want to do a 4 day roadtrip within Paris. I want to visit the famous attractions along the route.",
            "timestamp": datetime.now(timezone.utc),
            "itinerary_details": "itinery_detail_ex1"
        },
        {
            "query": "I want to do a 7 day roadtrip from Madrid to London. I want to visit the famous attractions along the route.",
            "timestamp": datetime.now(timezone.utc),
            "output": "itinery_detail_ex2"
        }
    ]
}

result = users_collection.insert_one(user_data)
print(f"User inserted with id: {result.inserted_id}")
