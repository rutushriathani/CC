import os
import json
import shutil
from utils import get_state_dir, ensure_dir

# Force the state directory to be local to your project for easier debugging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, 'data')

IMAGES_DIR = os.path.join(STATE_DIR, 'images')
LAYERS_DIR = os.path.join(STATE_DIR, 'layers')
CACHE_DIR = os.path.join(STATE_DIR, 'cache')
CACHE_INDEX_PATH = os.path.join(CACHE_DIR, 'index.json')

def get_image_manifest_path(name_tag):
    # Converts 'myimage:latest' to 'myimage_latest.json' to avoid filename issues
    safe_name = name_tag.replace(':', '_')
    return os.path.join(IMAGES_DIR, f"{safe_name}.json")

def save_image_manifest(name_tag, data):
    ensure_dir(IMAGES_DIR)
    path = get_image_manifest_path(name_tag)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Manifest saved to: {path}")

def load_image_manifest(name_tag):
    path = get_image_manifest_path(name_tag)
    if not os.path.exists(path):
        print(f"Error: Image '{name_tag}' not found.")
        return None
    with open(path, "r") as f:
        return json.load(f)

def list_images():
    ensure_dir(IMAGES_DIR)
    images = [f.replace('.json','').replace('_', ':') for f in os.listdir(IMAGES_DIR) if f.endswith('.json')]
    
    if not images:
        print("No images found in local store.")
    else:
        print("REPOSITORY          TAG")
        for img in images:
            if ':' in img:
                repo, tag = img.split(':', 1)
                print(f"{repo:<20} {tag}")
            else:
                print(f"{img:<20} latest")
    return images

def remove_image(name_tag):
    path = get_image_manifest_path(name_tag)
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted image: {name_tag}")
    else:
        print(f"Image {name_tag} not found.")

def get_layer_path(layer_id):
    return os.path.join(LAYERS_DIR, f"{layer_id}.tar")

def save_layer_tar(layer_id, tar_bytes):
    ensure_dir(LAYERS_DIR)
    with open(get_layer_path(layer_id), "wb") as f:
        f.write(tar_bytes)

def ensure_cache_index():
    ensure_dir(CACHE_DIR)
    if not os.path.exists(CACHE_INDEX_PATH):
        with open(CACHE_INDEX_PATH, "w") as f:
            json.dump({}, f)

def get_cache_index():
    ensure_cache_index()
    with open(CACHE_INDEX_PATH, "r") as f:
        return json.load(f)

def save_cache_index(index_data):
    ensure_cache_index()
    with open(CACHE_INDEX_PATH, "w") as f:
        json.dump(index_data, f)
def show_history(name_tag):
    import os

    print("Image History for:", name_tag)

    if not os.path.exists("Docksmithfile"):
        print("Docksmithfile not found")
        return

    with open("Docksmithfile", "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line:
            print(line)
