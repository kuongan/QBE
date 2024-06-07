import logging
import yt_dlp
import os

def download(youtube_url):
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Extract YouTube ID from the URL
    youtube_id = youtube_url.split('v=')[-1]
    output_file = f"./music/mp3/{youtube_id}.mp3"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'./music/mp3/{youtube_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        logging.info(f'Successfully downloaded and converted {youtube_id} to MP3')
        return f"{youtube_id}.mp3"
    except Exception as e:
        logging.error(f'Error downloading {youtube_id}: {str(e)}')
        return None

