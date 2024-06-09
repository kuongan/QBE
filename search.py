import logging
import fun as f
import convert as c
import database as d
from database import conn
from analyze import spectrogram
import analyze as a
import sys 
import time
import numpy as np
from sklearn.metrics import accuracy_score, classification_report

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

def remove_song(title):
    d.drop_song(conn, title)
    log.info('song %s removed from database', title)

def construct_database():
    f.firststep(conn)

def match(f1, f2):
    """compare two fingerprints (ver.1) and see if they match

    Params
    + f1 (num) - fingerprint stored in database, duration=10s
    + f2 (num) - fingerprint of a snippet, duration>=10s

    Return
    + boolean, True if match, False otherwise
    """
    # Calculate Euclidean distance between the two fingerprints
    tolerance = 10**(-8)
    dist = np.sum((f1 - f2)**2)
    if dist < tolerance:
        print(dist)
        return dist

def match2(f1, f2):
    """compare two fingerprints (ver.2) and see if they match

    Params
    + f1 (array) - fingerprint stored in database, duration=10s
    + f2 (array) - fingerprint of a snippet, duration>=10s

    Return
    + boolean, True if match, False otherwise
    """
    tolerance = 0.1

    if len(f1) == len(f2):
        pairs = zip(f1, f2)
        dists = [a.custom_euclidean(x, y) for x, y in pairs]
        if all([(d < tolerance) for d in dists]):
            return dists
    else:
        log.error("expected equal fingerprint lengths")

def identify1(conn, pathfile):
    """Identify a snippet (wav) with fingerprint ver.1."""
    
    # Bắt đầu tính thời gian
    start_time = time.time()
    
    # Đoạn mã của bạn ở đây
    _, f, _, spect = spectrogram(pathfile)
    f_snippet = a.fingerprint(f, spect)
    end_time = time.time()
    print("Thời gian tính fingerprint là:", end_time - start_time)
    # Bắt đầu tính thời gian tại đây
    start_matching_time = time.time()
    
    # Phần mã bạn đã cung cấp
    distances = []
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    for i in range(1, max_song_id+1):
        records = d.select_fingerprint1(conn, i)
        for f1 in records:
            dist = match(f1, f_snippet)
            if dist is not None:
                distances.append((i, dist))

    if distances:
        closest_indices = sorted(distances, key=lambda x: x[1])
        titlelist = []
        selected_ids = []  
        for song_id, _ in closest_indices:
            if song_id not in selected_ids:
                title = d.select_title(song_id, conn)
                titlelist.append(title)
                log.info('song title found for best match with song_id=%s', song_id)
                selected_ids.append(song_id)
                if len(titlelist) == 5:
                    break

        end_matching_time = time.time()
        print("Thời gian tìm kiếm là:", end_matching_time - start_matching_time)

        return titlelist
    else:
        return []

def identify2(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.2 """

    framerate, f, _, spect = spectrogram(pathfile)
    f_snippet = a.fingerprint2(f, spect, framerate)
    
    distances = []
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    for i in range(1, max_song_id+1):
        records = d.select_fingerprint2(conn, i)
        for f1 in records:
            f2 = f_snippet[0]
            dists = match2(f1, f2)
            if dists:
                distances.append((i, dists))

    if distances:
        closest_indices = sorted(distances, key=lambda x: x[1])[:10]
        titlelist = []
        selected_ids = []
        for song_id, _ in closest_indices:
            if song_id not in selected_ids:
                title = d.select_title(song_id, conn)
                titlelist.append(title)
                log.info('song title found for best match with song_id=%s', song_id)
                selected_ids.append(song_id)
                if len(titlelist) == 5:
                    break
        return titlelist
    else:
        return []

def identify_snippet(pathfile, type):
    start = time.time()
    if pathfile is None:
        log.error('expected a pathfile for "identify" command')
        return None
    else:
        if type == 1:
            titlelist,song_id = f.identify1(conn, pathfile)
            if not titlelist:
                return None
            return titlelist
        elif type == 2 or type is None:
            titlelist, song_id = f.identify2(conn, pathfile)
            if not titlelist:
                return None
            return titlelist
        elif type == 3:
            title1, song_id1 = f.identify1(conn, pathfile)
            print('tt', title1)
            title2, song_id2 = f.identify2(conn, pathfile)
            print('tt2', title2)
            titlelist = f.find_common_values(title1, title2)
            return [f'{titlelist}']
        else:
            log.error('expected 1 or 2 for "type"')
            return None
    end = time.time()
    print("tong thoi gian la:", end - start)

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
