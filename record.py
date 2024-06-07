import pyaudio
import wave
from time import time as time
import os


def RecordQuery(duration):
    
    # Audio settings
    sample_format = pyaudio.paInt16
    channels = 2  # Mono audio input
    sample_rate = 48000  # Standard sample rate (Hz)
    chunk_size = 1024  # Size of each audio chunk
    record_duration = duration  # Duration to record in seconds
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open an audio stream for input
    stream = p.open(format=sample_format,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size)

    # Create an empty list to store the audio frames
    frames = []

    print("Recording...")

    # Record audio for the specified duration
    start_time = time()
    while (time() - start_time) < record_duration:
        data = stream.read(chunk_size)
        frames.append(data)

    # Stop recording
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
        
    # Save the recorded data as a WAV file
    filename = "./music/snippet/query.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return filename

#RecordQuery(20)
