import logging
import fun as f
import convert as c
import database as d
from database import conn
from analyze import spectrogram
import sys 


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='shazam.log',
                    filemode='w')
# define a Handler which writes WARNING messages or higher to the sys.stderr
console = logging.StreamHandler(sys.stdout)
# set log level by verbose
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger().addHandler(console)

log = logging.getLogger(__name__)
# MAIN FUNCTIONS

def add_song(pathfile):
    f.add_single(conn, pathfile)

def update_song(title):
    if title is None:
        log.error('song title must be given for db search')
    # Implement logic for updating song metadata

def remove_song(title):
    d.drop_song(conn, title)
    log.info('song %s removed from database', title)

def construct_database():
    f.firststep(conn)

def identify_snippet(pathfile, type):
    if pathfile is None:
        log.error('expected a pathfile for "identify" command')
    else:
        if type == 1:
            titlelist = f.identify1(conn, pathfile)
            return titlelist
            #for title in titlelist:
                #print('The best match is:', title)
        elif type == 2 or type is None:
            titlelist = f.identify2(conn, pathfile)
            for title in titlelist:
                print('The best match is:', title)
            return titlelist
        else:
            log.error('expected 1 or 2 for "type"')

def admin(action):
    if action == "rm_dup":
        d.drop_duplicate(conn)
        log.info('all duplicates removed from database')
    else:
        log.error('action not recognized, please checkout "python interface.py admin -h" for available choices')

def list_songs():
    titles = d.list_all_songs(conn)
    for title in titles:
        print(title)
    return titles
