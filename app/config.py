import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cle-secrete-par-defaut'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://newsflow_bdd1:votre_mot_de_passe@postgresql-newsflow.alwaysdata.net/newsflow_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False