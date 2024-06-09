import sys
import logging
import argparse
import fun as f
import convert as c
import database as d
from database import conn
from analyze import spectrogram
import time
from sklearn.metrics import accuracy_score, classification_report

# INTERFACE DESIGN

parser = argparse.ArgumentParser(
    description='Freezam: process and identify audio files')
parser.add_argument('-v', '--version', action='version', version='Freezam 0.5 beta')
parser.add_argument("-vb", "--verbose", action="store_true", help="switch btw log levels")

# subcommands
subparsers = parser.add_subparsers(dest='subcommands')
# add
parser_add = subparsers.add_parser("add", help='add a song to database')
parser_add.add_argument('--pathfile', type=str, help='pathfile of the song')
# update (modify song info)
parser_update = subparsers.add_parser("update", help='update metadata of a song')
parser_update.add_argument('--title', type=str, help='song title')
parser_update.add_argument('--artist', type=str, help='song artist')
parser_update.add_argument('--album', type=str, help='song album')
# remove
parser_remove = subparsers.add_parser("remove", help='remove a song from database')
parser_remove.add_argument('--title', type=str, help='song title')
# construct (ingest an entire directory for database construction)
parser_fun = subparsers.add_parser("construct", help='construct database at 1-click')
# identify_snippet
parser_identify_snippet = subparsers.add_parser("identify_snippet", help='identify a snippet')
parser_identify_snippet.add_argument('--pathfile', type=str, help='pathfile of the snippet')
parser_identify_snippet.add_argument('--type', type=int, help='1 or 2 or 3, fingerprint method for identification')
#identify_dataset
parser_identify = subparsers.add_parser("identify_dataset", help='identify a snippet')
parser_identify.add_argument('--path', type=str, help='pathfile of folder')
parser_identify.add_argument('--lb', type=str, help='label file(csv)')
parser_identify.add_argument('--type', type=int, help='1 or 2, fingerprint method for identification')
# admin
parser_admin = subparsers.add_parser("admin", help='administrator mode. clean up database,etc.')
parser_admin.add_argument('--action', type=str, help='rm_dup - remove duplicates in database')
# list
parser_list = subparsers.add_parser("list", help='list all songs in database')

args = parser.parse_args()


# LOG SETUP

# set up logging to file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='shazam.log',
                    filemode='w')
# define a Handler which writes WARNING messages or higher to the sys.stderr
console = logging.StreamHandler(sys.stdout)
# set log level by verbose
if args.verbose:
    console.setLevel(logging.DEBUG)
else:
    console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger().addHandler(console)

log = logging.getLogger(__name__)


# MAIN FUNCTION

def main():
    """ execute the commands given in interface """

    # add
    if args.subcommands == "add":
        pathfile = args.pathfile
        f.add_single(conn, pathfile)

    # update
    if args.subcommands == "update":
        title = args.title
        if title is None:
            log.error('song title must be given for db search')
    # remove
    if args.subcommands == "remove":
        title = args.title
        d.drop_song(conn, title)
        log.info('song %s removed from database', title)

    # construct
    if args.subcommands == "construct":
        f.firststep(conn)

    # identify
    if args.subcommands == 'identify_snippet':
        pathfile = args.pathfile
        type = args.type
        start=time.time()
        if pathfile is None:
            log.error('expected a pathfile for "identify" command')
        else:
            if type == 1:
                # match by local peak
                title = f.identify1(conn, pathfile)
                if title ==[]:
                    print('No matched song found')
                else:
                    print('The best match is:', title)

            elif type == 2 or type is None:
                # match by maximum power per octave (default)
                title = f.identify2(conn, pathfile)
                if title ==[]:
                    print('No matched song found')
                else:
                    print('The best match is:', title)
            elif type == 3 or type is None:
                title1 = f.identify1(conn, pathfile)
                print("title1", title1)
                title2 = f.identify2(conn, pathfile)
                print("title2", title2)
                result =f.find_common_values(title1,title2)
                print(result)
                
            else:
                log.error('expected 1 or 2 for "type"')
        end =time.time()
        print("tổng thời gian là:", end-start)
    #dataset
    if args.subcommands == 'identify_dataset':
        pathfile = args.path
        label_file = args.lb  
        type = args.type
        start=time.time()
        if pathfile is None:
            log.error('expected a pathfile for "identify" command')
        else:
            true, predict = f.identify_data(pathfile, label_file,type)   
            accuracy = accuracy_score(true, predict)
            report = classification_report(true, predict, zero_division=1)
            print(report)
            print(f"Accuracy: {accuracy:.2f}")
                
    # admin
    if args.subcommands == 'admin':
        action = args.action
        if action == "rm_dup":
            # remove duplicates
            d.drop_duplicate(conn)
            log.info('all duplicates removed from database')
        else:
            log.error('action not recognized, please checkout "python interface.py admin -h" for available choices')

    # list
    if args.subcommands == 'list':
        titles = d.list_all_songs(conn)
        for title in titles:
            print(title)
        


# RUN
main()


# TEST INPUT
# python interface.py identify --pathfile="C:\Users\User\freezam\music\snippet\query.wav" --type=2