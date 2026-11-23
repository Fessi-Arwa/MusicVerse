"""Repository layer for MusicVerse.

Provides CRUD operations for the database.
All functions use database.py for connections.
"""
from typing import List, Optional
from .database import get_db_connection
from .models import Song, Playlist, PlaylistSong


def get_all_songs() -> List[Song]:
    """Get all songs from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs")
        rows = cursor.fetchall()
        return [
            Song(
                id=row["id"],
                titre=row["titre"],
                artiste=row["artiste"],
                album=row["album"],
                duree=row["duree"],
                annee=row["annee"],
                genre=row["genre"],
                humeur=row["humeur"],
                is_favorite=bool(row["is_favorite"]),
                ecoutes=row["ecoutes"],
                derniere_ecoute=row["derniere_ecoute"]
            )
            for row in rows
        ]


def get_song_by_id(song_id: int) -> Optional[Song]:
    """Get a song by its ID. Returns None if not found."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = cursor.fetchone()
        if row:
            return Song(
                id=row["id"],
                titre=row["titre"],
                artiste=row["artiste"],
                album=row["album"],
                duree=row["duree"],
                annee=row["annee"],
                genre=row["genre"],
                humeur=row["humeur"],
                is_favorite=bool(row["is_favorite"]),
                ecoutes=row["ecoutes"],
                derniere_ecoute=row["derniere_ecoute"]
            )
        return None


def search_songs(query: str, limit: Optional[int] = None) -> List[Song]:
    """Search songs by titre, artiste, album, genre, or humeur (partial match)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM songs
            WHERE titre LIKE ? OR artiste LIKE ? OR album LIKE ?
                   OR genre LIKE ? OR humeur LIKE ?
        """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        rows = cursor.fetchall()
        songs = [
            Song(
                id=row["id"],
                titre=row["titre"],
                artiste=row["artiste"],
                album=row["album"],
                duree=row["duree"],
                annee=row["annee"],
                genre=row["genre"],
                humeur=row["humeur"],
                is_favorite=bool(row["is_favorite"]),
                ecoutes=row["ecoutes"],
                derniere_ecoute=row["derniere_ecoute"]
            )
            for row in rows
        ]
        if limit:
            return songs[:limit]
        return songs


def get_favorite_songs() -> List[Song]:
    """Get all songs marked as favorites."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE is_favorite = 1")
        rows = cursor.fetchall()
        return [
            Song(
                id=row["id"],
                titre=row["titre"],
                artiste=row["artiste"],
                album=row["album"],
                duree=row["duree"],
                annee=row["annee"],
                genre=row["genre"],
                humeur=row["humeur"],
                is_favorite=True,
                ecoutes=row["ecoutes"],
                derniere_ecoute=row["derniere_ecoute"]
            )
            for row in rows
        ]


def toggle_favorite(song_id: int) -> bool:
    """Toggle the favorite status of a song. Returns the new status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_favorite FROM songs WHERE id = ?", (song_id,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Song with ID {song_id} not found")
        
        new_status = not bool(row["is_favorite"])
        cursor.execute(
            "UPDATE songs SET is_favorite = ? WHERE id = ?",
            (int(new_status), song_id)
        )
        conn.commit()
        return new_status


def create_playlist(name: str) -> Playlist:
    """Create a new playlist. Returns the created Playlist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlists (nom) VALUES (?)", (name,))
        playlist_id = cursor.lastrowid
        conn.commit()
        return Playlist(id=playlist_id, nom=name)


def get_all_playlists() -> List[Playlist]:
    """Get all playlists from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM playlists ORDER BY nom")
        rows = cursor.fetchall()
        return [
            Playlist(id=row["id"], nom=row["nom"])
            for row in rows
        ]


def get_unique_moods() -> List[str]:
    """Get all unique humeurs from the songs database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT humeur FROM songs ORDER BY humeur")
        rows = cursor.fetchall()
        return [row["humeur"] for row in rows]


def get_playlist_by_id(playlist_id: int) -> Optional[Playlist]:
    """Get a playlist by its ID. Returns None if not found."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
        row = cursor.fetchone()
        if row:
            return Playlist(id=row["id"], nom=row["nom"])
        return None


