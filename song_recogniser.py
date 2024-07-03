import os
import click
from storage import setup_db
from recognise import register_directory, listen_to_song, register_song, recognise_song
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Argument parsing
parser = argparse.ArgumentParser(
    description='Museek: process and identify audio files')

# Subcommands
subparsers = parser.add_subparsers(dest='subcommands')

# Register subcommand
parser_add = subparsers.add_parser("register", help="Register a song or a directory of songs")
parser_add.add_argument('--pathfile', type=str, help='pathfile of directory')

# Recognise subcommand
parser_add = subparsers.add_parser("recognise",  help="Use the microphone to listen for a song")
parser_add.add_argument('--listen', help='listen to song')
parser_add.add_argument('--pathfile', type=str, help='pathfile of snippet')

# Initialise subcommand
parser_add = subparsers.add_parser("initialise", help="Initialise DB")

args = parser.parse_args()


def register(path):
    """Register a song or a directory of songs."""
    if os.path.isdir(path):
        print("roi")
        register_directory(path)
    else:
        register_song(path)


def recognise(listen, path):
    """Recognise a song."""
    if listen == "true":
        result = listen_to_song()
    else:
        result = recognise_song(path)
    return result

def initialise():
    """Initialise the database."""
    setup_db()


def main():
    """Execute the commands given in interface."""
    try:
        # Register subcommand
        if args.subcommands == "register":
            pathfile = args.pathfile
            register(pathfile)

        # Recognise subcommand
        if args.subcommands == "recognise":
            listen = args.listen
            pathfile = args.pathfile
            result =recognise(listen,pathfile)
            print(result)

        # Initialise subcommand
        if args.subcommands == "initialise":
            initialise()

    except Exception as e:
        log.error(f"An error occurred: {e}")


# RUN
if __name__ == "__main__":
    main()
