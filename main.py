#!/usr/bin/env python3
import sys
import argparse
from build_engine import build_image
from image import list_images, remove_image, load_image_manifest, show_history
from runtime import run_container

def main():
    parser = argparse.ArgumentParser(
        prog='docksmith',
        description='A simplified Docker-like build and runtime system'
    )

    subparsers = parser.add_subparsers(dest='command')

    # ---------------- BUILD ----------------
    build_parser = subparsers.add_parser('build')
    build_parser.add_argument('-t', '--tag', required=True)
    build_parser.add_argument('--no-cache', action='store_true')
    build_parser.add_argument('context')

    # ---------------- RUN ----------------
    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('-e', action='append', default=[])
    run_parser.add_argument('name_tag')
    run_parser.add_argument('cmd', nargs=argparse.REMAINDER)

    # ---------------- IMAGES ----------------
    subparsers.add_parser('images')

    # ---------------- RMI ----------------
    rmi_parser = subparsers.add_parser('rmi')
    rmi_parser.add_argument('name_tag')

    # ---------------- HISTORY (NEW FEATURE) ----------------
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('name_tag')

    args = parser.parse_args()

    # ---------------- COMMAND HANDLING ----------------
    if args.command == 'build':
        build_image(args.context, args.tag, args.no_cache)

    elif args.command == 'run':
        env_overrides = dict(e.split('=', 1) for e in args.e)
        run_container(args.name_tag, args.cmd, env_overrides)

    elif args.command == 'images':
        list_images()

    elif args.command == 'rmi':
        remove_image(args.name_tag)

    elif args.command == 'history':
        show_history(args.name_tag)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