def get_playlist_songs(playlist_id: int) -> List[Song]:
    """Get all songs in a playlist, ordered by position."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.* FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = ?
            ORDER BY ps.position
        """, (playlist_id,))
        rows = cursor.fetchall()
        return [
            Song(
                id=row["id"],
                titre=row["titre"],
                artiste=row["artiste"],
                album=row["album"],
                duree=row["duree"],
                annee=row["annee"],
                genre=row["genre"],
                humeur=row["humeur"],
                is_favorite=bool(row["is_favorite"]),
                ecoutes=row["ecoutes"],
                derniere_ecoute=row["derniere_ecoute"]
            )
            for row in rows
        ]


def add_song_to_playlist(playlist_id: int, song_id: int, position: int = 0) -> None:
    """Add a song to a playlist at the specified position."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check if song already exists in playlist
        cursor.execute(
            "SELECT * FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
            (playlist_id, song_id)
        )
        if cursor.fetchone():
            # Update position if song already exists
            cursor.execute(
                "UPDATE playlist_songs SET position = ? WHERE playlist_id = ? AND song_id = ?",
                (position, playlist_id, song_id)
            )
        else:
            # Insert new entry
            cursor.execute(
                "INSERT INTO playlist_songs (playlist_id, song_id, position) VALUES (?, ?, ?)",
                (playlist_id, song_id, position)
            )
        conn.commit()


def remove_song_from_playlist(playlist_id: int, song_id: int) -> None:
    """Remove a song from a playlist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
            (playlist_id, song_id)
        )
        conn.commit()


def delete_playlist(playlist_id: int) -> None:
    """Delete a playlist (and its songs via CASCADE)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        conn.commit()


def update_song_ecoutes(song_id: int, count: int) -> None:
    """Increment the écoutes counter for a song by count."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE songs SET ecoutes = ecoutes + ?, derniere_ecoute = date('now') WHERE id = ?",
            (count, song_id)
        )
        conn.commit()


def get_songs_by_mood(mood: str) -> List[Song]:
    """Get all songs with a specific humeur."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE humeur = ?", (mood,))
        rows = cursor.fetchall()
        return [
            Song(
                id=row["id"],
                titre=row["titre"],
                artiste=row["artiste"],
                album=row["album"],
                duree=row["duree"],
                annee=row["annee"],
                genre=row["genre"],
                humeur=row["humeur"],
                is_favorite=bool(row["is_favorite"]),
                ecoutes=row["ecoutes"],
                derniere_ecoute=row["derniere_ecoute"]
            )
            for row in rows
        ]


def get_stats() -> dict:
    """Get statistics: top 3 artistes, top 3 genres, most listened song.
    
    Artists and genres are ranked by total écoutes (SUM), with stable ordering
    (alphabetical) in case of ties.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Top 3 artistes (par total d'écoutes)
        cursor.execute("""
            SELECT artiste, SUM(ecoutes) as total_ecoutes
            FROM songs
            GROUP BY artiste
            ORDER BY total_ecoutes DESC, artiste ASC
            LIMIT 3
        """)
        top_artistes = [{"artiste": row["artiste"], "total_ecoutes": row["total_ecoutes"]}
                        for row in cursor.fetchall()]
        
        # Top 3 genres (par total d'écoutes)
        cursor.execute("""
            SELECT genre, SUM(ecoutes) as total_ecoutes
            FROM songs
            GROUP BY genre
            ORDER BY total_ecoutes DESC, genre ASC
            LIMIT 3
        """)
        top_genres = [{"genre": row["genre"], "total_ecoutes": row["total_ecoutes"]}
                      for row in cursor.fetchall()]
        
        # Chanson la plus écoutée
        cursor.execute("""
            SELECT titre, artiste, ecoutes
            FROM songs
            ORDER BY ecoutes DESC, titre ASC
            LIMIT 1
        """)
        top_song = cursor.fetchone()
        most_listened = {
            "titre": top_song["titre"],
            "artiste": top_song["artiste"],
            "ecoutes": top_song["ecoutes"]
        } if top_song else None
        
        return {
            "top_artistes": top_artistes,
            "top_genres": top_genres,
            "most_listened": most_listened
        }
