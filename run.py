from app import create_app
import os
import sys

# Débogage pour vérifier la configuration
print(f"URL de base de données utilisée: {os.environ.get('DATABASE_URL')}")

# Ajouter le chemin courant à PYTHONPATH pour aider à résoudre les problèmes d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
print(f"Chemins d'importation Python: {sys.path}")

try:
    app = create_app()
    print("Application Flask créée avec succès!")
except Exception as e:
    print(f"Erreur lors de la création de l'application: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == '__main__':
    app.run(debug=True)