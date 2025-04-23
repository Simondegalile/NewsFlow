from app.models.article import Article
from app.models.interaction import Interaction
from app.models.keyword import Keyword
from app.models.user_keyword_preference import UserKeywordPreference
from sqlalchemy import func
from app import db

def update_user_preferences(user_id):
    """Met à jour les préférences de mots-clés de l'utilisateur en fonction de ses interactions"""
    # Récupérer les interactions récentes de l'utilisateur
    interactions = Interaction.query.filter_by(
        user_id=user_id,
        interaction_type='read'
    ).order_by(Interaction.created_at.desc()).limit(50).all()
    
    if not interactions:
        return
    
    # Récupérer les IDs des articles lus
    article_ids = [i.article_id for i in interactions if i.article_id]
    
    # Récupérer les mots-clés de ces articles
    article_keywords = Keyword.query.filter(Keyword.article_id.in_(article_ids)).all()
    
    # Compter l'occurrence des mots-clés
    keyword_counts = {}
    for kw in article_keywords:
        if kw.keyword in keyword_counts:
            keyword_counts[kw.keyword] += 1
        else:
            keyword_counts[kw.keyword] = 1
    
    # Mettre à jour ou créer des préférences utilisateur
    for keyword, count in keyword_counts.items():
        # Normaliser le poids (1-5)
        weight = min(5, max(1, count))
        
        # Chercher une préférence existante
        preference = UserKeywordPreference.query.filter_by(
            user_id=user_id,
            keyword=keyword
        ).first()
        
        if preference:
            # Mettre à jour le poids (moyenne mobile)
            preference.weight = (preference.weight * 0.7) + (weight * 0.3)
        else:
            # Créer une nouvelle préférence
            preference = UserKeywordPreference(
                user_id=user_id,
                keyword=keyword,
                weight=weight
            )
            db.session.add(preference)
    
    # Enregistrer les modifications
    db.session.commit()

def get_recommended_articles(user_id, limit=20):
    """Récupère les articles recommandés pour un utilisateur"""
    # Si aucun ID utilisateur n'est fourni, renvoyer les articles récents
    if not user_id:
        return Article.query.order_by(Article.published_date.desc()).limit(limit)
    
    # Récupérer les préférences de mots-clés de l'utilisateur
    user_preferences = UserKeywordPreference.query.filter_by(user_id=user_id).all()
    
    # Si l'utilisateur n'a pas de préférences, renvoyer les articles récents
    if not user_preferences:
        return Article.query.order_by(Article.published_date.desc()).limit(limit)
    
    # IDs des articles déjà lus
    read_article_ids = [i.article_id for i in Interaction.query.filter_by(
        user_id=user_id,
        interaction_type='read'
    ).all() if i.article_id]
    
    # Créer un dictionnaire des mots-clés et leurs poids
    keyword_weights = {pref.keyword: pref.weight for pref in user_preferences}
    
    # Requête avancée pour récupérer les articles pertinents
    # Calcul d'un score basé sur les correspondances de mots-clés
    recommended_articles = []
    
    # Récupérer tous les mots-clés des articles non lus
    candidate_keywords = Keyword.query.filter(
        ~Keyword.article_id.in_(read_article_ids)
    ).all()
    
    # Calculer un score pour chaque article
    article_scores = {}
    for kw in candidate_keywords:
        if kw.keyword in keyword_weights:
            if kw.article_id in article_scores:
                article_scores[kw.article_id] += kw.weight * keyword_weights[kw.keyword]
            else:
                article_scores[kw.article_id] = kw.weight * keyword_weights[kw.keyword]
    
    # Trier les articles par score
    sorted_articles = sorted(article_scores.items(), key=lambda x: x[1], reverse=True)
    top_article_ids = [article_id for article_id, _ in sorted_articles[:limit]]
    
    # Si nous n'avons pas assez d'articles recommandés, compléter avec des articles récents
    if len(top_article_ids) < limit:
        additional_articles = Article.query.filter(
            ~Article.id.in_(read_article_ids + top_article_ids)
        ).order_by(
            Article.published_date.desc()
        ).limit(limit - len(top_article_ids))
        
        for article in additional_articles:
            top_article_ids.append(article.id)
    
    # Récupérer les objets Article dans l'ordre de pertinence
    if top_article_ids:
        from sqlalchemy import case
        # Cette requête préserve l'ordre de tri par pertinence
        articles_query = Article.query.filter(Article.id.in_(top_article_ids))
        articles_query = articles_query.order_by(
            case({id: i for i, id in enumerate(top_article_ids)}, value=Article.id)
        )
        return articles_query
    else:
        # Fallback sur les articles récents
        return Article.query.order_by(Article.published_date.desc()).limit(limit)