import os
import tarfile
import shutil
import json
import hashlib
from utils import get_state_dir, ensure_dir, zero_tarinfo
from image import save_image_manifest, get_layer_path

# This script imports a minimal base image (e.g., python:3.11 rootfs) into ~/.docksmith/images and ~/.docksmith/layers
# Usage: python import_base_image.py /path/to/python311-rootfs.tar python:3.11

def compute_digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return 'sha256:' + h.hexdigest()

def main():
    import sys
    if len(sys.argv) != 3:
        print("Usage: python import_base_image.py /path/to/rootfs.tar python:3.11")
        sys.exit(1)
    tar_path, name_tag = sys.argv[1:3]
    state_dir = get_state_dir()
    images_dir = os.path.join(state_dir, 'images')
    layers_dir = os.path.join(state_dir, 'layers')
    ensure_dir(images_dir)
    ensure_dir(layers_dir)
    # Copy tar to layers dir
    digest = compute_digest(tar_path)
    layer_path = get_layer_path(digest)
    shutil.copy2(tar_path, layer_path)
    size = os.path.getsize(layer_path)
    # Manifest
    name, tag = name_tag.split(':') if ':' in name_tag else (name_tag, 'latest')
    manifest = {
        'name': name,
        'tag': tag,
        'digest': '',
        'created': '',
        'config': {
            'Env': [],
            'Cmd': None,
            'WorkingDir': '/'
        },
        'layers': [
            {'digest': digest, 'size': size, 'createdBy': '<imported base>'}
        ]
    }
    # Compute manifest digest
    manifest_bytes = json.dumps({**manifest, 'digest': ''}, sort_keys=True).encode()
    manifest_digest = 'sha256:' + hashlib.sha256(manifest_bytes).hexdigest()
    manifest['digest'] = manifest_digest
    from datetime import datetime
    manifest['created'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    save_image_manifest(manifest)
    print(f"Imported base image {name_tag} as {manifest_digest}")

if __name__ == '__main__':
    main()
