# ❤ GO DOWN THE RABBIT HOLE! ❤
#
# DESCRIPTION
#
# This program integrates functions from other modules to:
# + create a database
# + import metadata
# + convert mp3 to wav
# + identify a snippet
# + used features: user interaction
#   (intro, prompt user input, inform user when completed)

# TODO: read from url


import os
import logging
import numpy as np
import analyze as a
import convert as c
import database as d
from database import conn
from analyze import spectrogram


log = logging.getLogger(__name__)

def firststep(conn):
    d.create_table(conn)
    log.info("database created")
    
    for file in os.listdir("./music/mp3"):
        if file.endswith(".mp3"):
            pathfile = "./music/mp3/" + file
            tup, yt_id = c.get_file(pathfile) # type: ignore
            d.add_song_and_url(tup[0], yt_id, conn)
            c.convert(pathfile)
    log.info('all metadata recorded in the database')
    log.info('all audio converted to wav')

    for file in os.listdir("./music/wav"):
        if file.endswith(".wav"):
            pathfile = "./music/wav/" + file
            framerate, f, t, spect = spectrogram(pathfile)
            fingerprints1 = a.fingerprint(f, spect)
            fingerprints2 = a.fingerprint2(f, spect, framerate)
            song_id = d.select_songid(file, conn)
            log.info('audio file no. %s recorded in the database', song_id)
            d.add_fingerprint(file, t, fingerprints1, fingerprints2, conn)
            d.update_fingerprinted(song_id, conn)
    
    print('Done! Please check out your database ❤')
def add_single(conn, pathfile):
    if pathfile.endswith(".mp3"):
        tup, yt_id = c.get_file(pathfile) # type: ignore
        d.add_song_and_url(tup[0], yt_id, conn)
        log.info('metadata recorded in the database')
        c.convert(pathfile)
        log.info('audio converted to wav')
        filename = os.path.basename(pathfile)
        pathwav = "./music/wav/" + filename[:-3] + "wav"
        framerate, f, t, spect = spectrogram(pathwav)
        fingerprints1 = a.fingerprint(f, spect)
        fingerprints2 = a.fingerprint2(f, spect, framerate)
        song_id = d.select_songid(filename, conn)
        log.info('audio file no. %s recorded in the database', song_id)
        d.add_fingerprint(filename, t, fingerprints1, fingerprints2, conn)
        d.update_fingerprinted(song_id, conn)
        
        print('Done!', filename, 'added to your database ❤')




