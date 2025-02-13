from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for
from tinydb import TinyDB, Query
import sys

# Set up the TinyDB database
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# Initialize TinyDB
db = TinyDB(os.path.join(SITE_ROOT, 'db.json'))
songs_table = db.table('songs')

def parse_json(data):
    # Parse data to a proper JSON format
    return json.dumps(data, default=str)

@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

@app.route("/count")
def count():
    """Return the length of data"""
    count = len(songs_table.all())
    return {"count": count}, 200

@app.route("/song", methods=["GET"])
def songs():
    """Get all songs in the list"""
    documents = songs_table.all()
    return {"songs": parse_json(documents)}, 200

@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    """Get a song by id"""
    Song = Query()
    song = songs_table.search(Song.id == id)
    
    if not song:
        return {"message": f"song with id {id} not found"}, 404

    return parse_json(song[0]), 200

@app.route("/song", methods=["POST"])
def create_song():
    """Create a new song"""
    new_song = request.json
    Song = Query()
    
    song = songs_table.search(Song.id == new_song["id"])

    if song:
        return {"Message": f"song with id {new_song['id']} already present"}, 302

    # Insert the new song
    songs_table.insert(new_song)

    return {"inserted id": new_song["id"]}, 201

@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    """Update a song"""
    song_in = request.json
    Song = Query()
    
    song = songs_table.search(Song.id == id)

    if not song:
        return {"message": "song not found"}, 404

    # Update the song
    songs_table.update(song_in, Song.id == id)

    updated_song = songs_table.search(Song.id == id)[0]
    return parse_json(updated_song), 201

@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    """Delete a song"""
    Song = Query()
    result = songs_table.remove(Song.id == id)

    if result == 0:
        return {"message": "song not found"}, 404
    else:
        return "", 204
