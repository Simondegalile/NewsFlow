from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.article import Article
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.interaction import Interaction
from datetime import datetime

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
    
    return render_template('feed/index.html', 
                           category_id=category_id, 
                           categories=categories)

@feed_bp.route('/api/articles')
@login_required
def get_articles():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Filtrer par catégorie si spécifiée
    if category_id:
        articles = Article.query.filter_by(category_id=category_id)
    else:
        articles = Article.query
    
    # Ordonner et paginer
    articles = articles.order_by(Article.published_date.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    # Récupérer les favoris de l'utilisateur
    favorite_articles = [fav.article_id for fav in Favorite.query.filter_by(user_id=current_user.id).all()]
    
    # Formater la réponse
    result = {
        'articles': [],
        'has_next': articles.has_next,
        'next_page': articles.next_num if articles.has_next else None
    }
    
    for article in articles.items:
        result['articles'].append({
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'image_url': article.image_url,
            'source_name': article.source.name if article.source else 'Source inconnue',
            'category_name': article.category.name if article.category else 'Catégorie inconnue',
            'published_date': article.published_date.strftime('%d/%m/%Y') if article.published_date else None,
            'url': article.url,
            'is_favorite': article.id in favorite_articles
        })
    
    return jsonify(result)

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