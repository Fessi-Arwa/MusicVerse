# MusicVerse — Your Personal Music Universe

MusicVerse est une application personnelle pour découvrir, organiser et mieux comprendre sa bibliothèque musicale. Elle réunit les chansons, les playlists, les favoris, les souvenirs associés à la musique et des statistiques sur ses goûts.

## Objectif du projet

Créer une petite application non triviale, utilisable par une personne et par un agent IA. L’agent pourra consulter la bibliothèque et proposer ou réaliser des actions musicales à partir des données de l’utilisateur.

## Fonctionnalités envisagées

- **Bibliothèque** : enregistrer des chansons avec leur titre, artiste, album, genres et humeur.
- **Recherche et filtres** : retrouver des chansons par titre, artiste, album, genre ou humeur.
- **Playlists** : créer et modifier des playlists personnalisées.
- **Favoris** : marquer et retrouver facilement ses chansons préférées.
- **Journal musical** : associer une chanson à un souvenir ou à une émotion.
- **Statistiques** : présenter les artistes et genres les plus présents dans la bibliothèque, ainsi que l’évolution des goûts.

## Utilisation par un agent IA

Une interface en ligne de commande donnera à l’agent accès aux mêmes opérations que l’application. L’agent pourra notamment :

- rechercher les chansons d’un artiste et filtrer la bibliothèque ;
- composer une playlist selon une humeur ;
- suggérer des chansons similaires à partir des artistes, genres et humeurs renseignés ;
- résumer les préférences musicales ;
- proposer de réorganiser une playlist selon un critère choisi.

Les suggestions s’appuieront d’abord sur les métadonnées de la bibliothèque, sans modèle de recommandation externe.

## Première version envisagée

Le périmètre initial est une bibliothèque locale avec des métadonnées saisies ou importées par l’utilisateur. La première version visera la gestion des chansons, des favoris et des playlists, la recherche, puis quelques statistiques simples. L’interface et la persistance seront choisies pendant la conception, en privilégiant une structure de données partagée entre l’application et la CLI.

L’écoute ou le téléchargement de musique, l’intégration à un service de streaming et le partage social ne font pas partie du périmètre initial.

## Plan de travail initial

1. Définir les données d’une chanson, d’une playlist et d’une entrée du journal musical.
2. Choisir l’interface et le stockage, puis préparer la structure du projet.
3. Implémenter la bibliothèque, la recherche, les favoris et les playlists.
4. Ajouter le journal musical et les premières statistiques.
5. Exposer les opérations principales dans la CLI pour l’agent.
6. Intégrer et documenter le parcours utilisateur, puis rédiger `report.md` sur le processus de développement.

Ce plan est une première proposition ; le périmètre et les choix techniques seront ajustés au fil du travail de l’équipe.

## Contraintes du mini-projet

- Projet réalisé en groupe de deux ou trois personnes.
- Code et développement suivis dans Git.
- Application au moins partiellement utilisable par un agent.
- Utilisation de Mistral Vibe et conservation des événements enregistrés dans `events/`.
- Cible indicative du cours : un projet assez conséquent pour commencer à passer à l’échelle (environ vingt fichiers de code et cinquante commits).
