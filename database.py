# RUN THIS PROGRAM TO:
# construct database

# TODO:
# 1.fast search, hashing

import pyodbc
import os
from convert import get_youtube_title
from analyze import spectrogram
import numpy as np

# Thông tin kết nối
server = 'MSI\\KHUONGAN'  # Thay thế bằng tên máy chủ và tên instance của bạn
database = 'QBH'  # Thay thế bằng tên cơ sở dữ liệu của bạn

# Chuỗi kết nối
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

try:
    # Kết nối tới SQL Server
    conn = pyodbc.connect(connection_string)
    print("Kết nối thành công!")
except Exception as e:
    print("Lỗi khi kết nối tới SQL Server:", e)
 
# connect to database
#conn = psycopg2.connect(
#    host="sculptor.stat.cmu.edu",
#    database=DB_USER,
#    user=DB_USER,
#    password=DB_PASSWORD
#)

def test_connect(conn):
    """ check connection to postgresql """
    if conn.closed == 0:
        print('Connected to MySQL database')
    else:
        print('Unable to connect')


def create_table(conn):
    """ create two tables: music & fingerprint

    MUSIC
    + store song info (title, artist, album, etc.)
    + indicate whether a song is fingerprinted or not
    + fingerprinted default = 0, update when completed

    FINGERPRINT
    + store all info required for fingerprint (hash, windows, etc)
    + foreign key song_id to link two tables
    + delete a song in music = delete all same song_id in fingerprint

    JUSTIFICATION
    WHY TWO TABLES?
    + we'll mostly be working with fingerprint table (calc windows, etc)
    + no need to search song info every time
    HOW IT WORKS
    + do all the calc in fingerprint table
    + then link to music table for song info in last step
    """
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS fingerprint")
    cur.execute("DROP TABLE IF EXISTS music")

    cur.execute("""
        CREATE TABLE music (
            song_id INT IDENTITY(1,1) PRIMARY KEY,
            title VARCHAR(MAX) NOT NULL,
            address VARCHAR(MAX),
            url VARCHAR(MAX),
            fingerprinted INT DEFAULT 0
        )""")
    cur.execute("""
        CREATE TABLE fingerprint (
            sig_id INT IDENTITY(1,1) PRIMARY KEY,
            song_id INT,
            center INT,
            signature1 DECIMAL(6,5),
            signature2 VARCHAR(MAX) -- Store array as a string or consider a separate related table
        )""")
    # Adding the foreign key constraint separately to allow for ON DELETE CASCADE
    cur.execute("""
        ALTER TABLE fingerprint
        ADD CONSTRAINT FK_fingerprint_music
        FOREIGN KEY (song_id) REFERENCES music(song_id) ON DELETE CASCADE;
    """)

    conn.commit()
def show_tables(conn):
    try:
        # Lấy danh sách các bảng từ cơ sở dữ liệu
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        
        # In tên của các bảng
        tables = cursor.fetchall()
        print("Danh sách các bảng trong cơ sở dữ liệu:")
        for table in tables:
            print(table[0])
    except Exception as e:
        print("Lỗi khi hiển thị các bảng:", e)


