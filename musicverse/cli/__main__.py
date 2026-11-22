"""MusicVerse CLI entry point.

Implements the following commands:
- search: Search songs by query
- create-playlist: Create playlist by mood
- similar: Find similar songs
- simulate-listens: Simulate song listens
- list: List songs (with --favorites option)
- stats: Show library statistics

All outputs are in JSON format.
"""
import argparse
import json
import sys
from datetime import date

from musicverse.core.database import init_db
from musicverse.core.services import (
    search_songs,
    create_playlist_by_mood,
    find_similar_songs,
    simulate_listens,
    get_favorites,
    get_all_songs_service,
    get_statistics,
)


def song_to_dict(song) -> dict:
    """Convert Song model to JSON-serializable dictionary."""
    return {
        "id": song.id,
        "titre": song.titre,
        "artiste": song.artiste,
        "album": song.album,
        "duree": song.duree,
        "annee": song.annee,
        "genre": song.genre,
        "humeur": song.humeur,
        "is_favorite": song.is_favorite,
        "ecoutes": song.ecoutes,
        "derniere_ecoute": song.derniere_ecoute
    }


def main():
    """Main entry point for MusicVerse CLI."""
    # Initialize database (loads demo data if empty)
    init_db()

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="MusicVerse CLI - Manage your music library"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ========== SEARCH ==========
    search_parser = subparsers.add_parser(
        "search",
        help="Search songs by titre, artiste, album, genre, or humeur"
    )
    search_parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Search term (partial match)"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of results to return"
    )

    # ========== CREATE-PLAYLIST ==========
    create_playlist_parser = subparsers.add_parser(
        "create-playlist",
        help="Create a playlist with all songs of a given mood"
    )
    create_playlist_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the playlist"
    )
    create_playlist_parser.add_argument(
        "--mood",
        type=str,
        required=True,
        help="Mood to filter songs by (e.g., 'Énergique', 'Calme')"
    )

    # ========== SIMILAR ==========
    similar_parser = subparsers.add_parser(
        "similar",
        help="Find songs similar to a given song (same genre or mood)"
    )
    similar_parser.add_argument(
        "--song-id",
        type=int,
        required=True,
        help="ID of the source song"
    )
    similar_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of similar songs to return (default: 3)"
    )

    # ========== SIMULATE-LISTENS ==========
    simulate_parser = subparsers.add_parser(
        "simulate-listens",
        help="Simulate listening to a song (increment écoutes counter)"
    )
    simulate_parser.add_argument(
        "--song-id",
        type=int,
        required=True,
        help="ID of the song"
    )
    simulate_parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of écoutes to add (default: 1)"
    )

    # ========== LIST ==========
    list_parser = subparsers.add_parser(
        "list",
        help="List songs from the library"
    )
    list_parser.add_argument(
        "--favorites",
        action="store_true",
        help="List only favorite songs"
    )

    # ========== STATS ==========
    subparsers.add_parser(
        "stats",
        help="Show library statistics (top artistes, genres, most listened song)"
    )

    # Parse arguments
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Execute command and output JSON
    result = None

    if args.command == "search":
        songs = search_songs(args.query, args.limit)
        result = [song_to_dict(s) for s in songs]

    elif args.command == "create-playlist":
        playlist = create_playlist_by_mood(args.name, args.mood)
        result = {"playlist_id": playlist.id, "nom": playlist.nom}

    elif args.command == "similar":
        songs = find_similar_songs(args.song_id, args.limit)
        result = [song_to_dict(s) for s in songs]

    elif args.command == "simulate-listens":
        simulate_listens(args.song_id, args.count)
        result = {"message": f"Added {args.count} écoutes to song {args.song_id}"}

    elif args.command == "list":
        if args.favorites:
            songs = get_favorites()
        else:
            songs = get_all_songs_service()
        result = [song_to_dict(s) for s in songs]

    elif args.command == "stats":
        result = get_statistics()

    # Output as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
