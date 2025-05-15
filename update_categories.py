# update_categories.py
import os
import sys

# Ajouter le répertoire courant au chemin Python pour pouvoir importer l'application
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importer l'application depuis run.py
from run import app
from app import db
from app.models.category import Category
from app.models.source import Source
from app.models.article import Article
from datetime import datetime

def run():
    """Exécute la mise à jour des catégories"""
    with app.app_context():
        print("Mise à jour des catégories...")
        
        # 1. Créer une catégorie par défaut si elle n'existe pas
        default_category = Category.query.filter_by(name="À la une").first()
        if not default_category:
            default_category = Category(
                name="À la une",
                description="Les actualités principales",
                created_at=datetime.utcnow()
            )
            db.session.add(default_category)
            db.session.commit()
            print("✅ Catégorie par défaut créée")
            
        # 2. Migrer tous les articles et sources vers la catégorie par défaut
        print("Migration des articles et sources vers la catégorie par défaut...")
        Article.query.update({Article.category_id: default_category.id})
        Source.query.update({Source.category_id: default_category.id})
        db.session.commit()
        
        # 3. Supprimer toutes les autres catégories
        print("Suppression des catégories obsolètes...")
        Category.query.filter(Category.id != default_category.id).delete()
        db.session.commit()
        
        # 4. Créer les nouvelles catégories
        new_categories = [
            # "À la une" existe déjà
            {"name": "Politique", "description": "Actualités politiques nationales et internationales"},
            {"name": "Économie", "description": "Économie, entreprises et marchés financiers"},
            {"name": "International", "description": "Actualités du monde entier"},
            {"name": "Société", "description": "Faits de société, éducation, santé"},
            {"name": "Tech & Numérique", "description": "Innovations technologiques, digital et médias"},
            {"name": "Culture", "description": "Arts, cinéma, musique et littérature"},
            {"name": "Sports", "description": "Actualités sportives"},
            {"name": "Sciences", "description": "Recherche, environnement et découvertes"}
        ]
        
        print("Création des nouvelles catégories...")
        for cat_data in new_categories:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                created_at=datetime.utcnow()
            )
            db.session.add(category)
        
        db.session.commit()
        print(f"✅ {len(new_categories)} nouvelles catégories créées")
        
        # 5. Mapping des sources vers les catégories
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
        
        # 6. Règles générales
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
        
        # 7. Mettre à jour les sources
        print("Association des sources aux catégories...")
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
        
        # 8. Mettre à jour les articles
        print("Mise à jour des articles...")
        articles = Article.query.all()
        updated_count = 0
        
        for article in articles:
            source = Source.query.get(article.source_id)
            if source:
                article.category_id = source.category_id
                updated_count += 1
        
        db.session.commit()
        print(f"✅ {updated_count} articles mis à jour")
        
        # 9. Ajouter nouvelles sources
        print("Ajout des nouvelles sources...")
        new_sources = [
            {"name": "Numerama", "url": "https://www.numerama.com/feed/", "logo_url": "https://www.numerama.com/favicon.ico", "category_name": "Tech & Numérique"},
            {"name": "01net - Actualités", "url": "https://www.01net.com/rss/info/flux-rss/flux-toutes-les-actualites/", "logo_url": "https://www.01net.com/favicon.ico", "category_name": "Tech & Numérique"},
            {"name": "01net - Tests", "url": "https://www.01net.com/rss/tests/flux-rss/flux-tous-les-tests/", "logo_url": "https://www.01net.com/favicon.ico", "category_name": "Tech & Numérique"},
            {"name": "Le Figaro - Actualités", "url": "https://www.lefigaro.fr/rss/figaro_actualites.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "À la une"},
            {"name": "Le Figaro - Économie", "url": "https://www.lefigaro.fr/rss/figaro_economie.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Économie"},
            {"name": "Le Figaro - Culture", "url": "https://www.lefigaro.fr/rss/figaro_culture.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Culture"},
            {"name": "Le Figaro - Sports", "url": "https://www.lefigaro.fr/rss/figaro_sport.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Sports"}
        ]
        
        added_count = 0
        for source_data in new_sources:
            # Vérifier si la source existe déjà
            existing = Source.query.filter_by(url=source_data["url"]).first()
            if not existing:
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
                    added_count += 1
        
        db.session.commit()
        print(f"✅ {added_count} nouvelles sources ajoutées")
        
        print("Mise à jour des catégories terminée avec succès !")

if __name__ == "__main__":
    run()