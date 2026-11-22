"""Data models for MusicVerse."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Song:
    """Represents a song with all its metadata and statistics."""
    id: int
    titre: str
    artiste: str
    album: str
    duree: int  # Duration in seconds
    annee: int
    genre: str
    humeur: str
    is_favorite: bool = False
    ecoutes: int = 0
    derniere_ecoute: Optional[date] = None


@dataclass
class Playlist:
    """Represents a playlist."""
    id: int
    nom: str


@dataclass
class PlaylistSong:
    """Represents a song in a playlist with its position."""
    playlist_id: int
    song_id: int
    position: int = 0
