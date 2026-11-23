"""Flask routes for MusicVerse web interface.

Provides the Bibliothèque page with song listing, search, and favorite toggling.
Provides the Playlists page with playlist listing, creation, and details.
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from ..core.services import (
    get_all_songs_service,
    search_songs,
    toggle_favorite,
    get_all_playlists_service,
    create_playlist_by_mood,
    get_playlist_by_id,
    get_playlist_songs,
    get_unique_moods_service,
)

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