def add_song_and_url(title, youtube_id, conn):
    try:
        # Ensure the input values are strings
        if not isinstance(title, str) or not isinstance(youtube_id, str):
            raise ValueError("Invalid input: title and youtube_id must be strings")
        parts = youtube_id.split("/")
        youtube_id = parts[-1]    
        # Construct the YouTube URL
        url = f"https://www.youtube.com/watch?v={youtube_id}"
        
        cur = conn.cursor()
        query = "INSERT INTO music (title, url) VALUES (?, ?)"
        
        # Execute the query with parameters passed as a tuple
        cur.execute(query, (title, url))
        conn.commit()
    except pyodbc.ProgrammingError as e:
        print(f"SQL Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def add_fingerprint(filename, t, fingerprints1, fingerprints2, conn):
    """Thêm các dấu vân tay (ver.1 & ver.2) của một bài hát vào cơ sở dữ liệu."""
    query = 'INSERT INTO fingerprint (song_id, center, signature1, signature2) VALUES (?,?,?,?)'
    song_id = select_songid(filename, conn)
    for i in range(len(t)):
        signature2_str = ', '.join(map(str, fingerprints2[i]))
        val = (song_id, t[i], fingerprints1[i], signature2_str)
        cur = conn.cursor()
        cur.execute(query, val)
        conn.commit()




def drop_song(title, conn):
    """ delete song from music """
    cur = conn.cursor()
    query = 'DELETE FROM music WHERE title = %s'
    cur.execute(query, (title,))
    conn.commit()


def drop_unfingerprinted(conn):
    """ delete unfingerprinted song from music """
    cur = conn.cursor()
    query = 'DELETE FROM music WHERE fingerprinted = 0'
    cur.execute(query)
    conn.commit()


def drop_duplicate(conn):
    """ delete duplicate rows from music """
    cur = conn.cursor()
    cur.execute(
        """DELETE FROM music a USING music b
        WHERE a.song_id > b.song_id
        AND a.title = b.title
        """)
    conn.commit()


def update_fingerprinted(song_id, conn):
    """ set fingerprinted = 1 when done """
    cur = conn.cursor()
    query = 'UPDATE music SET fingerprinted = 1 where song_id = ?'
    cur.execute(query, (song_id,))
    conn.commit()



def select_songid(filename, conn):
    """ return song_id of a song """
    cur = conn.cursor()
    query = 'SELECT song_id from music WHERE title = ?'  # Sử dụng '?' thay vì '%s' cho pyodbc
    # get rid of the suffix (.wav) in filename
    file_name= os.path.basename(filename)
    val = file_name[:-4]  # Đảm bảo val là một tuple với một phần tử
    cur.execute(query, (get_youtube_title(val)))
    # the output should be a single str
    records = cur.fetchall()
    print('hehe',records[0][0])
    # convert to str
    return records[0][0]


def select_title(song_id, conn):
    """ select song title by song id """
    cur = conn.cursor()
    query = 'SELECT title from music WHERE song_id =  ?'
    cur.execute(query, (song_id))
    records = cur.fetchall()
    return records[0][0]


def select_max_song_id(conn):
    """ select the maximum song_id (to loop over all songs) """
    cur = conn.cursor()
    cur.execute('SELECT MAX(song_id) from music')
    records = cur.fetchall()
    return records[0][0]


def select_fingerprint1(conn, song_id):
    """ select all fingerprints (ver.1) of a song """
    cur = conn.cursor()
    cur.execute('select signature1 from fingerprint where song_id= ?', (song_id))
    records = cur.fetchall()
     # convert decimal tuple to float num
    records = [float(elem[0]) for elem in records]
    return records


def select_fingerprint2(conn, song_id):
    """Select fingerprints (ver.2) of a song."""
    cur = conn.cursor()
    query = 'SELECT signature2 FROM fingerprint WHERE song_id = ?'
    cur.execute(query, (song_id,))
    records = cur.fetchall()
    
    # Chuyển đổi dữ liệu từ chuỗi sang số, bỏ qua nếu không thể chuyển đổi
    fingerprint_list = []
    for elem in records:
        fingerprint = elem[0].split(',')  # Tách các giá trị bằng dấu phẩy
        fingerprint = [float(val) for val in fingerprint if val.strip()]  # Chuyển đổi thành số, bỏ qua khoảng trắng
        fingerprint_list.append(fingerprint)
    return np.array(fingerprint_list)



def list_all_songs(conn):
    """ list all song titles in database """
    cur = conn.cursor()
    cur.execute('SELECT title from music')
    records = cur.fetchall()
    # convert tuple list to list of strings
    records = [ elem[0] for elem in records ]
    return records


def fast_search(conn):
    """ create Generalized Inverted Indexes (GIN) for fast search,
    good for searching k-nearest neighbors"""
    pass


# TRASH BELOW

# exact match
def search_match(sig, conn):
    """ search the database for matches, return song info accordingly

    USER GUIDE
    retrieve by: print(search_match.__doc__)

    TO PRINT SONG INFO
    records = search_match(sig, conn)[0]
    for row in records:
        print("title = ", row[0])
        print("artist = ", row[1])
        print("album = ", row[2])
        print("song_id = ", row[3])

    TO PRINT NUMBER OF MATCHES
    count = search_match(sig, conn)[1]
    print(count)
    """
    cur = conn.cursor()
    query = """SELECT a.title, a.song_id FROM music a
    INNER JOIN (SELECT song_id FROM fingerprint WHERE signature1 = %s) b
    ON a.song_id = b.song_id"""
    val = (sig,)
    cur.execute(query, val)
    # record song_id of all matches
    records = cur.fetchall()
    # count number of matches
    count = cur.rowcount

    return records, count
