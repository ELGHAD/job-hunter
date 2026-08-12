

Readme · MD
# 🇲🇦 Job Hunter — Agrégateur d'Offres d'Emploi Intelligent
 
> Centralisez, classez et exportez les meilleures offres d'emploi du Maroc et d'ailleurs — en une seule recherche.
 
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/HTML5-Frontend-E34F26?logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/SerpAPI-Integration-4285F4" alt="SerpAPI">
  <img src="https://img.shields.io/badge/Status-Active-success" alt="Status">
  <img src="https://img.shields.io/badge/License-Not%20specified-lightgrey" alt="License">
</p>
---
 
## 📌 Aperçu du projet
 
**Job Hunter** est un outil d'agrégation d'offres d'emploi qui interroge simultanément plusieurs plateformes de recrutement (**LinkedIn, Bayt, Rekrute, Emploi.ma, Indeed, Glassdoor, Monster**) via l'API **SerpAPI**, puis **déduplique, classe et score** les résultats selon leur pertinence par rapport aux compétences recherchées. Conçu pour les chercheurs d'emploi — en particulier sur le marché marocain et MENA — il transforme une recherche multi-sites chronophage en un flux de travail centralisé, historisé en base de données et exportable en Excel.
 
Ce projet s'adresse aux **développeurs, candidats tech et professionnels en reconversion** souhaitant automatiser leur veille emploi plutôt que de parcourir manuellement chaque plateforme.
 
---
 
## ✨ Fonctionnalités clés
 
- 🔎 **Recherche multi-sources unifiée** : une seule requête interroge 7 plateformes (LinkedIn, Bayt, Rekrute, Emploi.ma, Indeed, Glassdoor, Monster) via Google Jobs API et des requêtes ciblées `site:`.
- 🧠 **Scoring de pertinence intelligent** : algorithme de classement basé sur la correspondance des mots-clés (titre vs description), la qualité de la source, la présence d'un salaire et la fraîcheur de l'annonce.
- 🧹 **Déduplication automatique** des offres provenant de sources multiples.
- 🗄️ **Historisation en base PostgreSQL** : chaque recherche est sauvegardée pour constituer une base d'opportunités dans le temps.
- 📊 **Export Excel formaté** : fichier `.xlsx` avec liens cliquables, code couleur selon la pertinence et une feuille de synthèse (stats par source, totaux, métadonnées).
- 🖥️ **Interface web légère** : frontend HTML/JS mono-page, sans dépendances lourdes.
- 🔌 **API REST simple** exposant recherche, export, historique et statistiques.
- ⏱️ **Automatisable** : compatible avec une exécution planifiée (cron) pour une veille quotidienne.
---
 
## 🏗️ Architecture & Stack Technique
 
| Composant | Technologie | Rôle |
|---|---|---|
| **Backend** | Python (Flask) | Serveur API REST (`app.py`) |
| **Scraping / Sourcing** | SerpAPI (Google Jobs API) | Récupération et scoring des offres (`scraper.py`) |
| **Base de données** | PostgreSQL | Persistance des offres et historique des recherches (`database.py`) |
| **Export** | openpyxl (implicite via `.xlsx`) | Génération de rapports Excel formatés (`excel_export.py`) |
| **Frontend** | HTML5 / JavaScript (SPA légère) | Interface utilisateur (`index.html`) |
| **Architecture logicielle** | API REST + séparation claire des responsabilités (scraping / persistance / export / présentation) | Modularité et maintenabilité |
 
### 🔑 Endpoints API principaux
 
| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/search` | Lancer une recherche d'offres |
| `POST` | `/api/export/excel` | Télécharger les résultats au format Excel |
| `GET` | `/api/history` | Récupérer l'historique des recherches |
| `GET` | `/api/stats` | Statistiques de la base de données |
| `GET` | `/health` | Vérification de l'état du service |
 
### 🗄️ Schéma de la base de données
 
```sql
jobs (
  id, title, company, location, source, url, description,
  salary, posted_at, work_type, relevance_score,
  keywords_matched, search_query, scraped_at
)
```
 
---
 
## 🚀 Guide d'installation & Démarrage rapide
 
### Prérequis
- Python 3.x
- PostgreSQL (optionnel mais recommandé)
- Une clé API [SerpAPI](https://serpapi.com) (plan gratuit : 100 recherches/mois)
### 1️⃣ Cloner le projet
```bash
git clone https://github.com/ELGHAD/job-hunter.git
cd job-hunter
```
 
### 2️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```
 
