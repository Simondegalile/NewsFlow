Exécutez l'application :
bashflask --app run.py run

Utilisez les commandes Flask :
bash# Pour initialiser la base de données avec les nouvelles catégories
flask --app run.py init-db

# Pour mettre à jour les flux RSS
flask --app run.py update-rss

# Pour réorganiser les catégories existantes
flask --app run.py reorganize-categories

Si vous souhaitez créer ou mettre à jour les catégories manuellement :
bashflask --app run.py shell
Puis dans le shell:
pythonfrom app import db
from app.models.category import Category
from datetime import datetime

# Créer une nouvelle catégorie
tech_cat = Category(name="Tech & Numérique", description="Innovations technologiques et digital", created_at=datetime.utcnow())
db.session.add(tech_cat)
db.session.commit()