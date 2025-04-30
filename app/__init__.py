from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-newsflow')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://newsflow_bdd1:votre_mot_de_passe@postgresql-newsflow.alwaysdata.net/newsflow_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation des extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    
    # Enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.feed import feed_bp
    from app.routes.favorite import favorite_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.direct_feed import direct_feed_bp  # Nouveau blueprint
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(direct_feed_bp)  # Enregistrement du nouveau blueprint
    
    # Commande pour initialiser la base de données
    @app.cli.command("init-db")
    def init_db():
        """Initialise la base de données avec les catégories et sources."""
        from app.models.category import Category
        from app.models.source import Source
        from datetime import datetime
        
        # Vérifier si les catégories existent déjà
        if Category.query.count() > 0:
            print("La base de données contient déjà des catégories.")
            return
            
        # Créer les catégories
        categories = [
            {"name": "À la une", "description": "Articles principaux du jour"},
            {"name": "Économie", "description": "Actualités économiques et financières"},
            {"name": "Politique", "description": "Actualités politiques nationales et internationales"},
            {"name": "Entreprise", "description": "Informations sur les entreprises et le monde des affaires"},
            {"name": "Finance et Marchés", "description": "Actualités des marchés financiers et de la bourse"},
            {"name": "Idées", "description": "Opinions, analyses et débats"},
            {"name": "Le Week-end", "description": "Articles de loisirs et de détente pour le week-end"},
            {"name": "Monde", "description": "Actualités internationales"},
            {"name": "Patrimoine", "description": "Conseils et informations sur la gestion de patrimoine"},
            {"name": "Régions", "description": "Actualités régionales et locales"},
            {"name": "Start-up", "description": "Innovations et entreprises en démarrage"},
            {"name": "Tech et Médias", "description": "Nouvelles technologies et actualités des médias"}
        ]
        
        for cat_data in categories:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                created_at=datetime.utcnow()
            )
            db.session.add(category)
        
        db.session.commit()
        print(f"Ajout de {len(categories)} catégories.")
        
        # Créer les sources RSS
        sources = [
            {"name": "Le Monde - À la une", "url": "https://www.lemonde.fr/rss/une.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "À la une"},
            {"name": "Les Échos - À la une", "url": "https://services.lesechos.fr/rss/les-echos-aujourd-hui.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "À la une"},
            {"name": "Les Échos - Économie", "url": "https://services.lesechos.fr/rss/les-echos-economie.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Les Échos - Politique", "url": "https://services.lesechos.fr/rss/les-echos-politique.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Politique"},
            {"name": "Les Échos - Entreprises", "url": "https://services.lesechos.fr/rss/les-echos-entreprises.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Entreprise"},
            {"name": "Les Échos - Finance et Marchés", "url": "https://services.lesechos.fr/rss/les-echos-finance-marches.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Finance et Marchés"},
            {"name": "Les Échos - Idées", "url": "https://services.lesechos.fr/rss/les-echos-idees.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Idées"},
            {"name": "Les Échos - Monde", "url": "https://services.lesechos.fr/rss/les-echos-monde.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Monde"},
            {"name": "Les Échos - Tech & Médias", "url": "https://services.lesechos.fr/rss/les-echos-tech-medias.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Tech et Médias"},
            {"name": "Le Monde - Économie", "url": "https://www.lemonde.fr/economie/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Le Monde - International", "url": "https://www.lemonde.fr/international/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Monde"},
            {"name": "Le Monde - Politique", "url": "https://www.lemonde.fr/politique/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Politique"}
        ]
        
        for source_data in sources:
            category = Category.query.filter_by(name=source_data["category_name"]).first()
            if category:
                source = Source(
                    name=source_data["name"],
                    url=source_data["url"],
                    logo_url=source_data["logo_url"],
                    category_id=category.id,
                    last_update=datetime.utcnow()
                )
                db.session.add(source)
        
        db.session.commit()
        print(f"Ajout de {len(sources)} sources RSS.")
        
        print("Base de données initialisée avec succès !")
    
    # Commande pour mettre à jour les flux RSS
    @app.cli.command("update-rss")
    def update_rss():
        """Met à jour les articles depuis les flux RSS."""
        from app.services.rss_direct_service import fetch_and_store_articles
        
        articles_count = fetch_and_store_articles()
        print(f"Ajout de {articles_count} nouveaux articles.")
    
    return app

# Import des modèles pour que Flask-Migrate les détecte
from app.models import user, article, category, source, favorite, interaction, keyword