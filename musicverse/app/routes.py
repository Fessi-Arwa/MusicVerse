"""Flask routes for MusicVerse web interface.

Provides the Bibliothèque page with song listing, search, and favorite toggling.
Provides the Playlists page with playlist listing, creation, and details.
"""
import os
from pathlib import Path
from urllib.parse import urlsplit

from flask import (
    Blueprint, abort, flash, jsonify, redirect, render_template, request,
    send_from_directory, url_for,
)
from ..core.database import REPO_ROOT
from ..core.services import (
    attach_song_cover,
    attach_song_audio,
    get_all_songs_service,
    get_song_by_id,
    search_songs,
    toggle_favorite,
    get_all_playlists_service,
    create_playlist_by_mood,
    get_playlist_by_id,
    get_playlist_songs,
    get_unique_moods_service,
    save_song_lyrics,
)

AUDIO_UPLOAD_DIR = os.path.join(REPO_ROOT, "musicverse_audio")
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".oga", ".opus", ".m4a", ".aac", ".flac", ".webm"}
AUDIO_MIME_TYPES = {
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
    ".oga": "audio/ogg", ".opus": "audio/ogg", ".m4a": "audio/mp4",
    ".aac": "audio/aac", ".flac": "audio/flac", ".webm": "audio/webm",
}
ALLOWED_COVER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Create the Bibliothèque blueprint
library_bp = Blueprint('library', __name__, url_prefix='/library',
                        template_folder='templates',
                        static_folder='static')


@library_bp.route('/')
def library():
    """Display the library page with all songs."""
    query = request.args.get('q', '')
    
    if query:
        songs = search_songs(query)
    else:
        songs = get_all_songs_service()
    
    return render_template('library.html', songs=songs, query=query)


@library_bp.route('/search')
def library_search():
    """Search endpoint - redirects to library with query parameter."""
    query = request.args.get('q', '')
    return redirect(url_for('library.library', q=query))


@library_bp.route('/toggle_favorite/<int:song_id>', methods=['POST'])
def toggle_favorite_route(song_id):
    """Toggle the favorite status of a song.
    
    Returns JSON with the new favorite status.
    """
    try:
        new_status = toggle_favorite(song_id)
        return jsonify({
            'success': True,
            'song_id': song_id,
            'is_favorite': new_status
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'An error occurred while toggling favorite'
        }), 500


@library_bp.route('/upload-audio/<int:song_id>', methods=['POST'])
def upload_song_audio(song_id):
    """Store a user's audio file locally and associate it with a song."""
    song = get_song_by_id(song_id)
    if song is None:
        abort(404)

    uploaded_file = request.files.get('audio_file')
    extension = Path(uploaded_file.filename or '').suffix.lower() if uploaded_file else ''
    if uploaded_file is None or not uploaded_file.filename:
        flash("Choisis d’abord un fichier audio.", "error")
        return _safe_audio_return()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        flash("Format audio accepté : MP3, WAV, OGG, OPUS, M4A, AAC, FLAC ou WEBM.", "error")
        return _safe_audio_return()

    os.makedirs(AUDIO_UPLOAD_DIR, exist_ok=True)
    audio_filename = f"{song_id}{extension}"
    target_path = os.path.join(AUDIO_UPLOAD_DIR, audio_filename)
    uploaded_file.save(target_path)
    attach_song_audio(song_id, audio_filename)

    if song.audio_file and song.audio_file != audio_filename:
        previous_path = os.path.join(AUDIO_UPLOAD_DIR, os.path.basename(song.audio_file))
        if os.path.isfile(previous_path):
            os.remove(previous_path)

    flash(f"Audio associé à « {song.titre} ». Tu peux maintenant le lancer.", "success")
    return _safe_audio_return()


@library_bp.route('/audio/<int:song_id>')
def serve_song_audio(song_id):
    """Stream an audio file previously uploaded for a song."""
    song = get_song_by_id(song_id)
    if song is None or not song.audio_file:
        abort(404)
    extension = Path(song.audio_file).suffix.lower()
    return send_from_directory(
        AUDIO_UPLOAD_DIR,
        os.path.basename(song.audio_file),
        mimetype=AUDIO_MIME_TYPES.get(extension, "application/octet-stream"),
        conditional=True,
    )


