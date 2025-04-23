from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models.interaction import Interaction
from app.models.article import Article
from app.models.category import Category
from app.models.user_keyword_preference import UserKeywordPreference
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Nombre d'articles lus
    read_count = Interaction.query.filter_by(
        user_id=current_user.id,
        interaction_type='read'
    ).count()
    
    # Temps total passé
    total_time = db.session.query(func.sum(Interaction.duration_seconds)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    # Statistiques par catégorie
    category_stats = db.session.query(
        Category.name,
        func.count(Interaction.id).label('count')
    ).join(
        Article, Article.id == Interaction.article_id
    ).join(
        Category, Category.id == Article.category_id
    ).filter(
        Interaction.user_id == current_user.id,
        Interaction.interaction_type == 'read'
    ).group_by(
        Category.name
    ).order_by(
        func.count(Interaction.id).desc()
    ).all()
    
    # Mots-clés préférés
    keyword_preferences = UserKeywordPreference.query.filter_by(
        user_id=current_user.id
    ).order_by(
        UserKeywordPreference.weight.desc()
    ).limit(10).all()
    
    # Articles récemment lus
    recent_articles_interactions = Interaction.query.filter_by(
        user_id=current_user.id,
        interaction_type='read'
    ).order_by(
        Interaction.created_at.desc()
    ).limit(5).all()
    
    recent_article_ids = [i.article_id for i in recent_articles_interactions if i.article_id]
    recent_articles = Article.query.filter(Article.id.in_(recent_article_ids)).all()
    
    # Ordonner les articles selon l'ordre des interactions
    ordered_articles = []
    for interaction in recent_articles_interactions:
        for article in recent_articles:
            if article.id == interaction.article_id:
                ordered_articles.append(article)
                break
    
    return render_template('dashboard/index.html',
                           read_count=read_count,
                           total_time=total_time,
                           category_stats=category_stats,
                           keyword_preferences=keyword_preferences,
                           recent_articles=ordered_articles)