document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('player-overlay');
    const panel = document.getElementById('audio-dock');
    const player = document.getElementById('music-player');
    const title = document.getElementById('player-title');
    const artist = document.getElementById('player-artist');
    const album = document.getElementById('player-album');
    const cover = document.getElementById('player-cover');
    const coverPlaceholder = document.getElementById('player-cover-placeholder');
    const placeholderAlbum = document.getElementById('cover-placeholder-album');
    const coverForm = document.getElementById('cover-upload-form');
    const coverInput = document.getElementById('cover-file-input');
    const lyricsForm = document.getElementById('lyrics-form');
    const lyricsInput = document.getElementById('lyrics-input');
    const lyricsDisplay = document.getElementById('lyrics-display');
    const lyricsEmpty = document.getElementById('lyrics-empty');
    const lyricsStatus = document.getElementById('lyrics-status');
    const lyricsEditToggle = document.getElementById('lyrics-edit-toggle');
    const closeButton = document.getElementById('player-close');

    if (!overlay || !panel || !player) return;

    let lastPlayButton = null;

    const closePanel = () => {
        player.pause();
        overlay.hidden = true;
        if (lastPlayButton) lastPlayButton.focus();
    };

    document.querySelectorAll('.play-track-button').forEach(button => {
        button.addEventListener('click', async () => {
            lastPlayButton = button;
            overlay.hidden = false;
            panel.focus();
            title.textContent = button.dataset.title;
            artist.textContent = button.dataset.artist;
            album.textContent = button.dataset.album || 'Album non renseigné';
            placeholderAlbum.textContent = button.dataset.album || 'Pochette à ajouter';
            coverForm.action = button.dataset.coverUploadUrl;
            lyricsForm.action = button.dataset.lyricsUrl;
            lyricsInput.value = button.dataset.lyrics || '';
            lyricsStatus.textContent = '';
            lyricsForm.hidden = true;
            lyricsEditToggle.textContent = lyricsInput.value ? 'Modifier' : 'Ajouter';
            lyricsDisplay.textContent = lyricsInput.value;
            lyricsDisplay.hidden = !lyricsInput.value;
            lyricsEmpty.hidden = Boolean(lyricsInput.value);

            const coverUrl = button.dataset.coverUrl;
            if (coverUrl) {
                cover.src = coverUrl;
                cover.hidden = false;
                coverPlaceholder.hidden = true;
                cover.onerror = () => {
                    cover.hidden = true;
                    coverPlaceholder.hidden = false;
                };
            } else {
                cover.removeAttribute('src');
                cover.hidden = true;
                coverPlaceholder.hidden = false;
            }

            const nextUrl = button.dataset.audioUrl;
            if (player.dataset.audioUrl !== nextUrl) {
                player.dataset.audioUrl = nextUrl;
                player.src = nextUrl;
                player.load();
            }

            try {
                await player.play();
            } catch (error) {
                // The native controls remain available if autoplay is blocked.
                console.info('Clique sur Lecture dans le lecteur pour démarrer.', error);
            }
        });
    });

    closeButton.addEventListener('click', closePanel);
    overlay.addEventListener('click', event => {
        if (event.target === overlay) closePanel();
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !overlay.hidden) closePanel();
    });

    lyricsEditToggle.addEventListener('click', () => {
        lyricsForm.hidden = !lyricsForm.hidden;
        if (!lyricsForm.hidden) lyricsInput.focus();
    });

    lyricsForm.addEventListener('submit', async event => {
        event.preventDefault();
        lyricsStatus.textContent = 'Enregistrement…';
        try {
            const response = await fetch(lyricsForm.action, {
                method: 'POST',
                body: new FormData(lyricsForm),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || 'Impossible d’enregistrer les paroles.');
            const currentButton = lastPlayButton;
            currentButton.dataset.lyrics = lyricsInput.value;
            lyricsDisplay.textContent = lyricsInput.value;
            lyricsDisplay.hidden = !lyricsInput.value;
            lyricsEmpty.hidden = Boolean(lyricsInput.value);
            lyricsForm.hidden = true;
            lyricsEditToggle.textContent = lyricsInput.value ? 'Modifier' : 'Ajouter';
            lyricsStatus.textContent = 'Paroles enregistrées';
        } catch (error) {
            lyricsStatus.textContent = error.message;
        }
    });

    document.querySelectorAll('.audio-upload-form input[type="file"]').forEach(input => {
        input.addEventListener('change', () => {
            if (input.files.length && input.form.requestSubmit) input.form.requestSubmit();
            else if (input.files.length) input.form.submit();
        });
    });

    coverInput.addEventListener('change', () => {
        if (coverInput.files.length && coverForm.requestSubmit) coverForm.requestSubmit();
        else if (coverInput.files.length) coverForm.submit();
    });
});
