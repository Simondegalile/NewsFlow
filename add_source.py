#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour ajouter une nouvelle source RSS
"""

from app import create_app, db
from app.models.category import Category
from app.models.source import Source
from datetime import datetime
import argparse
import sys
import urllib.parse

app = create_app()

def get_domain(url):
    """Extrait le domaine d'une URL"""
    parsed_url = urllib.parse.urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def add_source(name, url, category_name, logo_url=None):
    """Ajoute une nouvelle source RSS"""
    with app.app_context():
        # Vérifier si la catégorie existe
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            print(f"Erreur: Catégorie '{category_name}' introuvable")
            print("Catégories disponibles:")
            categories = Category.query.all()
            for cat in categories:
                print(f"- {cat.name}")
            return False
        
        # Vérifier si la source existe déjà
        existing = Source.query.filter_by(url=url).first()
        if existing:
            print(f"Attention: Une source avec l'URL '{url}' existe déjà")
            print(f"Nom: {existing.name}")
            if existing.category_id:
                existing_category = Category.query.get(existing.category_id)
                print(f"Catégorie: {existing_category.name if existing_category else 'Inconnue'}")
                
            # Demander si l'utilisateur veut mettre à jour la source
            update = input("Voulez-vous mettre à jour cette source? (o/n): ").lower() == 'o'
            if update:
                existing.name = name
                existing.category_id = category.id
                if logo_url:
                    existing.logo_url = logo_url
                db.session.commit()
                print(f"Source '{name}' mise à jour avec succès")
                return True
            else:
                return False
        
        # Logo par défaut si non spécifié
        if not logo_url:
            domain = get_domain(url)
            logo_url = f"{domain}/favicon.ico"
        
        # Créer la nouvelle source
        source = Source(
            name=name,
            url=url,
            logo_url=logo_url,
            category_id=category.id,
            last_update=datetime.utcnow()
        )
        
        db.session.add(source)
        db.session.commit()
        print(f"Source '{name}' ajoutée avec succès à la catégorie '{category_name}'")
        return True

def list_categories():
    """Liste toutes les catégories disponibles"""
    with app.app_context():
        categories = Category.query.all()
        print("Catégories disponibles:")
        for cat in categories:
            print(f"- {cat.name}: {cat.description}")

def list_sources():
    """Liste toutes les sources par catégorie"""
    with app.app_context():
        categories = Category.query.all()
        print("Sources par catégorie:")
        
        for cat in categories:
            sources = Source.query.filter_by(category_id=cat.id).all()
            if sources:
                print(f"\n{cat.name} ({len(sources)} sources):")
                for source in sources:
                    print(f"  - {source.name}: {source.url}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gestion des sources RSS')
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Commande d'ajout
    add_parser = subparsers.add_parser('add', help='Ajouter une nouvelle source')
    add_parser.add_argument('--name', required=True, help='Nom de la source')
    add_parser.add_argument('--url', required=True, help='URL du flux RSS')
    add_parser.add_argument('--category', required=True, help='Nom de la catégorie')
    add_parser.add_argument('--logo', help='URL du logo (facultatif)')
    
    # Commande de listage des catégories
    list_cats_parser = subparsers.add_parser('list-categories', help='Lister les catégories disponibles')
    
    # Commande de listage des sources
    list_sources_parser = subparsers.add_parser('list-sources', help='Lister les sources par catégorie')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        if not add_source(args.name, args.url, args.category, args.logo):
            sys.exit(1)
    elif args.command == 'list-categories':
        list_categories()
    elif args.command == 'list-sources':
        list_sources()
    else:
        parser.print_help()