import scipy.io.wavfile as wavfile

# Đọc file audio
sample_rate, audio_samples = wavfile.read(r'C:\Users\User\freezam\d6pgocXnK8U.mp3')

# Lấy thông tin về mẫu tín hiệu
num_samples = len(audio_samples)
duration = num_samples / sample_rate  # Tính thời lượng tín hiệu (s)

# Kiểm tra số chiều của mảng mẫu âm thanh
if audio_samples.ndim == 1:
    audio_type = 'Mono'
elif audio_samples.ndim == 2:
    audio_type = 'Stereo'
else:
    audio_type = 'Unknown'

print(f'Sample rate: {sample_rate} Hz')
print(f'Number of samples: {num_samples}')
print(f'Duration: {duration:.2f} seconds')
print(f'Shape of audio samples array: {audio_samples.shape}')
print(f'Audio type: {audio_type}')
