#!/usr/bin/env python3
import sys
import argparse
from build_engine import build_image
from image import list_images, remove_image, load_image_manifest
from runtime import run_container

def main():
    parser = argparse.ArgumentParser(prog='docksmith', description='A simplified Docker-like build and runtime system')
    subparsers = parser.add_subparsers(dest='command')

    # build
    build_parser = subparsers.add_parser('build', help='Build an image from a Docksmithfile')
    build_parser.add_argument('-t', '--tag', required=True, help='Name:tag for the image')
    build_parser.add_argument('--no-cache', action='store_true', help='Disable build cache')
    build_parser.add_argument('context', help='Build context directory')

    # images
    images_parser = subparsers.add_parser('images', help='List images in the local store')

    # rmi
    rmi_parser = subparsers.add_parser('rmi', help='Remove an image')
    rmi_parser.add_argument('name_tag', help='Image name:tag to remove')

    # run
    run_parser = subparsers.add_parser('run', help='Run a container from an image')
    run_parser.add_argument('-e', action='append', default=[], help='Override environment variable (KEY=VALUE)')
    run_parser.add_argument('name_tag', help='Image name:tag to run')
    run_parser.add_argument('cmd', nargs=argparse.REMAINDER, help='Override CMD')

    args = parser.parse_args()

    if args.command == 'build':
        build_image(args.context, args.tag, args.no_cache)
    elif args.command == 'images':
        list_images()
    elif args.command == 'rmi':
        remove_image(args.name_tag)
    elif args.command == 'run':
        env_overrides = dict(e.split('=', 1) for e in args.e)
        run_container(args.name_tag, args.cmd, env_overrides)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
