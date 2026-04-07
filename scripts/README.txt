# Importing a Base Image for Docksmith

1. Obtain a minimal Linux rootfs tarball (e.g., python:3.11, alpine, etc). You can use Docker to export a container rootfs, or download a prebuilt rootfs tarball.

2. Place the tarball somewhere accessible, e.g. `/tmp/python311-rootfs.tar`.

3. Run:

    python import_base_image.py /tmp/python311-rootfs.tar python:3.11

This will import the base image into `~/.docksmith/` for use in Docksmith builds.
