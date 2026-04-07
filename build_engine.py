import os
import sys
import shutil
from utils import parse_docksmithfile
from image import STATE_DIR, save_image_manifest

def build_image(context_dir, tag, no_cache):
    # 1. Parse Docksmithfile
    docksmithfile = os.path.join(context_dir, 'Docksmithfile')
    if not os.path.exists(docksmithfile):
        print(f"Docksmithfile not found in {context_dir}")
        sys.exit(1)

    steps = parse_docksmithfile(docksmithfile)

    # 2. Setup Temporary build root folder
    temp_root = os.path.join(STATE_DIR, 'tmp', tag.replace(':', '_'))
    if os.path.exists(temp_root):
        shutil.rmtree(temp_root)
    os.makedirs(temp_root, exist_ok=True)

    # Variables to track image state
    current_workdir = "/"

    # 3. Execute Build Steps
    for step_num, step in enumerate(steps, start=1):
        instr = step['instr'].upper()
        arg = step.get('arg', '').strip()
        print(f"Step {step_num}/{len(steps)} : {instr} {arg}")

        # Handle WORKDIR
        if instr == 'WORKDIR':
            current_workdir = arg
            workdir_path = arg[1:] if arg.startswith('/') else arg
            full_workdir = os.path.join(temp_root, workdir_path)
            os.makedirs(full_workdir, exist_ok=True)

        # Handle COPY
        elif instr == 'COPY':
            arg_parts = arg.split()
            if len(arg_parts) >= 2:
                src, dst = arg_parts[0], arg_parts[1]
                
                # Make destination relative to temp_root
                dst_relative = dst[1:] if dst.startswith('/') else dst
                dst_path = os.path.join(temp_root, dst_relative)
                
                # Ensure destination directory exists
                if dst.endswith('/') or not os.path.basename(dst):
                    os.makedirs(dst_path, exist_ok=True)
                    dst_path = os.path.join(dst_path, os.path.basename(src))
                else:
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                src_full_path = os.path.join(context_dir, src)
                if os.path.exists(src_full_path):
                    shutil.copy2(src_full_path, dst_path)
                else:
                    print(f"Error: Source file {src} not found in context.")
                    sys.exit(1)

    # 4. FINAL REGISTRATION
    # Define where the permanent image files will live
    image_files_dir = os.path.join(STATE_DIR, 'image_data', tag.replace(':', '_'))
    
    if os.path.exists(image_files_dir):
        shutil.rmtree(image_files_dir)
    os.makedirs(os.path.dirname(image_files_dir), exist_ok=True)
    
    # Move built files from temp to permanent storage
    shutil.move(temp_root, image_files_dir)

    # Create the metadata dictionary
    manifest_data = {
        "tag": tag,
        "config": {
            "working_dir": current_workdir,
            "image_data_path": image_files_dir
        },
        "layers": [] 
    }

    # CRITICAL: Call the function from image.py to save the .json file
    # This is what makes 'docksmith images' show the result!
    save_image_manifest(tag, manifest_data)

    print(f"Successfully built and tagged {tag}")