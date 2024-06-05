# RUN THIS PROGRAM TO:
# 1.create spectrogram
# 2.plot spectrogram
# 3.compute fingerprints (2 versions)
# 4.match two fingerprints

import numpy as np
import logging
from scipy import signal
from scipy.io import wavfile
from scipy.spatial import distance
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors


log = logging.getLogger(__name__)

import numpy as np

def spectrogram(pathfile):
    """Đọc một file WAV và tính toán spectrogram."""
    if not pathfile.endswith(".wav"):
        raise ValueError("Audio file must be in WAV format")

    try:
        # Đọc file WAV
        framerate, series = wavfile.read(pathfile)
        log.info("wav file processed")
        # Chuyển đổi âm thanh đa kênh thành âm thanh một kênh
        if series.ndim == 1:
            series = series  # Mono
        elif series.ndim == 2:
            series = np.mean(series, axis=1)  # Stereo
        else:
            raise ValueError("Audio file has an unsupported number of channels")


        # Tính toán spectrogram
        f, t, spect = signal.spectrogram(
            series,
            fs=framerate,
            nperseg=10*framerate,
            noverlap=(10-1)*framerate,
            window="hamming"
        )
        log.info("spectrogram computed")
        return framerate, f, t, spect

    except Exception as e:
        raise RuntimeError(f"Error processing WAV file: {e}")





def plot_spectrogram(f, t, spect):
    """plot a spectrogram"""
    # normalize the scale, make it easier to see the trends
    plt.pcolormesh(t, f, spect, norm=matplotlib.colors.Normalize(0,1))
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()



def fingerprint(f, spect):
    """compute fingerprint (ver.1) from spectrogram

    Option 4 in the instruction:
    find a list of (positive) frequencies f (scaled to [0, 1])
    at which the local periodogram has a peak
    """
    if np.max(spect) == 0:
        raise ValueError("Spectrogram contains only zeros")
    
    spect = spect / np.max(spect)  # Normalize the spectrogram
    
    peaks = np.argmax(spect, axis=0)
    
    if max(f) == 0:
        raise ValueError("Frequency array contains only zeros")
    
    max_f = max(f)
    fingerprints = f[peaks] / max_f
    log.info("fingerprint (ver.1) computed")

    return np.array(fingerprints)



def fingerprint2(f, spect, framerate):
    """compute fingerprint (ver.2) from spectrogram

    Option 5 in the instruction:
    find the maximum power per octave in local periodograms
    """
    # m = number of octaves
    # must have m>5 to cover middleC
    # larger m -> better precision
    m = 8
    min_f = int((2**-(m+1))*(framerate/2))
    fingerprints = []

    log.info("start to iterate through the spectrogram")

    # iterate through all octaves
    for k in range(m):
        start = min_f*(2**k)*10
        end = min_f*(2**(k+1))*10
        # take subset of spectrogram, slice each octave
        sub_f = f[start:end]
        sub_spect = spect[start:end]
        # compute fingerprint of each subset
        sub_fingerprint = fingerprint(sub_f, sub_spect)
        fingerprints.append(sub_fingerprint)
    # transpose to get fingerprint for each window
    fingerprints = np.array(fingerprints).T

    log.info("fingerprint (ver.2) computed")

    return fingerprints


def match_true(f1, f2):
    """compare two fingerprints (ver.1) and see if they match

    Params
    + f1 (num) - fingerprint stored in database, duration=10s
    + f2 (num) - fingerprint of a snippet, duration>=10s

    Return
    + boolean, True if match, False otherwise
    """
    # small tolerance -> better precision
    tolerance = 10**(-8)
    dist = (f1-f2)**2
    return dist < tolerance

def match(f1, f2):
    """compare two fingerprints (ver.1) and see if they match

    Params
    + f1 (num) - fingerprint stored in database, duration=10s
    + f2 (num) - fingerprint of a snippet, duration>=10s

    Return
    + boolean, True if match, False otherwise
    """
    # Calculate Euclidean distance between the two fingerprints
    tolerance = 10**(-5)
    dist = (f1-f2)**2
    return dist

# TEST OUTPUT

#pathfile = r"C:\Users\User\freezam\music\snippet\you.wav"
#framerate, f, t, spect = spectrogram(pathfile)
#plot_spectrogram(f, t, spect)
#fingerprint(f, spect)
#print(fingerprint2(f, spect, framerate))
def custom_euclidean(x, y):
    """Tính khoảng cách Euclidean giữa hai vectơ."""
    return np.sqrt(np.sum((x - y) ** 2))

def match3(f1, f2):
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
        dists = [custom_euclidean(x, y) for x, y in pairs]
        if all([(d < tolerance) for d in dists]):
            return True
        return False

    else:
        log.error("expected equal fingerprint lengths")

def match2(f1, f2):
    """compare two fingerprints (ver.2) and see if they match

    Params
    + f1 (array) - fingerprint stored in database, duration=10s
    + f2 (array) - fingerprint of a snippet, duration>=10s

    Return
    + boolean, True if match, False otherwise
    """
    if len(f1) == len(f2):
        pairs = zip(f1, f2)
        dists = [custom_euclidean(x, y) for x, y in pairs]
        return dists

    #else:
      #
      # log.error("expected equal fingerprint lengths")