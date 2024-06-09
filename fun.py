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

import time
import os
import logging
import numpy as np
import analyze as a
import convert as c 
import database as d
from database import conn
from analyze import spectrogram
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report


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
def add_single(conn, file):
    if file.endswith(".mp3"):
        pathfile = "./music/mp3/" + file
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
            dist = a.match(f1, f_snippet)
            distances.append((i, dist))

    if distances:
        closest_indices = sorted(distances, key=lambda x: x[1][0])
        titlelist = []
        selected_ids = []  
        for song_id, _ in closest_indices:
            if song_id not in selected_ids:
                title = d.select_title(song_id, conn)
                titlelist.append((title))
                log.info('song title found for best match with song_id=%s', song_id)
                selected_ids.append(song_id)
                if len(titlelist) == 5:
                    break

        end_matching_time = time.time()
        
        # Kết thúc tính thời gian tại đây
        print("Thời gian tìm kiếm là:", end_matching_time - start_matching_time)

        return titlelist, selected_ids
    else:
        return []

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
        selected_ids = []  # Set to keep track of selected song ids
        for song_id, _ in closest_indices:
            # If the song id is not in selected_ids, add its title to titlelist
            if song_id not in selected_ids:
                title = d.select_title(song_id, conn)
                titlelist.append((title))
                log.info('song title found for best match with song_id=%s', song_id)
                selected_ids.append(song_id)  # Add song_id to selected_ids
                # If we have already selected 10 different songs, break the loop
                if len(titlelist) == 5:
                    break

        return titlelist, selected_ids
    else:
        return []
def find_common_values(title1, title2):
    # Tạo các từ điển để lưu trữ độ quan trọng của các giá trị trong mỗi danh sách
    importance1 = {}
    importance2 = {}
    # Tính độ quan trọng cho mỗi giá trị trong danh sách 1
    for idx, value in enumerate(title1):
        print(idx, type(idx))
        importance1[value] = 5-idx    
    # Tính độ quan trọng cho mỗi giá trị trong danh sách 2
    for idx, value in enumerate(title2):
        print(idx, type(idx))
        importance2[value] = 5-idx 
    # Tạo danh sách để lưu trữ tất cả các giá trị
    all_values = set(title1) | set(title2)

    
    # Tạo danh sách để lưu trữ kết quả
    result = []
    
    # Tính tổng độ quan trọng của mỗi giá trị
    for value in all_values:
        score = importance1.get(value, 0) + importance2.get(value, 0)
        result.append((value, score))
    
    # Sắp xếp kết quả theo điểm số giảm dần
    result.sort(key=lambda x: x[1], reverse=True)
    # Trả về giá trị có điểm số cao nhất
    if result:
        return result[0][0]
    else:
        return None



def identify_data(path, label_file, type = 2):
    true = []
    predict =[]
    df = pd.read_csv(label_file)
    print("hahaha")
    filenames = df['filename'].tolist()
    print(df.columns)
    for file in os.listdir(path):
        if file in filenames:
            full_path = os.path.join(path, file)
            if type ==1:
                titlelist, selected_ids = identify1(conn, full_path)
            else:
                titlelist, selected_ids = identify2(conn, full_path)
            if titlelist and selected_ids:
                true_song_id = df.loc[df['filename'] == file].values[0]                
                true.append(true_song_id[0])  
                predict.append(selected_ids[0])
                print(f"{file}, '{titlelist[0]}'")
            else:
                print('No title found')
        else:
            print('help')
    return np.array(true), np.array(predict)

# Assuming conn and identify1 are already defined
path = r'C:\Users\User\freezam\music\snippet\test'
label_file = r'C:\Users\User\freezam\test.csv'

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