### 3️⃣ Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditez .env et renseignez votre SERPAPI_KEY
```
 
### 4️⃣ Configurer PostgreSQL (optionnel)
```sql
CREATE DATABASE jobhunter;
```
Renseignez ensuite `DATABASE_URL` dans le fichier `.env`. Les tables sont créées automatiquement au premier lancement.
 
### 5️⃣ Démarrer le backend
```bash
cd backend
python app.py
```
➡️ Le serveur démarre sur `http://localhost:5050`
 
### 6️⃣ Lancer le frontend
```bash
# Option A : ouvrir directement le fichier
open frontend/index.html
 
# Option B : servir via un serveur local
python -m http.server 3000 --directory frontend
# Puis ouvrez http://localhost:3000
```
 
---
 
## 📁 Structure du projet
 
```
job_hunter/
├── backend/
│   ├── app.py            # Serveur API Flask
│   ├── scraper.py        # Recherche SerpAPI + logique de scoring
│   ├── database.py       # Persistance PostgreSQL
│   └── excel_export.py   # Export Excel formaté
├── frontend/
│   └── index.html        # Interface utilisateur (SPA)
├── exports/               # Fichiers Excel générés
├── .env.example
├── requirements.txt
└── README.md
```
 
---
 
## ⚙️ Fonctionnement (résumé)
 
1. L'utilisateur saisit ses compétences/technologies (ex. `React, Node.js`).
2. Le scraper construit plusieurs requêtes SerpAPI : Google Jobs API (LinkedIn, Glassdoor, Indeed) + requêtes ciblées `site:bayt.com`, `site:rekrute.com`, `site:emploi.ma`.
3. Les résultats sont **dédupliqués** puis **classés** selon un score composite (mot-clé dans le titre vs description, qualité de la source, présence d'un salaire, fraîcheur de l'annonce).
4. Les offres sont **enregistrées en PostgreSQL** pour l'historique.
5. Export possible en **Excel formaté** avec code couleur selon la pertinence.
---
 
## 🔒 Sécurité & Bonnes pratiques
 
- **Gestion des secrets** via fichier `.env` (non versionné), clé SerpAPI isolée du code source.
- **Séparation des responsabilités** : logique de scraping, persistance et export découplées en modules distincts.
- **Persistance structurée** via PostgreSQL avec schéma de données explicite.
- **API REST stateless** facilitant les tests et l'intégration continue.
- **Configuration par environnement** (`.env.example` fourni) pour un déploiement reproductible.
> 💡 Pistes d'amélioration suggérées : ajout de tests automatisés, authentification sur les endpoints sensibles, et validation stricte des entrées côté API.
 
---
 
## 💡 Astuces d'utilisation
 
- Combinez plusieurs compétences séparées par des virgules pour élargir la recherche : `Python, Django, REST API`.
- Le **badge de score de pertinence** (0–15+) affiché sur chaque offre indique la qualité du match.
- Une bordure verte signale un score élevé (≥ 7) — à prioriser.
- Automatisez la recherche quotidienne via une tâche **cron** pour constituer une base d'opportunités dans le temps.
---
 
## 👤 Auteur & Contact
 
**ELGHAD**
- GitHub : [@ELGHAD](https://github.com/ELGHAD)
- Projet : [job-hunter](https://github.com/ELGHAD/job-hunter)
N'hésitez pas à ⭐ le dépôt si ce projet vous a été utile, à ouvrir une *issue* pour toute suggestion, ou à proposer une *pull request* !
 
---
 
<p align="center"><i>Développé avec 🇲🇦 passion pour simplifier la recherche d'emploi.</i></p>
 
