from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session
from flask_login import login_required, current_user
import feedparser
from app.models.source import Source
from app.models.category import Category
from app.models.article import Article
from app.models.favorite import Favorite
from app.models.interaction import Interaction
from app.services.rss_direct_service import fetch_rss_feeds, get_categories
from datetime import datetime
import hashlib
from app import db
import sys
import json

direct_feed_bp = Blueprint('direct_feed', __name__)

@direct_feed_bp.route('/direct')
@login_required
def index():
    """Page principale pour les flux directs"""
    # Récupérer la catégorie demandée (si spécifiée)
    category_id = request.args.get('category', type=int)
    
    # Récupérer toutes les catégories pour le menu
    categories = get_categories()
    
    # Enregistrer l'interaction
    interaction = Interaction(
        user_id=current_user.id,
        interaction_type='visit_direct_feed',
        created_at=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()
    
    return render_template('feed/direct.html', 
                           category_id=category_id, 
                           categories=categories)

@direct_feed_bp.route('/api/direct-feed')
@login_required
def get_direct_feed():
    """API pour récupérer les flux RSS en direct"""
    category_id = request.args.get('category', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    print(f"API /api/direct-feed appelée - category_id={category_id}, limit={limit}")
    
    # Récupérer les articles en direct
    try:
        articles = fetch_rss_feeds(category_id, limit)
        print(f"API - {len(articles)} articles récupérés")
        
        # Vérifier quels articles sont en favoris
        favorites = get_user_favorites()
        favorite_urls = [fav.get('url') for fav in favorites]
        
        # Marquer les articles favoris
        for article in articles:
            article['is_favorite'] = article.get('url') in favorite_urls
        
        return jsonify({
            'articles': articles,
            'count': len(articles)
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERREUR dans /api/direct-feed: {e}")
        print(error_details)
        
        return jsonify({
            'articles': [],
            'count': 0,
            'error': str(e),
            'message': "Une erreur s'est produite lors de la récupération des articles"
        })

@direct_feed_bp.route('/direct/article')
@login_required
def view_direct_article():
    """Afficher un article direct via son URL"""
    article_url = request.args.get('url')
    source_name = request.args.get('source')
    title = request.args.get('title')
    
    if not article_url:
        return render_template('feed/article_not_found.html')
    
    # Vérifier si l'article est en favori
    favorites = get_user_favorites()
    is_favorite = any(fav.get('url') == article_url for fav in favorites)
    
    # Enregistrer l'interaction
    interaction = Interaction(
        user_id=current_user.id,
        interaction_type='view_direct',
        created_at=datetime.utcnow()
    )
    db.session.add(interaction)
    
    # Enregistrer dans l'historique des articles vus
    save_to_history(article_url, title, source_name)
    
    db.session.commit()
    
    return render_template('feed/direct_article.html', 
                           article_url=article_url,
                           source_name=source_name,
                           title=title,
                           is_favorite=is_favorite)

@direct_feed_bp.route('/api/direct-favorites/toggle', methods=['POST'])
@login_required
def toggle_direct_favorite():
    """API pour ajouter/supprimer un article direct des favoris"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'status': 'error', 'message': 'URL manquante'}), 400
    
    url = data.get('url')
    title = data.get('title', 'Sans titre')
    source = data.get('source', 'Source inconnue')
    summary = data.get('summary', '')
    
    # Vérifier si l'article est déjà en favori
    favorites = get_user_favorites()
    is_favorite = any(fav.get('url') == url for fav in favorites)
    
    if is_favorite:
        # Retirer des favoris
        remove_from_favorites(url)
        return jsonify({'status': 'removed', 'url': url})
    else:
        # Ajouter aux favoris
        article = {
            'url': url,
            'title': title,
            'source_name': source,
            'summary': summary,
            'date_added': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        add_to_favorites(article)
        return jsonify({'status': 'added', 'url': url})

@direct_feed_bp.route('/direct/favorites')
@login_required
def direct_favorites():
    """Page des favoris d'articles directs"""
    favorites = get_user_favorites()
    return render_template('feed/direct_favorites.html', favorites=favorites)

@direct_feed_bp.route('/direct/history')
@login_required
def direct_history():
    """Page d'historique des articles lus"""
    # Récupérer les articles récemment consultés
    recent_articles = get_user_history()
    return render_template('feed/direct_history.html', articles=recent_articles)

# Fonctions utilitaires pour gérer les favoris et l'historique

def get_user_favorites():
    """Récupère les favoris de l'utilisateur (BD + session)"""
    # Favoris stockés en session
    if 'direct_favorites' not in session:
        session['direct_favorites'] = []
        
    session_favorites = session.get('direct_favorites', [])
    
    # Récupérer également les favoris de la BD
    favorites_from_db = []
    try:
        # Récupérer les favoris de l'utilisateur
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        
        for favorite in favorites:
            article = Article.query.get(favorite.article_id)
            if article and article.url:
                favorites_from_db.append({
                    'url': article.url,
                    'title': article.title,
                    'source_name': article.source.name if article.source else 'Source inconnue',
                    'summary': article.summary or '',
                    'date_added': favorite.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
    except Exception as e:
        print(f"Erreur lors de la récupération des favoris depuis la BD: {e}")
    
    # Fusionner les deux listes (en évitant les doublons)
    all_favorites = favorites_from_db.copy()
    
    # Ajouter les favoris de session qui ne sont pas déjà dans la BD
    for session_fav in session_favorites:
        if not any(db_fav.get('url') == session_fav.get('url') for db_fav in favorites_from_db):
            all_favorites.append(session_fav)
    
    return all_favorites

def add_to_favorites(article):
    """Ajoute un article aux favoris (session + BD)"""
    # Ajouter à la session
    if 'direct_favorites' not in session:
        session['direct_favorites'] = []
    
    session_favorites = session.get('direct_favorites', [])
    
    # Vérifier si l'article existe déjà
    for i, fav in enumerate(session_favorites):
        if fav.get('url') == article.get('url'):
            # Remplacer l'article existant
            session_favorites[i] = article
            session['direct_favorites'] = session_favorites
            return
    
    # Ajouter l'article s'il n'existe pas
    session_favorites.append(article)
    session['direct_favorites'] = session_favorites
    
    # Synchroniser également avec la base de données
    sync_with_database(article)

def remove_from_favorites(url):
    """Supprime un article des favoris (session + BD)"""
    # Supprimer de la session
    if 'direct_favorites' in session:
        session_favorites = session.get('direct_favorites', [])
        session['direct_favorites'] = [fav for fav in session_favorites if fav.get('url') != url]
    
    # Supprimer également de la base de données
    remove_from_database(url)

def sync_with_database(article_data):
    """Synchronise un favori direct avec la base de données"""
    # Vérifier si un article correspondant existe déjà
    existing_article = Article.query.filter_by(url=article_data.get('url')).first()
    
    if not existing_article:
        try:
            # Trouver la première source et catégorie
            source = Source.query.first()
            category = Category.query.first()
            
            source_id = source.id if source else 1
            category_id = category.id if category else 1
            
            # Créer un article temporaire
            article = Article(
                title=article_data.get('title', 'Sans titre'),
                url=article_data.get('url', ''),
                summary=article_data.get('summary', ''),
                source_id=source_id,
                category_id=category_id,
                created_at=datetime.utcnow()
            )
            db.session.add(article)
            db.session.commit()
            
            existing_article = article
        except Exception as e:
            print(f"Erreur lors de la création de l'article: {e}")
            return
    
    # Vérifier si l'article est déjà en favori
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        article_id=existing_article.id
    ).first()
    
    if not existing_favorite:
        # Ajouter aux favoris
        favorite = Favorite(
            user_id=current_user.id,
            article_id=existing_article.id,
            created_at=datetime.utcnow()
        )
        db.session.add(favorite)
        db.session.commit()

def remove_from_database(url):
    """Supprime un favori direct de la base de données"""
    # Trouver l'article correspondant
    article = Article.query.filter_by(url=url).first()
    
    if article:
        # Supprimer le favori
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            article_id=article.id
        ).first()
        
        if favorite:
            db.session.delete(favorite)
            db.session.commit()

def save_to_history(url, title, source_name):
    """Sauvegarde un article direct dans l'historique"""
    # Créer un nouvel article si nécessaire
    existing_article = Article.query.filter_by(url=url).first()
    
    if not existing_article:
        try:
            # Trouver la première source et catégorie
            source = Source.query.first()
            category = Category.query.first()
            
            source_id = source.id if source else 1
            category_id = category.id if category else 1
            
            # Créer un article temporaire pour l'historique
            article = Article(
                title=title,
                url=url,
                summary="",
                source_id=source_id,
                category_id=category_id,
                created_at=datetime.utcnow()
            )
            db.session.add(article)
            db.session.commit()
            
            existing_article = article
        except Exception as e:
            print(f"Erreur lors de la création de l'article pour l'historique: {e}")
            return
    
    # Créer une interaction de type "read"
    interaction = Interaction(
        user_id=current_user.id,
        article_id=existing_article.id,
        interaction_type='read',
        created_at=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()

def get_user_history():
    """Récupère l'historique des articles lus par l'utilisateur"""
    # Récupérer les interactions de type "read"
    recent_interactions = Interaction.query.filter_by(
        user_id=current_user.id,
        interaction_type='read'
    ).order_by(
        Interaction.created_at.desc()
    ).limit(20).all()
    
    # Récupérer les articles correspondants
    articles = []
    for interaction in recent_interactions:
        article = Article.query.get(interaction.article_id)
        if article:
            # Récupérer la source
            source_name = "Source inconnue"
            if article.source_id:
                source = Source.query.get(article.source_id)
                if source:
                    source_name = source.name
            
            articles.append({
                'title': article.title,
                'url': article.url,
                'source_name': source_name,
                'summary': article.summary or '',
                'read_date': interaction.created_at.strftime('%d/%m/%Y %H:%M')
            })
    
    return articles