import os
import json
import tarfile
import hashlib
from datetime import datetime

def create_layer(source_dir, layer_path):
    with tarfile.open(layer_path, "w") as tar:
        tar.add(source_dir, arcname=".")

def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def build_image(context, tag, no_cache):
    print("Reading Docksmithfile...")

    file_path = os.path.join(context, "Docksmithfile")

    if not os.path.exists(file_path):
        print("Error: Docksmithfile not found")
        return

    original_dir = os.getcwd()

    images_dir = os.path.expanduser("~/.docksmith/images")
    layers_dir = os.path.expanduser("~/.docksmith/layers")
    cache_dir = os.path.expanduser("~/.docksmith/cache")

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(layers_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    layer_count = 0
    cmd_to_run = ""

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        print("Processing:", line)

        parts = line.split(" ", 1)
        instruction = parts[0]

        # -------- FROM --------
        if instruction == "FROM":
            print("Using base image:", parts[1])

        # -------- WORKDIR --------
        elif instruction == "WORKDIR":
            path = parts[1]
            print("Setting WORKDIR:", path)
            os.makedirs(path, exist_ok=True)
            os.chdir(path)

        # -------- COPY --------
        elif instruction == "COPY":
            hash_val = get_hash(line)
            cache_path = os.path.join(cache_dir, hash_val)

            if os.path.exists(cache_path) and not no_cache:
                print("[CACHE HIT] COPY skipped")
                continue
            else:
                print("[CACHE MISS] COPY executing")

            src, dest = parts[1].split(" ")
            os.system(f"cp -r {src} {dest}")

            open(cache_path, "w").close()

            layer_count += 1
            layer_path = os.path.join(layers_dir, f"layer{layer_count}.tar")
            create_layer(original_dir, layer_path)
            print("Layer created:", layer_path)

        # -------- ENV --------
        elif instruction == "ENV":
            key, value = parts[1].split("=")
            os.environ[key] = value

        # -------- RUN --------
        elif instruction == "RUN":
            hash_val = get_hash(line)
            cache_path = os.path.join(cache_dir, hash_val)

            if os.path.exists(cache_path) and not no_cache:
                print("[CACHE HIT] RUN skipped")
                continue
            else:
                print("[CACHE MISS] RUN executing")

            os.system(parts[1])

            open(cache_path, "w").close()

            layer_count += 1
            layer_path = os.path.join(layers_dir, f"layer{layer_count}.tar")
            create_layer(original_dir, layer_path)
            print("Layer created:", layer_path)

        # -------- CMD --------
        elif instruction == "CMD":
            cmd_to_run = parts[1]

        else:
            print("Unknown instruction:", instruction)
            return

    name, tag_val = tag.split(":")
    image_path = os.path.join(images_dir, f"{name}_{tag_val}.json")

    image_data = {
        "name": name,
        "tag": tag_val,
        "created": str(datetime.now()),
        "cmd": cmd_to_run,
        "layers": layer_count
    }

    with open(image_path, "w") as f:
        json.dump(image_data, f, indent=4)

    print("Image saved at:", image_path)

    os.chdir(original_dir)

    print("Build complete!")
