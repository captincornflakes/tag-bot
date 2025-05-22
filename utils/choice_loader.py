import json
import os

DATASTORE_DIR = os.path.join(os.path.dirname(__file__), '..', 'datastores')

def load_json_list(filename):
    path = os.path.join(DATASTORE_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_genders():
    return load_json_list("genders.json")

def load_pronouns():
    return load_json_list("pronouns.json")

def load_tags():
    return load_json_list("tags.json")