from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.favorite import Favorite
from app.models.article import Article

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/favorites')
@login_required
def list_favorites():
    # Récupérer les favoris de l'utilisateur
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    article_ids = [fav.article_id for fav in favorites]
    articles = Article.query.filter(Article.id.in_(article_ids)).all()
    
    return render_template('feed/favorites.html', articles=articles)

@favorite_bp.route('/api/favorites/toggle/<int:article_id>', methods=['POST'])
@login_required
def toggle_favorite(article_id):
    # Vérifier si l'article existe
    article = Article.query.get_or_404(article_id)
    
    # Vérifier si déjà en favori
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        article_id=article_id
    ).first()
    
    if favorite:
        # Supprimer des favoris
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'status': 'removed', 'article_id': article_id})
    else:
        # Ajouter aux favoris
        new_favorite = Favorite(
            user_id=current_user.id,
            article_id=article_id
        )
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'status': 'added', 'article_id': article_id})