# test_db.py
from app import create_app, db

app = create_app()

with app.app_context():
    try:
        # Exécuter une requête simple pour tester la connexion
        result = db.engine.execute("SELECT 1")
        print("Connexion à la base de données réussie!")
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")