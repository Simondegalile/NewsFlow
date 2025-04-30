from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.article import Article
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.interaction import Interaction
from app.models.source import Source
from datetime import datetime
import os
import subprocess
import sys

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/')
@feed_bp.route('/feed')
@login_required
def index():
    # Récupérer la catégorie demandée (si spécifiée)
    category_id = request.args.get('category', type=int)
    
    # Récupérer toutes les catégories pour le menu
    categories = Category.query.all()
    
    # Enregistrer l'interaction
    interaction = Interaction(
        user_id=current_user.id,
        interaction_type='visit_feed',
        created_at=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()
    
    # Récupérer les articles
    articles_query = Article.query
    if category_id:
        articles_query = articles_query.filter_by(category_id=category_id)
    
    articles = articles_query.order_by(Article.published_date.desc()).limit(30).all()
    
    # Récupérer les favoris
    favorite_articles = [fav.article_id for fav in Favorite.query.filter_by(user_id=current_user.id).all()]
    
    return render_template('feed/index.html',
                           category_id=category_id,
                           categories=categories,
                           articles=articles,
                           favorite_articles=favorite_articles)

@feed_bp.route('/article/<int:article_id>')
@login_required
def view_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    # Vérifier si l'article est en favori
    is_favorite = Favorite.query.filter_by(
        user_id=current_user.id, article_id=article_id
    ).first() is not None
    
    # Enregistrer l'interaction
    interaction = Interaction(
        user_id=current_user.id,
        article_id=article_id,
        interaction_type='view',
        created_at=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()
    
    return render_template('feed/article.html', 
                           article=article, 
                           is_favorite=is_favorite)

@feed_bp.route('/api/track', methods=['POST'])
@login_required
def track_interaction():
    data = request.json
    article_id = data.get('article_id')
    interaction_type = data.get('type')
    duration = data.get('duration')
    
    # Vérifications
    if not article_id or not interaction_type:
        return jsonify({'error': 'Données incomplètes'}), 400
    
    # Vérifier que l'article existe
    if Article.query.get(article_id) is None:
        return jsonify({'error': 'Article non trouvé'}), 404
    
    # Enregistrer l'interaction
    interaction = Interaction(
        user_id=current_user.id,
        article_id=article_id,
        interaction_type=interaction_type,
        duration_seconds=duration,
        created_at=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify({'success': True})

@feed_bp.route('/refresh_feed')
@login_required
def refresh_feed():
    """Exécute le script d'importation des articles"""
    try:
        # Exécuter le script externe
        script_path = os.path.join(os.getcwd(), 'direct_rss_import.py')
        
        if not os.path.exists(script_path):
            flash("Script d'importation introuvable. Veuillez créer le fichier direct_rss_import.py", "danger")
            return redirect(url_for('feed.index'))
        
        result = subprocess.run([sys.executable, script_path], 
                            capture_output=True, 
                            text=True)
        
        if result.returncode == 0:
            flash("Articles importés avec succès", "success")
        else:
            flash(f"Erreur lors de l'importation des articles: {result.stderr}", "danger")
        
    except Exception as e:
        flash(f"Erreur: {str(e)}", "danger")
    
    return redirect(url_for('feed.index'))