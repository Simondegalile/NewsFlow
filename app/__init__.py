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
            
        # Créer les catégories optimisées
        categories = [
            {"name": "À la une", "description": "Les actualités principales"},
            {"name": "Politique", "description": "Actualités politiques nationales et internationales"},
            {"name": "Économie", "description": "Économie, entreprises et marchés financiers"},
            {"name": "International", "description": "Actualités du monde entier"},
            {"name": "Société", "description": "Faits de société, éducation, santé"},
            {"name": "Tech & Numérique", "description": "Innovations technologiques, digital et médias"},
            {"name": "Culture", "description": "Arts, cinéma, musique et littérature"},
            {"name": "Sports", "description": "Actualités sportives"},
            {"name": "Sciences", "description": "Recherche, environnement et découvertes"}
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
            # Les Échos
            {"name": "Les Échos - À la une", "url": "https://services.lesechos.fr/rss/les-echos-aujourd-hui.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "À la une"},
            {"name": "Les Échos - Économie", "url": "https://services.lesechos.fr/rss/les-echos-economie.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Les Échos - Politique", "url": "https://services.lesechos.fr/rss/les-echos-politique.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Politique"},
            {"name": "Les Échos - Entreprises", "url": "https://services.lesechos.fr/rss/les-echos-entreprises.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Les Échos - Finance et Marchés", "url": "https://services.lesechos.fr/rss/les-echos-finance-marches.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Les Échos - Monde", "url": "https://services.lesechos.fr/rss/les-echos-monde.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "International"},
            {"name": "Les Échos - Tech & Médias", "url": "https://services.lesechos.fr/rss/les-echos-tech-medias.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Tech & Numérique"},
            
            # Le Monde
            {"name": "Le Monde - À la une", "url": "https://www.lemonde.fr/rss/une.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "À la une"},
            {"name": "Le Monde - Économie", "url": "https://www.lemonde.fr/economie/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Le Monde - International", "url": "https://www.lemonde.fr/international/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "International"},
            {"name": "Le Monde - Politique", "url": "https://www.lemonde.fr/politique/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Politique"},
            {"name": "Le Monde - Société", "url": "https://www.lemonde.fr/societe/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Société"},
            {"name": "Le Monde - Culture", "url": "https://www.lemonde.fr/culture/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Culture"},
            
            # France Info
            {"name": "France Info - Actualités", "url": "https://www.franceinfo.fr/videos.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "À la une"},
            {"name": "France Info - Monde", "url": "https://www.franceinfo.fr/monde.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "International"},
            {"name": "France Info - Politique", "url": "https://www.franceinfo.fr/politique.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "Politique"},
            {"name": "France Info - Économie", "url": "https://www.franceinfo.fr/economie.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "Économie"},
            {"name": "France Info - Culture", "url": "https://www.franceinfo.fr/culture.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "Culture"},
            {"name": "France Info - Sports", "url": "https://www.franceinfo.fr/sports.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "Sports"},
            {"name": "France Info - Sciences", "url": "https://www.franceinfo.fr/sciences.rss", "logo_url": "https://www.franceinfo.fr/favicon.ico", "category_name": "Sciences"},
            
            # Tech & Numérique
            {"name": "Numerama", "url": "https://www.numerama.com/feed/", "logo_url": "https://www.numerama.com/favicon.ico", "category_name": "Tech & Numérique"},
            {"name": "01net - Actualités", "url": "https://www.01net.com/rss/info/flux-rss/flux-toutes-les-actualites/", "logo_url": "https://www.01net.com/favicon.ico", "category_name": "Tech & Numérique"},
            {"name": "01net - Tests", "url": "https://www.01net.com/rss/tests/flux-rss/flux-tous-les-tests/", "logo_url": "https://www.01net.com/favicon.ico", "category_name": "Tech & Numérique"},
            
            # Autres sources
            {"name": "Le Figaro - Actualités", "url": "https://www.lefigaro.fr/rss/figaro_actualites.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "À la une"},
            {"name": "Le Figaro - Économie", "url": "https://www.lefigaro.fr/rss/figaro_economie.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Le Figaro - Culture", "url": "https://www.lefigaro.fr/rss/figaro_culture.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Culture"},
            {"name": "Le Figaro - Sports", "url": "https://www.lefigaro.fr/rss/figaro_sport.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Sports"}
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
        # Import à l'intérieur de la fonction pour éviter les problèmes d'importation circulaire
        from app.services.rss_service import fetch_and_store_articles
        
        articles_count = fetch_and_store_articles()
        print(f"Ajout de {articles_count} nouveaux articles.")
    
    # Commande pour réorganiser les catégories
    @app.cli.command("reorganize-categories")
    def reorganize_categories():
        """Réorganise les catégories existantes et reclasse les sources."""
        from app.models.category import Category
        from app.models.source import Source
        from app.models.article import Article
        from datetime import datetime
        
        print("Réorganisation des catégories...")
        
        # Catégorie par défaut (pour éviter les erreurs de contrainte)
        default_category = Category.query.filter_by(name="À la une").first()
        if not default_category:
            default_category = Category(
                name="À la une",
                description="Les actualités principales",
                created_at=datetime.utcnow()
            )
            db.session.add(default_category)
            db.session.commit()
        
        # Déplacer tous les articles et sources vers la catégorie par défaut
        Article.query.update({Article.category_id: default_category.id})
        Source.query.update({Source.category_id: default_category.id})
        db.session.commit()
        
        # Supprimer toutes les autres catégories
        Category.query.filter(Category.id != default_category.id).delete()
        db.session.commit()
        
        # Nouvelles catégories
        new_categories = [
            # Catégorie par défaut déjà créée
            {"name": "Politique", "description": "Actualités politiques nationales et internationales"},
            {"name": "Économie", "description": "Économie, entreprises et marchés financiers"},
            {"name": "International", "description": "Actualités du monde entier"},
            {"name": "Société", "description": "Faits de société, éducation, santé"},
            {"name": "Tech & Numérique", "description": "Innovations technologiques, digital et médias"},
            {"name": "Culture", "description": "Arts, cinéma, musique et littérature"},
            {"name": "Sports", "description": "Actualités sportives"},
            {"name": "Sciences", "description": "Recherche, environnement et découvertes"}
        ]
        
        # Créer les nouvelles catégories
        for cat_data in new_categories:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                created_at=datetime.utcnow()
            )
            db.session.add(category)
        
        db.session.commit()
        print(f"✅ Nouvelles catégories créées")
        
        # Définir les mappings de sources vers catégories
        source_category_mapping = {
            # Les Échos
            "Les Échos - À la une": "À la une",
            "Les Échos - Économie": "Économie",
            "Les Échos - Politique": "Politique",
            "Les Échos - Entreprises": "Économie",
            "Les Échos - Finance et Marchés": "Économie",
            "Les Échos - Idées": "Politique",
            "Les Échos - Monde": "International",
            "Les Échos - Tech & Médias": "Tech & Numérique",
            # Le Monde
            "Le Monde - À la une": "À la une",
            "Le Monde - Économie": "Économie",
            "Le Monde - International": "International",
            "Le Monde - Politique": "Politique",
            # France Info
            "France Info - Actualités": "À la une",
            "France Info - Monde": "International",
            "France Info - Économie": "Économie",
            "France Info - Politique": "Politique",
            "France Info - Culture": "Culture",
            "France Info - Sports": "Sports",
            "France Info - Sciences": "Sciences",
            # Tech & Numérique
            "Numerama": "Tech & Numérique",
            "01net": "Tech & Numérique",
            "01net - Actualités": "Tech & Numérique",
            "01net - Tests": "Tech & Numérique",
            # Le Figaro
            "Le Figaro - Actualités": "À la une",
            "Le Figaro - Économie": "Économie",
            "Le Figaro - Culture": "Culture",
            "Le Figaro - Sports": "Sports"
        }
        
        # Règles générales pour les sources sans mapping spécifique
        default_rules = {
            "économie": "Économie",
            "economie": "Économie",
            "eco": "Économie",
            "finance": "Économie",
            "politique": "Politique",
            "international": "International",
            "monde": "International",
            "tech": "Tech & Numérique",
            "numérique": "Tech & Numérique",
            "numerique": "Tech & Numérique",
            "culture": "Culture",
            "sport": "Sports",
            "science": "Sciences",
            "société": "Société",
            "societe": "Société"
        }
        
        # Mettre à jour les sources
        categories = {cat.name: cat for cat in Category.query.all()}
        sources = Source.query.all()
        
        for source in sources:
            # Utiliser le mapping direct
            if source.name in source_category_mapping:
                category_name = source_category_mapping[source.name]
            else:
                # Appliquer les règles générales
                source_name_lower = source.name.lower()
                category_name = "À la une"  # Catégorie par défaut
                
                for keyword, cat_name in default_rules.items():
                    if keyword in source_name_lower:
                        category_name = cat_name
                        break
            
            # Mettre à jour la source
            if category_name in categories:
                source.category_id = categories[category_name].id
                print(f"Source '{source.name}' → Catégorie '{category_name}'")
            else:
                # Fallback sur "À la une"
                source.category_id = categories["À la une"].id
                print(f"Source '{source.name}' → Catégorie 'À la une' (par défaut)")
        
        db.session.commit()
        print("✅ Sources mises à jour")
        
        # Mettre à jour les articles
        articles = Article.query.all()
        updated_count = 0
        
        for article in articles:
            source = Source.query.get(article.source_id)
            if source:
                article.category_id = source.category_id
                updated_count += 1
        
        db.session.commit()
        print(f"✅ {updated_count} articles mis à jour")
        
        print("Réorganisation des catégories terminée avec succès !")
    
    return app

# Import des modèles pour que Flask-Migrate les détecte
from app.models import user, article, category, source, favorite, interaction, keyword