# MusicVerse — Your Personal Music Universe

MusicVerse est une application personnelle pour organiser et explorer sa bibliothèque musicale. Ce projet vise à créer une application simple mais complète, utilisable à la fois par un humain via une interface graphique et par un agent IA via une CLI.

## Objectif du projet

Créer une application non triviale avec :
- Une bibliothèque de **20 chansons de démonstration** (données fixes)
- Une **interface graphique simple** pour parcourir les chansons et les playlists
- Une **CLI utilisable par un agent IA**, avec sorties JSON

## Périmètre du MVP

### ✅ Fonctionnalités incluses
- **Bibliothèque** : 20 chansons avec métadonnées (`titre`, `artiste`, `album`, `durée`, `année`, `genre`, **`humeur`**).
- **Recherche** : par `titre`, `artiste`, `album`, `genre` ou **`humeur`** (recherche partielle).
- **Favoris** : marquer/démarquer des chansons (`is_favorite: true/false`).
- **Playlists** : créer, modifier, supprimer des playlists et gérer leurs chansons (ajout/suppression par ID).
- **Statistiques** : compteur d’`écoutes` (entier) et `dernière_écoute` (date). Les **valeurs sont fixes et reproductibles** (pas de génération aléatoire au lancement) et modifiables uniquement via `simulate-listens`.
- **Suggestions** : trouver des titres similaires (même `genre` **ou** même `humeur`).

### 🖥️ Interface
- **GUI** : interface graphique légère pour naviguer dans la bibliothèque et les playlists.
- **CLI** : interface en ligne de commande avec **sorties JSON**, partageant la même logique et les mêmes données que la GUI.

### ❌ Hors périmètre
- Lecture audio.
- Intégration avec des services de streaming (Spotify, Deezer, etc.).
- Journal musical.

## Utilisation par un agent IA

Une interface en ligne de commande donnera à l’agent accès aux principales fonctions de l’application. L’agent pourra notamment :

| Commande | Description |
|---|---|
| `musicverse search --query "terme"` | Recherche des chansons (titre, artiste, album, genre, humeur). |
| `musicverse create-playlist --name "Nom" --mood "humeur"` | Crée une playlist avec toutes les chansons d’une humeur donnée. |
| `musicverse similar --song-id ID --limit N` | Trouve N chansons similaires (même genre ou humeur). |
| `musicverse simulate-listens --song-id ID --count N` | Simule N écoutes pour une chanson (met à jour `écoutes` et `dernière_écoute`). |
| `musicverse list --favorites` | Liste les chansons marquées comme favorites. |
| `musicverse stats` | Affiche les statistiques (top 3 artistes, top 3 genres, chanson la plus écoutée). |

Les suggestions s’appuient **uniquement sur les métadonnées** (genre, humeur) de la bibliothèque.

## Étapes de réalisation
1. Définir la structure des données (chansons, playlists, favoris, statistiques).
2. Implémenter le stockage local (JSON ou autre format simple).
3. Développer le cœur métier : recherche, gestion des playlists/favoris, similarité, statistiques.
4. Créer la **GUI** pour la navigation dans la bibliothèque et les playlists.
5. Implémenter la **CLI** avec sorties JSON (elles partagent les mêmes données et le cœur métier).
6. Ajouter les **20 chansons de démonstration** (données fixes).
7. Tester avec les **3 scénarios de démonstration**. 
8. Documenter et finaliser.
9. Rédiger `report.md` sur le processus de développement.

## Scénarios de démonstration

### 1️⃣ Recherche et favoris
- **CLI** : `musicverse search --query "Calme"` → Affiche les chansons correspondantes.
- **GUI** : Marquer une chanson comme favorite.
- **CLI** : `musicverse list --favorites` → Vérifie que la chanson est bien dans les favoris.

### 2️⃣ Création de playlist par humeur
- **CLI** : `musicverse create-playlist --name "Déprime" --mood "Triste"` → Crée une playlist avec toutes les chansons d’humeur "Triste".
- **GUI** : Vérifier que la playlist "Déprime" contient bien les chansons attendues.

### 3️⃣ Titres similaires et statistiques
- **CLI** : `musicverse similar --song-id 123 --limit 3` → Affiche 3 chansons similaires (même genre/humeur).
- **CLI** : `musicverse simulate-listens --song-id 123 --count 5` → Met à jour les stats.
- **CLI** : `musicverse stats` → Affiche les tops (artistes, genres, chansons) mis à jour.

## Contraintes du mini-projet
- Projet réalisé en **groupe de deux ou trois personnes**. 
- Code et développement suivis dans Git.
- Application au moins partiellement utilisable par un agent.
- Utilisation de Mistral Vibe et conservation des événements enregistrés dans `events/`.
- Cible indicative du cours : un projet assez conséquent pour commencer à passer à l’échelle (environ vingt fichiers de code et cinquante commits).
