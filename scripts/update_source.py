"""
Script pour mettre à jour les sources RSS vers des flux fiables
"""
from app import create_app, db
from app.models.source import Source
from app.models.category import Category
from datetime import datetime

# Liste des flux RSS fiables
RELIABLE_SOURCES = [
    # Le Monde
    {"name": "Le Monde - À la une", "url": "https://www.lemonde.fr/actualite-en-continu/rss_full.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "À la une"},
    {"name": "Le Monde - Économie", "url": "https://www.lemonde.fr/economie/rss.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Économie"},
    {"name": "Le Monde - International", "url": "https://www.lemonde.fr/international/rss.xml", "logo_url": "https://www.lemonde.fr/favicon.ico", "category_name": "Monde"},
    
    # Les Échos
    {"name": "Les Échos - À la une", "url": "https://www.lesechos.fr/rss/rss_une.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "À la une"},
    {"name": "Les Échos - Économie", "url": "https://www.lesechos.fr/rss/rss_economie.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Économie"},
    {"name": "Les Échos - Entreprises", "url": "https://www.lesechos.fr/rss/rss_entreprises.xml", "logo_url": "https://www.lesechos.fr/favicon.ico", "category_name": "Entreprise"},
    
    # Le Figaro
    {"name": "Le Figaro - À la une", "url": "https://www.lefigaro.fr/rss/figaro_actualites.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "À la une"},
    {"name": "Le Figaro - Économie", "url": "https://www.lefigaro.fr/rss/figaro_economie.xml", "logo_url": "https://www.lefigaro.fr/favicon.ico", "category_name": "Économie"},
    
    # L'Express
    {"name": "L'Express - À la une", "url": "https://www.lexpress.fr/rss/alaune.xml", "logo_url": "https://www.lexpress.fr/favicon.ico", "category_name": "À la une"},
    
    # France Info
    {"name": "France Info", "url": "https://www.francetvinfo.fr/titres.rss", "logo_url": "https://www.francetvinfo.fr/favicon.ico", "category_name": "À la une"}
]

def update_sources():
    """Met à jour les sources RSS avec des flux fiables"""
    app = create_app()
    
    with app.app_context():
        # Supprimer les sources existantes
        Source.query.delete()
        db.session.commit()
        print("Sources existantes supprimées")
        
        # Nombre de sources ajoutées
        added_count = 0
        
        # Ajouter les nouvelles sources
        for source_data in RELIABLE_SOURCES:
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
                print(f"Source ajoutée: {source_data['name']}")
            else:
                print(f"Catégorie non trouvée: {source_data['category_name']}")
        
        db.session.commit()
        print(f"Ajout de {added_count} sources RSS terminé.")

if __name__ == "__main__":
    print("Mise à jour des sources RSS...")
    update_sources()
    print("Mise à jour terminée.")