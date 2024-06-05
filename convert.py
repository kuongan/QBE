# RUN THIS PROGRAM TO:
# 1.convert mp3 to wav
# 2.extract mp3 metadata

from pydub import AudioSegment
from pytube import YouTube
from analyze import spectrogram
import eyed3
import os
import logging

log = logging.getLogger(__name__)


import os
from pydub import AudioSegment

def convert(infile):
    """convert mp3 to wav
    Param: infile(str): a mp3 file, like "./music/mp3/_eij6Vs7FGo.mp3"
    Export: outfile: a wav file with the same name, like "./music/wav/_eij6Vs7FGo.wav"
    """
    try:
        # Lấy phần tên tệp từ đường dẫn đầy đủ
        filename = os.path.basename(infile)
        # Tạo đường dẫn đến thư mục đầu ra
        out_dir = os.path.join('./music', "wav")
        os.makedirs(out_dir, exist_ok=True)  # Tạo thư mục nếu nó không tồn tại
        # Tạo tên tệp đầu ra với phần mở rộng .wav
        outfile = os.path.join(out_dir, filename[:-3] + "wav")
        # Xuất file WAV
        sound = AudioSegment.from_mp3(infile)
        sound.export(outfile, format="wav")
        print("WAV file exported successfully:", outfile)
    except OSError as e:
        print("Error:", e)

def get_youtube_id_from_filename(filename):
    """Extract youtube_id from filename {youtube_id}.mp3"""
    if filename.endswith(".mp3"):
        youtube_id = filename[:-4]  # Remove the .mp3 extension
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


def get_file(filename):
    youtube_id = get_youtube_id_from_filename(filename)
    if youtube_id:
        title = get_youtube_title(youtube_id)
        if title:
            yt_id = os.path.basename(youtube_id)
            yt_id = str(yt_id)
            tup = (title,)
            print(tup)
            return tup, youtube_id
    else:
        raise ValueError("Could not extract YouTube ID or title.")
