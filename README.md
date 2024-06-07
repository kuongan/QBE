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
- Create new database "QBH"


## Install Dependencies
Run the following command to install the required dependencies:
```bash
pip install -r requirements.txt
```

đoạn này viết tiếng việt cho mấy ní dễ làm theo nhoa.

Tải hết thư viện mà tui import ik, mấy đoạn tải ffmpeg dễ lỗi lắm thì thử pip install ffmpeg.

Nếu nó hiện Requirement already satisfied gòi thì dô cmd, gõ where ffmpeg gòi lấy cái path đó dô chỗ sửa biến môi trường add vào.

Lỗi nữa chụp màn hình gửi lên group đi @@.

mở visual code lên, cd dô thưu mục mới clone xún á, mở terminal lên (ctrl+shift+`) gõ 

```
python interface.py construct
``
Đợi nó chạy xong thì ngủ 1 giấc đi.

gòi chạy python app.py là hiện cái web lên á ní.

Giờ ngồi code html, css đi.

## Description

This program has the following functionalities:

**Database construction**

This program allows you to build your own music database at 1-click! 
 
To get started, please copy your music files (preferably in mp3 format) into the freezam/music/mp3 folder. You'll notice that the folder already contains some pre-downloaded music files for testing purposes. Feel free to add or remove files in the folder. 
Frist, you need to go to file database.py and replace your server name.

Then run the following command in the terminal:

```bash
cd freezam
$python interface.py construct
```

The program will print a message when it is done.

**Database management**

Currently the program supports the following manipulations of database:

- add a song to database

```
python interface.py add [-h] [--pathfile PATHFILE]
```

- modify song info

```
python interface.py update [-h] [--title TITLE] [--artist ARTIST] [--album ALBUM]
```

- remove a song from database

```
python interface.py remove [-h] [--title TITLE]
```

- list all songs in database

```
python interface.py list [-h]
```

- check and remove duplicate entries (should run regularly for database maintenance)

```
python interface.py admin --action=rm_dup
```

- More to come...

**Identify a snippet**

```
python interface.py identify [-h] [--pathfile PATHFILE] --type=1
```
or
```
python interface.py identify [-h] [--pathfile PATHFILE] --type=2
```

This program implements two types of fingerprints for audio identification:

- `type=1` computes a signature from local periodograms using the peak positive frequency method.
- `type=2` computes a signature by finding the maximum power per octave in local periodograms.

For faster identification, choose `type=1`; for better precision, choose `type=2`. The default option is `type=2`.

**Logging**

This application writes a message for each action taken to a designated log file shazam.log. Warnings and error messages go to the log file but also to standard error. You can customize the log level by turning on the `-vb` (verbose) option, so that all log entries will be output to standard error as well as the log file. For example:

```
python interface.py -vb identify --pathfile="./music/snippet/Track54.wav" --type=2
```


## Example

```
cd freezam
# create music database
python interface.py -vb construct
# identify a snippet (pre-downloaded)
python interface.py -vb identify --pathfile="./music/snippet/Track54.wav" --type=2
```


## Running the tests

To run the automated tests for this application:

```
cd shazam
pytest -v test_shazam.py
```

