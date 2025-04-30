"""
Script de diagnostic pour vérifier les sources RSS dans la base de données
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import feedparser

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
    last_update = db.Column(db.DateTime)
    
    category = db.relationship('Category', backref='sources')

def check_source(source):
    """Teste un flux RSS et affiche des informations"""
    print(f"Vérification de {source.name} ({source.url})")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    try:
        feed = feedparser.parse(source.url, request_headers={'User-Agent': user_agent})
        
        if hasattr(feed, 'status') and feed.status != 200:
            print(f"  ❌ Statut HTTP: {feed.status}")
            return False
            
        if not hasattr(feed, 'entries') or len(feed.entries) == 0:
            print("  ❌ Aucune entrée dans le flux RSS")
            return False
            
        print(f"  ✅ {len(feed.entries)} articles trouvés")
        
        # Afficher le premier article pour vérification
        if len(feed.entries) > 0:
            entry = feed.entries[0]
            print(f"  📰 Premier article: {entry.get('title', 'Sans titre')}")
            
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")
        return False

def check_all_sources():
    """Vérifie toutes les sources RSS dans la base de données"""
    with app.app_context():
        sources = Source.query.all()
        
        if not sources:
            print("❌ Aucune source trouvée dans la base de données!")
            return
            
        print(f"📊 {len(sources)} sources trouvées dans la base de données")
        
        # Compter les sources par catégorie
        category_counts = {}
        for source in sources:
            cat_name = source.category.name if source.category else "Sans catégorie"
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
        print("\n📋 Sources par catégorie:")
        for cat, count in category_counts.items():
            print(f"  - {cat}: {count}")
        
        # Tester quelques sources au hasard
        print("\n🔍 Test de quelques sources:")
        test_count = min(5, len(sources))
        success_count = 0
        
        for source in sources[:test_count]:
            if check_source(source):
                success_count += 1
        
        print(f"\n📈 Résultat: {success_count}/{test_count} sources fonctionnelles")
        
        if success_count == 0:
            print("\n⚠️ AUCUNE SOURCE NE FONCTIONNE! Vérifiez vos URLs.")
            print("Suggestions: ")
            print("1. Exécutez le script update_sources.py pour remettre à jour les sources")
            print("2. Assurez-vous que votre connexion internet fonctionne")
            print("3. Vérifiez que les URLs des flux RSS sont correctes et accessibles")

if __name__ == "__main__":
    print("🔎 Diagnostic des sources RSS...")
    check_all_sources()
    print("\nDiagnostic terminé.")
