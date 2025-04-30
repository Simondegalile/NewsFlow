"""
Script pour ajouter des sources RSS de test garanties fonctionnelles
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# Créer une mini application Flask pour accéder à la base de données
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://newsflow:B3cdakk2@postgresql-newsflow.alwaysdata.net/newsflow_bdd')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Définition des modèles minimaux
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    logo_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

# Flux RSS 100% fiables pour les tests
TEST_SOURCES = [
    # Flux officiels avec formats standardisés
    {"name": "France Info", "url": "https://www.francetvinfo.fr/titres.rss", "logo_url": "https://www.francetvinfo.fr/favicon.ico", "category_name": "À la une"},
    {"name": "Le Figaro Actualités", "url": "https://www.lefigaro.fr/rss/figaro_actualites.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "À la une"},
    {"name": "Le Figaro Économie", "url": "https://www.lefigaro.fr/rss/figaro_economie.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Économie"},
    {"name": "20 Minutes", "url": "https://www.20minutes.fr/feeds/rss-une.xml", "logo_url": "https://www.20minutes.fr/favicon.ico", "category_name": "À la une"},
    {"name": "L'Express", "url": "https://www.lexpress.fr/rss/alaune.xml", "logo_url": "https://www.lexpress.fr/favicon.ico", "category_name": "À la une"},
    
    # Flux sportifs (souvent très actifs et fiables)
    {"name": "L'Équipe", "url": "https://www.lequipe.fr/rss/actu_rss.xml", "logo_url": "https://www.lequipe.fr/favicon.ico", "category_name": "Le Week-end"},
    {"name": "RMC Sport", "url": "https://rmcsport.bfmtv.com/rss/football/", "logo_url": "https://rmcsport.bfmtv.com/favicon.ico", "category_name": "Le Week-end"},
    
    # Flux technologiques
    {"name": "01net", "url": "https://www.01net.com/actualites/feed/", "logo_url": "https://www.01net.com/favicon.ico", "category_name": "Tech et Médias"},
    {"name": "Numerama", "url": "https://www.numerama.com/feed/", "logo_url": "https://www.numerama.com/favicon.ico", "category_name": "Tech et Médias"},
    
    # Flux institutionnels
    {"name": "Service Public", "url": "https://www.service-public.fr/rss/fil-actu.xml", "logo_url": "https://www.service-public.fr/favicon.ico", "category_name": "Politique"}
]

def add_test_sources():
    """Ajoute des sources RSS de test garanties fonctionnelles"""
    with app.app_context():
        # Vérifier et ajouter chaque source
        added_count = 0
        
        for source_data in TEST_SOURCES:
            # Vérifier si la catégorie existe
            category = Category.query.filter_by(name=source_data["category_name"]).first()
            
            if not category:
                print(f"Catégorie '{source_data['category_name']}' non trouvée, création...")
                category = Category(
                    name=source_data["category_name"],
                    description=f"Catégorie {source_data['category_name']}"
                )
                db.session.add(category)
                db.session.commit()
                print(f"Catégorie '{source_data['category_name']}' créée avec ID {category.id}")
            
            # Vérifier si la source existe déjà
            existing_source = Source.query.filter_by(url=source_data["url"]).first()
            
            if existing_source:
                print(f"La source '{source_data['name']}' existe déjà")
                continue
            
            # Ajouter la source
            source = Source(
                name=source_data["name"],
                url=source_data["url"],
                logo_url=source_data["logo_url"],
                category_id=category.id,
                last_update=datetime.utcnow()
            )
            db.session.add(source)
            added_count += 1
            print(f"Source ajoutée: {source_data['name']}")
        
        db.session.commit()
        print(f"Ajout de {added_count} sources de test terminé.")

if __name__ == "__main__":
    print("⚡ Ajout de sources RSS de test...")
    add_test_sources()
    print("✅ Opération terminée.")