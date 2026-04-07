# Docksmith

A simplified Docker-like build and runtime system. Implements build caching, content-addressed layers, and process isolation. See the sample_app for a demo.

## Features
- Build images from Docksmithfile (FROM, COPY, RUN, WORKDIR, ENV, CMD)
- Deterministic build cache
- Content-addressed, immutable layers
- Linux process isolation (chroot/unshare)
- No daemon, all state in ~/.docksmith/

## Usage
See the sample_app directory for a demo Docksmithfile and app.
