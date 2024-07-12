# MUSEEK: A Shazam-like Audio Recognition Algorithm

Audio fingerprinting and recognition algorithm implemented in Python. 

## Dependencies

**Software**
- `ffmpeg` for converting audio files to .wav format
- `SQL Server` for database construction

**Python packages**
- `pydub` a Python ffmpeg wrapper
- `eyed3` for reading mp3 metadata
- `numpy` for audio signals transformations
- `scipy` used in spectrogram and peak finding algorithms
- `matplotlib` used for spectrogram plots
- `pyodbc` a Python-SQL Server database adapter
- `Flask` 


# Installation Guide
## Clone the Project
- Open your terminal or command prompt.
- Navigate to the directory where you want to clone the project.
- Run the following command to clone the repository:
    git clone https://github.com/kuongan/QBE.git

## Install SQL Server

Download and install SQL Server from the official Microsoft website.
Follow the installation instructions provided on the website.
### Set Up the Database
- Open SQL Server Management Studio (SSMS).
- Connect to your SQL Server instance.
- Create new database "QBE"


## Install Dependencies
Run the following command to install the required dependencies:
```bash
pip install -r requirements.txt
```

## Description

This program has the following functionalities:

**Database construction**

This program allows you to build your own music database at 1-click! 
 
To get started, please copy your music files  into the /music/mp3 folder. 
Frist, you need to go to file storage.py and replace your server name.

Then run the following command in the terminal to construct database:
```
python song_recogniser.py --pathfile ./music/mp3
```

**Web demo**

run ``` python app.py``` and choose record mode or upload file mode to retrieval the snippet.