@library_bp.route('/upload-cover/<int:song_id>', methods=['POST'])
def upload_song_cover(song_id):
    """Store a user's album cover image locally."""
    song = get_song_by_id(song_id)
    if song is None:
        abort(404)

    uploaded_file = request.files.get('cover_file')
    extension = Path(uploaded_file.filename or '').suffix.lower() if uploaded_file else ''
    if uploaded_file is None or not uploaded_file.filename:
        flash("Choisis une image de pochette.", "error")
        return _safe_audio_return()
    if extension not in ALLOWED_COVER_EXTENSIONS:
        flash("Format de pochette accepté : JPG, PNG, WEBP ou GIF.", "error")
        return _safe_audio_return()

    os.makedirs(AUDIO_UPLOAD_DIR, exist_ok=True)
    cover_filename = f"cover-{song_id}{extension}"
    uploaded_file.save(os.path.join(AUDIO_UPLOAD_DIR, cover_filename))
    attach_song_cover(song_id, cover_filename)

    if song.cover_file and song.cover_file != cover_filename:
        previous_path = os.path.join(AUDIO_UPLOAD_DIR, os.path.basename(song.cover_file))
        if os.path.isfile(previous_path):
            os.remove(previous_path)

    flash(f"Pochette ajoutée à « {song.titre} ».", "success")
    return _safe_audio_return()


@library_bp.route('/cover/<int:song_id>')
def serve_song_cover(song_id):
    """Serve a cover image previously uploaded for a song."""
    song = get_song_by_id(song_id)
    if song is None or not song.cover_file:
        abort(404)
    extension = Path(song.cover_file).suffix.lower()
    mime_type = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}.get(extension)
    return send_from_directory(
        AUDIO_UPLOAD_DIR,
        os.path.basename(song.cover_file),
        mimetype=mime_type,
        conditional=True,
    )


@library_bp.route('/lyrics/<int:song_id>', methods=['POST'])
def update_song_lyrics(song_id):
    """Save lyrics supplied by the user for a song."""
    if get_song_by_id(song_id) is None:
        abort(404)
    lyrics = request.form.get('lyrics', '')
    try:
        save_song_lyrics(song_id, lyrics)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    return jsonify({"success": True})


def _safe_audio_return():
    """Redirect to an internal library or playlist page after an upload."""
    destination = request.form.get('return_to', '')
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith(('/library/', '/playlists/')):
        destination = url_for('library.library')
    return redirect(destination)


# Create the Playlists blueprint
playlists_bp = Blueprint('playlists', __name__, url_prefix='/playlists',
                         template_folder='templates',
                         static_folder='static')


@playlists_bp.route('/')
def list_playlists():
    """Display all playlists."""
    playlists = get_all_playlists_service()
    moods = get_unique_moods_service()
    # Get song count for each playlist
    playlists_with_count = []
    for playlist in playlists:
        songs = get_playlist_songs(playlist.id)
        playlists_with_count.append({
            'id': playlist.id,
            'nom': playlist.nom,
            'song_count': len(songs)
        })
    return render_template('playlists.html', playlists=playlists_with_count, moods=moods)


@playlists_bp.route('/create', methods=['GET', 'POST'])
def create_playlist():
    """Create a playlist from a mood."""
    moods = get_unique_moods_service()
    playlists = get_all_playlists_service()
    # Get song count for each playlist
    playlists_with_count = []
    for playlist in playlists:
        songs = get_playlist_songs(playlist.id)
        playlists_with_count.append({
            'id': playlist.id,
            'nom': playlist.nom,
            'song_count': len(songs)
        })
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mood = request.form.get('mood', '').strip()
        
        if not name or not mood:
            # Return to form with error and preserve data
            return render_template('playlists.html', 
                                 playlists=playlists_with_count,
                                 moods=moods,
                                 error='Le nom et l\'humeur sont requis')
        
        try:
            playlist = create_playlist_by_mood(name, mood)
            return redirect(url_for('playlists.view_playlist', playlist_id=playlist.id))
        except Exception as e:
            return render_template('playlists.html',
                                 playlists=playlists_with_count,
                                 moods=moods,
                                 error=f'Erreur lors de la creation: {str(e)}')
    
    # GET request - show creation form
    return render_template('playlists.html', playlists=playlists_with_count, moods=moods)


@playlists_bp.route('/<int:playlist_id>')
def view_playlist(playlist_id):
    """View the songs in a playlist."""
    playlist = get_playlist_by_id(playlist_id)
    if playlist is None:
        abort(404)
    
    songs = get_playlist_songs(playlist_id)
    return render_template('playlist_detail.html', playlist=playlist, songs=songs)
