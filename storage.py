import uuid
import pyodbc
import os
from collections import defaultdict
import settings

# Logging setup
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Database connection settings
server = 'MSI\\KHUONGAN'  # Replace with your server and instance name
database = 'QBE'  # Replace with your database name

# Connection string
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# Create a single database connection and cursor
try:
    # Connect to SQL Server
    conn = pyodbc.connect(connection_string)
    print("Kết nối thành công!")
except Exception as e:
    print("Lỗi khi kết nối tới SQL Server:", e)
cursor = conn.cursor()

def setup_db():
    """Create the database and tables if they do not already exist."""
    cursor.execute("DROP TABLE IF EXISTS hash")
    cursor.execute("DROP TABLE IF EXISTS song_info")

    cursor.execute("""
    CREATE TABLE hash (
        hash bigint,
        offset REAL,
        song_id NVARCHAR(255)
    )
    """)
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='song_info' AND xtype='U')
    CREATE TABLE song_info (
        title NVARCHAR(255),
        youtube_id NVARCHAR(255),
        song_id NVARCHAR(255)
    )
    """)
    conn.commit()


def song_in_db(filename):
    """Check whether a path has already been registered.

    :param filename: The path to check.
    :returns: Whether the path exists in the database yet.
    :rtype: bool
    """
    song_id = str(uuid.uuid5(uuid.NAMESPACE_OID, filename).int)
    cursor.execute("SELECT * FROM song_info WHERE song_id=?", (song_id,))
    return cursor.fetchone() is not None

def store_song(hashes, song_info):
    """Register a song in the database.

    :param hashes: A list of tuples of the form (hash, time offset, song_id) as returned by
        :func:`~abracadabra.fingerprint.fingerprint_file`.
    :param song_info: A tuple of form (artist, album, title) describing the song.
    """
    if len(hashes) < 1:
        log.warning("No hashes provided for storing song.")
        return
    
    try:
        for hash_item in hashes:
            cursor.execute("INSERT INTO hash VALUES (?, ?, ?)", hash_item)
        insert_info = [i if i is not None else "Unknown" for i in song_info]
        cursor.execute("INSERT INTO song_info VALUES (?, ?, ?)", (*insert_info, hashes[0][2]))
        conn.commit()
        log.info("Song successfully stored in the database.")
    except pyodbc.Error as e:
        log.error(f"An error occurred while storing song: {e}")
        conn.rollback()
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        conn.rollback()


def get_matches(hashes, threshold=5):
    """Get matching songs for a set of hashes.

    :param hashes: A list of hashes as returned by
        :func:`~abracadabra.fingerprint.fingerprint_file`.
    :param threshold: Return songs that have more than ``threshold`` matches.
    :returns: A dictionary mapping ``song_id`` to a list of time offset tuples. The tuples are of
        the form (result offset, original hash offset).
    :rtype: dict(str: list(tuple(float, float)))
    """
    h_dict = {}
    for h, t, _ in hashes:
        h_dict[h] = t
    in_values = f"({','.join([str(h[0]) for h in hashes])})"
    cursor.execute(f"SELECT hash, offset, song_id FROM hash WHERE hash IN {in_values}")
    results = cursor.fetchall()
    result_dict = defaultdict(list)
    for r in results:
        result_dict[r[2]].append((r[1], h_dict[r[0]]))
    return result_dict

def get_info_for_song_id(song_id):
    """Lookup song information for a given ID."""
    cursor.execute("SELECT title FROM song_info WHERE song_id = ?", (song_id,))
    return cursor.fetchone()
