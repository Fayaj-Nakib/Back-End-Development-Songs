from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

# Task 1: Finish the code for the GET /song endpoint
@app.route("/song", methods=["GET"])
def songs():
    """Return all documents in the songs collection"""
    try:
        # Find all documents in the database collection
        all_songs = list(db.songs.find({}))
        
        # Format response as a dictionary list with standard 200 OK
        return jsonify({"songs": parse_json(all_songs)}), 200
    except Exception as e:
        app.logger.error(f"Database error during fetching songs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Task 2: Implement the /health endpoint
@app.route("/health", methods=["GET"])
def health():
    """Return the health status of the service"""
    return jsonify({"status": "OK"}), 200


# Task 3: Implement the /count endpoint
@app.route("/count", methods=["GET"])
def count():
    """Return the total number of documents in the songs collection"""
    try:
        # Utilizing the db connection defined above to count documents
        count_value = db.songs.count_documents({})
        return jsonify({"count": count_value}), 200
    except Exception as e:
        app.logger.error(f"Database error during count: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Exercise 3: Implement the GET /song/id endpoint
@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    """Find a song by its custom integer id"""
    try:
        # Use find_one to locate the song matching the id
        song = db.songs.find_one({"id": id})
        
        # If the song is not found, return 404 NOT FOUND
        if not song:
            return jsonify({"message": "song with id not found"}), 404
            
        # Return the song parsed as json with a status of 200 OK
        return jsonify(parse_json(song)), 200
    except Exception as e:
        app.logger.error(f"Database error during fetching song {id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Exercise 4: Implement the POST /song endpoint
@app.route("/song", methods=["POST"])
def create_song():
    """Extract a song from the body and insert it into the database"""
    try:
        # Extract the song data from the request body
        new_song = request.get_json()
        
        # Check if a song with the given 'id' already exists in the collection
        existing_song = db.songs.find_one({"id": new_song["id"]})
        if existing_song:
            return jsonify({"Message": f"song with id {new_song['id']} already present"}), 302
            
        # Append to the database collection using insert_one
        result = db.songs.insert_one(new_song)
        
        # Return the inserted id inside a parsed json wrapper with 201 CREATED
        return jsonify({"inserted id": parse_json(result.inserted_id)}), 201
    except Exception as e:
        app.logger.error(f"Database error during creating song: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Exercise 5: Implement the PUT /song endpoint
@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    """Update a song document if it exists in the collection"""
    try:
        # Extract the song tracking data from the incoming request body
        incoming_data = request.get_json()
        
        # Check if the song exists in our collection
        existing_song = db.songs.find_one({"id": id})
        if not existing_song:
            return jsonify({"message": "song not found"}), 404

        # Perform the update operation using the $set argument modifier
        result = db.songs.update_one({"id": id}, {"$set": incoming_data})
        
        # If a document was matched but nothing was changed (data is identical)
        if result.modified_count == 0:
            return jsonify({"message": "song found, but nothing updated"}), 200
            
        # If the database was successfully updated, get the fresh object entry
        updated_song = db.songs.find_one({"id": id})
        return jsonify(parse_json(updated_song)), 201
    except Exception as e:
        app.logger.error(f"Database error during updating song {id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
# Exercise 6: Implement the DELETE /song endpoint
@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    """Delete a song resource from the database collection"""
    try:
        # Use the delete_one method to remove the target document
        result = db.songs.delete_one({"id": id})
        
        # Check the deleted_count attribute
        if result.deleted_count == 0:
            return jsonify({"message": "song not found"}), 404
            
        # Successfully deleted - return an empty body payload with a 204 status
        return "", 204
    except Exception as e:
        app.logger.error(f"Database error during deleting song {id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500