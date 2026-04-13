import os
import json
import shutil

def run_container(name_tag, cmd_override, env_overrides):
    print("Running container with isolation...")

    name, tag_val = name_tag.split(":")
    image_path = os.path.expanduser(f"~/.docksmith/images/{name}_{tag_val}.json")

    if not os.path.exists(image_path):
        print("Error: Image not found.")
        return

    with open(image_path, "r") as f:
        image = json.load(f)

    cmd = image["cmd"]

    if cmd_override:
        cmd = " ".join(cmd_override)

    for key, value in env_overrides.items():
        os.environ[key] = value

    # --------------------------
    # CREATE ISOLATED FS
    # --------------------------
    container_root = os.path.expanduser(f"~/.docksmith/containers/{name}_{tag_val}")

    if os.path.exists(container_root):
        shutil.rmtree(container_root)

    os.makedirs(container_root, exist_ok=True)

    # copy current project into container
    os.system(f"cp -r . {container_root}")

    print("Container filesystem created at:", container_root)

    # --------------------------
    # RUN COMMAND INSIDE IT
    # --------------------------
    os.chdir(container_root)

    print("Executing CMD in isolated environment:", cmd)
    os.system(cmd)

    # return back
    os.chdir("..")
