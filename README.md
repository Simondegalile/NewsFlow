# NewsFlow

## 📰 Présentation du projet

NewsFlow est une application web de gestion de flux RSS permettant aux utilisateurs de suivre l'actualité de diverses sources françaises. Le projet offre une interface moderne et intuitive pour consulter, filtrer et sauvegarder des articles de presse dans un environnement personnalisé.

## ✨ Fonctionnalités principales

- **Agrégation de contenus** : Collection d'articles depuis divers flux RSS (Le Monde, Les Échos, etc.)
- **Catégorisation** : Organisation des articles par catégories thématiques (Économie, Politique, Tech, etc.)
- **Authentification** : Système de création de compte et connexion sécurisée
- **Favoris** : Possibilité de marquer des articles pour lecture ultérieure
- **Dashboard personnel** : Visualisation des statistiques d'utilisation et recommandations personnalisées
- **Suivi d'activité** : Enregistrement des interactions utilisateur pour améliorer les recommandations

## 🛠️ Technologies utilisées

- **Backend** : Flask (Python)
- **Base de données** : PostgreSQL avec SQLAlchemy ORM
- **Frontend** : HTML, Tailwind CSS, JavaScript
- **Authentification** : Flask-Login
- **Gestion des flux** : Feedparser
- **Migrations** : Flask-Migrate

## 🏗️ Architecture du projet

```
newsflow/
├── app/                            # Package principal
│   ├── models/                     # Modèles de données
│   │   ├── article.py              # Modèle Article
│   │   ├── category.py             # Modèle Catégorie
│   │   ├── favorite.py             # Modèle Favoris
│   │   ├── interaction.py          # Modèle Interactions utilisateur
│   │   ├── ...                     # Autres modèles
│   ├── routes/                     # Endpoints de l'application
│   │   ├── auth.py                 # Routes d'authentification
│   │   ├── dashboard.py            # Routes du tableau de bord
│   │   ├── favorite.py             # Routes des favoris
│   │   ├── feed.py                 # Routes du fil d'actualités
│   ├── services/                   # Services et utilitaires
│   │   ├── recommender.py          # Service de recommandation d'articles
│   │   ├── rss_service.py          # Service de récupération des flux RSS
│   ├── templates/                  # Templates HTML
│   │   ├── auth/                   # Templates d'authentification
│   │   ├── dashboard/              # Templates du tableau de bord
│   │   ├── feed/                   # Templates du fil d'actualités et articles
│   ├── __init__.py                 # Initialisation de l'application
├── requirements.txt                # Dépendances Python
├── .gitignore                      # Fichiers ignorés par git
├── run.py                          # Point d'entrée de l'application
└── test_db.py                      # Script de test de connexion à la base de données
```

## 📊 Modèle de données

- **User** : Informations utilisateur et authentification
- **Article** : Contenu des articles récupérés des flux RSS
- **Category** : Catégories thématiques des articles
- **Source** : Sources des flux RSS
- **Favorite** : Marqueurs d'articles favoris
- **Interaction** : Actions des utilisateurs (lectures, vues, etc.)
- **Keyword** : Mots-clés extraits des articles
- **UserCategoryPreference** : Préférences utilisateur par catégorie
- **UserKeywordPreference** : Préférences utilisateur par mot-clé

## ⚙️ Installation

### Prérequis
- Python 3.8+
- PostgreSQL
- Pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-nom/newsflow.git
   cd newsflow
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   
   Créez un fichier `.env` à la racine du projet avec les informations suivantes:
   ```
   SECRET_KEY=votre_clé_secrète
   DATABASE_URL=postgresql://utilisateur:mot_de_passe@hôte:port/nom_base_de_données
   ```

5. **Initialiser la base de données**
   ```bash
   flask init-db
   ```

6. **Récupérer les articles**
   ```bash
   flask update-rss
   ```

7. **Lancer l'application**
   ```bash
   flask run
   # ou
   python run.py
   ```

## 🔄 Maintenance

### Mise à jour des articles
Pour mettre à jour la base de données avec les derniers articles:
```bash
flask update-rss
```

### Migrations de base de données
Si vous modifiez les modèles, utilisez Flask-Migrate pour appliquer les changements:
```bash
flask db migrate -m "Description des changements"
flask db upgrade
```

## 🚀 Déploiement

L'application est configurée pour fonctionner sur divers environnements:

- **Développement** : Mode debug activé (`flask run --debug`)
- **Production** : Utilisez un serveur WSGI comme Gunicorn ou uWSGI

Pour le déploiement en production, assurez-vous de:
- Configurer correctement les variables d'environnement
- Utiliser une base de données PostgreSQL robuste
- Mettre en place un proxy inversé (Nginx, Apache)
- Configurer SSL pour HTTPS

## 🤝 Contribution

Les contributions sont les bienvenues! Pour contribuer:

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## 📧 Contact

Pour toute question ou suggestion, n'hésitez pas à me contacter [votre-email@example.com].
