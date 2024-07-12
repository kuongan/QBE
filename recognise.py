import os
import logging
import numpy as np
from multiprocessing import current_process
from record import record_audio
from fingerprint import fingerprint_file, fingerprint_audio
from storage import store_song, get_matches, get_info_for_song_id, song_in_db
from pydub import AudioSegment
from pytube import YouTube
import eyed3

log = logging.getLogger(__name__)

KNOWN_EXTENSIONS = ["mp3", "wav"]

def get_youtube_id_from_filename(filename):
    """Extract youtube_id from filename {youtube_id}.mp3"""
    if filename.endswith(".mp3"):
        youtube_id = filename[:-4]  # Remove the .mp3 extension
        print("this is",youtube_id)
        return youtube_id
    return None

def get_youtube_title(youtube_id):
    """Get title from YouTube video using youtube_id."""
    try:
        url = f"https://www.youtube.com/watch?v={youtube_id}"
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        log.error(f"Error occurred while fetching metadata: {e}")
        return None

def get_song_info(filename):
    tube_id= os.path.basename(filename) 
    youtube_id = get_youtube_id_from_filename(tube_id)
    if youtube_id:
        title = get_youtube_title(youtube_id)
        if title:
            yt_id = os.path.basename(youtube_id)
            yt_id = str(yt_id)
            print((title, yt_id))
            return (title, yt_id)

def register_song(filename):
    """Register a single song.

    Checks if the song is already registered based on the path provided and ignores
    those that are already registered.

    :param filename: Path to the file to register
    """
    hashes = fingerprint_file(filename)
    print("done")
    song_info = get_song_info(filename)
    print("xong")
    logging.info(f"Writing {filename}")
    store_song(hashes, song_info)
    print("next")
    logging.info(f"Wrote {filename}")

def register_directory(path):
    """Recursively register songs in a directory.

    :param path: Path of directory to register
    """
    to_register = []
    for files in os.listdir(path):
        register_song(os.path.join(path,files))

def score_match(offsets):
    """Score a matched song.

    Calculates a histogram of the deltas between the time offsets of the hashes from the
    recorded sample and the time offsets of the hashes matched in the database for a song.
    The function then returns the size of the largest bin in this histogram as a score.

    :param offsets: List of offset pairs for matching hashes
    :returns: The highest peak in a histogram of time deltas
    :rtype: int
    """
    # Use bins spaced 0.5 seconds apart
    binwidth = 0.5
    tks = list(map(lambda x: x[0] - x[1], offsets))
    hist, _ = np.histogram(tks,
                           bins=np.arange(int(min(tks)),
                                          int(max(tks)) + binwidth + 1,
                                          binwidth))
    return np.max(hist)


def best_match(matches):
    """For a dictionary of song_id: offsets, returns the best song_id.

    Scores each song in the matches dictionary and then returns the song_id with the best score.

    :param matches: Dictionary of song_id to list of offset pairs (db_offset, sample_offset)
       as returned by :func:`~abracadabra.Storage.storage.get_matches`.
    :returns: song_id with the best score.
    :rtype: str
    """
    matched_song = None
    best_score = 0
    for song_id, offsets in matches.items():
        if len(offsets) < best_score:
            # can't be best score, avoid expensive histogram
            continue
        score = score_match(offsets)
        if score > best_score:
            best_score = score
            matched_song = song_id
    return matched_song


def recognise_song(filename):
    """Recognises a pre-recorded sample.

    Recognises the sample stored at the path ``filename``. The sample can be in any of the
    formats in :data:`recognise.KNOWN_FORMATS`.

    :param filename: Path of file to be recognised.
    :returns: :func:`~abracadabra.recognise.get_song_info` result for matched song or None.
    :rtype: tuple(str, str, str)
    """
    hashes = fingerprint_file(filename)
    matches = get_matches(hashes)
    matched_song = best_match(matches)
    info = get_info_for_song_id(matched_song)
    if info is not None:
        return info
    return matched_song


def listen_to_song(filename=None):
    """Recognises a song using the microphone.

    Optionally saves the sample recorded using the path provided for use in future tests.
    This function is good for one-off recognitions, to generate a full test suite, look
    into :func:`~abracadabra.record.gen_many_tests`.

    :param filename: The path to store the recorded sample (optional)
    :returns: :func:`~abracadabra.recognise.get_song_info` result for matched song or None.
    :rtype: tuple(str, str, str)
    """
    audio = record_audio(filename=filename)
    hashes = fingerprint_audio(audio)
    matches = get_matches(hashes)
    matched_song = best_match(matches)
    info = get_info_for_song_id(matched_song)
    if info is not None:
        return info
    return matched_song
