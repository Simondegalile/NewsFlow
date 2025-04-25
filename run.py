from app import create_app
import os

# Débogage pour vérifier la configuration
print(f"URL de base de données utilisée: {os.environ.get('DATABASE_URL')}")



app = create_app()

if __name__ == '__main__':
    app.run(debug=True)





