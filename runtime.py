import os
import sys
import subprocess
import shutil

def run_container(name_tag, cmd_override, env_overrides):
    # 1. Load the manifest
    from image import load_image_manifest
    manifest = load_image_manifest(name_tag)
    
    if not manifest:
        print(f"Error: Image '{name_tag}' not found.")
        sys.exit(1)

    # 2. Locate the image data
    # We use the path saved during the build process
    image_data_path = manifest['config'].get('image_data_path')
    
    if not image_data_path or not os.path.exists(image_data_path):
        print(f"Error: Image data not found at {image_data_path}")
        sys.exit(1)

    # 3. Prepare Environment
    env = os.environ.copy()
    # Add any environment variables saved in the manifest
    for e in manifest['config'].get('Env', []):
        if '=' in e:
            k, v = e.split('=', 1)
            env[k] = v
    env.update(env_overrides)

    # 4. Prepare Command (CMD)
    # Priority: Command line override > Manifest default
    cmd = cmd_override if cmd_override else manifest['config'].get('Cmd')
    
    if not cmd:
        print("No CMD defined. Usage: python3 docksmith.py run <image> <command>")
        sys.exit(1)

    # 5. Determine Working Directory
    workdir = manifest['config'].get('working_dir', '/')
    # Make it relative to the image data path
    if workdir.startswith('/'):
        workdir = workdir[1:]
    
    run_path = os.path.join(image_data_path, workdir)

    # 6. Execute (Simulated Container)
    # Instead of chroot, we change directory and run via subprocess
    # This allows us to use the host's Python while running the image's files
    try:
        print(f"--- Container Starting: {name_tag} ---")
        
        # If the command is 'python3', use the absolute path to YOUR python
        if cmd[0] == "python3":
            cmd[0] = sys.executable

        subprocess.run(
            cmd,
            cwd=run_path,
            env=env,
            check=True
        )
        
        print(f"--- Container Exited Successfully ---")
        
    except subprocess.CalledProcessError as e:
        print(f"Container failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"Error: Command '{cmd[0]}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def run_in_build(root, command, env, workdir):
    """
    Used during the build process to run commands inside the temp root.
    Simplified for macOS compatibility.
    """
    envp = os.environ.copy()
    envp.update(env)
    
    # Adjust workdir path
    actual_workdir = os.path.join(root, workdir[1:] if workdir.startswith('/') else workdir)
    os.makedirs(actual_workdir, exist_ok=True)

    try:
        # Run the command using the system shell, but inside the build directory
        subprocess.run(command, shell=True, cwd=actual_workdir, env=envp, check=True)
    except subprocess.CalledProcessError as e:
        print(f"RUN failed: {e}")
        sys.exit(1)