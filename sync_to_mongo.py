import os
import json
import pytz
from datetime import datetime
from pymongo import MongoClient

def sync_to_mongo():
    # Read environment variables
    project_key = os.getenv("PROJECT_KEY")
    project_name = os.getenv("PROJECT_NAME", "Unnamed Project")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB", "sonarqube_db")
    collection_name = os.getenv("MONGO_COLLECTION", "analysis_results")
    json_file_path = os.getenv("SONAR_JSON", "sonar_results.json")
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    # Load SonarQube results from local file (fetched already by curl)
    with open(json_file_path) as f:
        data = json.load(f)

    if "component" not in data or "measures" not in data["component"]:
        print("⚠ Error: Invalid SonarQube JSON format.")
        return

    # Extract metrics
    measures = {m['metric']: m.get('value', '0') for m in data['component']['measures']}

    # Create the document to insert/update
    document = {
        "project_key": project_key,
        "project_name": project_name,
        "analysis": measures,
        "last_updated": timestamp
    }

    # Connect to MongoDB and perform upsert
    client = MongoClient(mongo_uri)
    collection = client[db_name][collection_name]

    collection.insert_one(document)

    print(f"✔ Synced SonarQube results for '{project_key}' to MongoDB.")

if __name__ == "__main__":
    sync_to_mongo()