def identify(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.1 """

    # read snippet and compute fingerprints
    _, f, _, spect = spectrogram(pathfile)
    f_snippet = a.fingerprint(f, spect)
    print(f_snippet)
    # create a list to store number of matches for each song
    match_count = []

    # iterate through all songs in database
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    print(max_song_id)
    for i in range(1, max_song_id+1):
        count = 0
        # get all fingerprints (ver.1) of the song
        records = d.select_fingerprint1(conn, i)
        # iterate through the fingerprints
        for f1 in records:
            for f2 in f_snippet:
                if a.match(f1, f2):
                    count += 1
        # record number of matches for each song
        match_count.append(count)
        print(match_count)

    # find the best match
    max_count = max(match_count)
    log.info("best match found")
    # find all song_ids of the best match(es)
    l_songid = [i+1 for i, j in enumerate(match_count) if j == max_count]
    # get the song titles
    titlelist = []
    for song_id in l_songid:
        title = d.select_title(song_id, conn)
        titlelist.append(title)
        log.info('song title found for best match with song_id=%s', song_id)

    return titlelist

def identify1(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.1 """

    # read snippet and compute fingerprints
    _, f, _, spect = spectrogram(pathfile)
    f_snippet = a.fingerprint(f, spect)
    print(f_snippet)
    # create a list to store distances for each song
    distances = []

    # iterate through all songs in database
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    print(max_song_id)
    for i in range(1, max_song_id+1):
        # get all fingerprints (ver.1) of the song
        records = d.select_fingerprint1(conn, i)
        # iterate through the fingerprints
        for f1 in records:
            dist = a.match(f1, f_snippet)
            distances.append((i, dist))

    if distances:  # Check if distances is not empty
        # sort distances and get the indices of the closest 10 songs
        closest_indices = sorted(distances, key=lambda x: x[1][0])

        # get the song titles of the closest 10 songs
        titlelist = []
        selected_ids = set()  # Set to keep track of selected song ids
        for song_id, _ in closest_indices:
            # If the song id is not in selected_ids, add its title to titlelist
            if song_id not in selected_ids:
                title = d.select_title(song_id, conn)
                titlelist.append(title)
                log.info('song title found for best match with song_id=%s', song_id)
                selected_ids.add(song_id)  # Add song_id to selected_ids
                # If we have already selected 10 different songs, break the loop
                if len(titlelist) == 15:
                    break

        return titlelist
    else:
        return []


def identify3(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.2 """

    # read snippet and compute fingerprints
    framerate, f, _, spect = spectrogram(pathfile)
    f_snippet = a.fingerprint2(f, spect, framerate)
    # create a list to store number of matches for each song
    match_count = []

    # iterate through all songs in database
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    print(max_song_id)
    for i in range(1, max_song_id+1):
        count = 0
        # get all fingerprints (ver.2) of the song
        records = d.select_fingerprint2(conn, i)
        # iterate through the fingerprints
        for f1 in records:
            # look at the first window (0-10s) of f2 only
            f2 = f_snippet[0]
            if a.match2(f1, f2):
                count += 1
        # record number of matches for each song
        match_count.append(count)
        print(match_count)

    # find the best match
    max_count = max(match_count)
    log.info("best match found")
    # find all song_ids of the best match(es)
    l_songid = [i+1 for i, j in enumerate(match_count) if j == max_count]
    # get the song titles
    titlelist = []
    for song_id in l_songid:
        title = d.select_title(song_id, conn)
        titlelist.append(title)
        log.info('song title found for best match with song_id=%s', song_id)

    return titlelist

def identify2(conn, pathfile):
    """ identify a snippet (wav) with fingerprint ver.2 """

    # read snippet and compute fingerprints
    framerate, f, _, spect = spectrogram(pathfile)
    f_snippet = a.fingerprint2(f, spect, framerate)
    # create a list to store distances for each song
    distances = []

    # iterate through all songs in database
    log.info("iterating through all songs in database")
    max_song_id = d.select_max_song_id(conn)
    print(max_song_id)
    for i in range(1, max_song_id+1):
        # get all fingerprints (ver.2) of the song
        records = d.select_fingerprint2(conn, i)
        # iterate through the fingerprints
        for f1 in records:
            f2 = f_snippet[0]
            dists = a.match2(f1, f2)
            distances.append((i, dists))

    if distances:  # Check if distances is not empty
        # sort distances and get the indices of the closest 10 songs
        closest_indices = sorted(distances, key=lambda x: x[1])[:10]

        # get the song titles of the closest 10 songs
        titlelist = []
        selected_ids = set()  # Set to keep track of selected song ids
        for song_id, _ in closest_indices:
            # If the song id is not in selected_ids, add its title to titlelist
            if song_id not in selected_ids:
                title = d.select_title(song_id, conn)
                titlelist.append(title)
                log.info('song title found for best match with song_id=%s', song_id)
                selected_ids.add(song_id)  # Add song_id to selected_ids
                # If we have already selected 10 different songs, break the loop
                if len(titlelist) == 10:
                    break

        return titlelist
    else:
        return []


# TEST OUTPUT
#identify2(conn, "./music/snippet/Track52.wav")


# UNUSED STUFF BELOW

def interact():
    """ interaction! """
    print("""
    Hi! Welcome to Freezam program!

    This program is able to read a snippet from
    your local directory, and identify the song for you!'

    Ready to go?

    'Features available:
    1.construct a library for reference
    2....
    """)
    opt = int(input('Please select an option above: '))

    if opt == 1:
        firststep(conn)
    elif opt == 2:
        print('Oops, the feature is in progress. See you in the next release!')
    else:
        print('Please enter a valid index')
        choice = str(input('Hit Q to quit or hit ANY OTHER KEY to try again:'))
        if choice == 'Q' or choice == 'q':
            print()
            print(' ~See ya~ ')
        else:
            interact()


def main():
    try:
        interact()
    except ValueError:
        print('Oops, please enter a valid index :(')
        choice = str(input('Hit Q to quit or hit ANY OTHER KEY to try again:'))
        if choice == 'Q' or choice == 'q':
            print()
            print(' ~See ya~ ')
        else:
            interact()