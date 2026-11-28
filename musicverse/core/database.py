"""SQLite database management for MusicVerse.

Handles database connection, initialization, and demo data loading.
"""
import json
import os
import sqlite3
from pathlib import Path

from .models import Song, Playlist, PlaylistSong


# Database path: MusicVerse/musicverse.db (at repository root)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(REPO_ROOT, "musicverse.db")

# Demo data path: musicverse/data/demo_songs.json (relative to package)
DEMO_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "demo_songs.json")


def get_db_connection():
    """Get a database connection with foreign keys enabled.
    
    Foreign keys are activated for each connection to ensure
    referential integrity (e.g., CASCADE deletes).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database: create tables and load demo data if empty.
    
    Creates the directory for the database file if it doesn't exist.
    Demo data is loaded ONLY if the songs table is empty.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY,
                titre TEXT NOT NULL,
                artiste TEXT NOT NULL,
                album TEXT,
                duree INTEGER,
                annee INTEGER,
                genre TEXT NOT NULL,
                humeur TEXT NOT NULL,
                is_favorite BOOLEAN DEFAULT FALSE,
                ecoutes INTEGER DEFAULT 0,
                derniere_ecoute TEXT,
                audio_file TEXT,
                cover_file TEXT,
                lyrics TEXT DEFAULT ''
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                position INTEGER DEFAULT 0,
                PRIMARY KEY (playlist_id, song_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
            )
        """)

        # Add optional local media fields to databases created by older versions.
        song_columns = {row["name"] for row in cursor.execute("PRAGMA table_info(songs)")}
        if "audio_file" not in song_columns:
            cursor.execute("ALTER TABLE songs ADD COLUMN audio_file TEXT")
        if "cover_file" not in song_columns:
            cursor.execute("ALTER TABLE songs ADD COLUMN cover_file TEXT")
        if "lyrics" not in song_columns:
            cursor.execute("ALTER TABLE songs ADD COLUMN lyrics TEXT DEFAULT ''")
        
        conn.commit()
        
        # Load demo data ONLY if songs table is empty
        cursor.execute("SELECT COUNT(*) FROM songs")
        if cursor.fetchone()[0] == 0:
            _load_demo_data(conn)


def _load_demo_data(conn):
    """Load demo songs from JSON file into the database.
    
    Demo data includes 20 songs with stable IDs (104-123) and fixed
    listen counts for reproducible statistics.
    """
    with open(DEMO_DATA_PATH, "r", encoding="utf-8") as f:
        demo_songs = json.load(f)
    
    cursor = conn.cursor()
    for song_data in demo_songs:
        cursor.execute("""
            INSERT INTO songs (id, titre, artiste, album, duree, annee, genre, humeur, is_favorite, ecoutes, derniere_ecoute)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            song_data["id"],
            song_data["titre"],
            song_data["artiste"],
            song_data["album"],
            song_data["duree"],
            song_data["annee"],
            song_data["genre"],
            song_data["humeur"],
            song_data.get("is_favorite", False),
            song_data.get("ecoutes", 0),
            song_data.get("derniere_ecoute")
        ))
    
    conn.commit()
