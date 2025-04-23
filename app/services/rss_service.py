import feedparser
from datetime import datetime
import re
from app import db
from app.models.article import Article
from app.models.source import Source
from app.models.keyword import Keyword

def clean_html(raw_html):
    """Nettoie les tags HTML du texte"""
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)
    return clean_text

def extract_keywords(text, max_keywords=5):
    """Extrait des mots-clés d'un texte"""
    if not text:
        return []
    
    # Nettoyer et préparer le texte
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Filtrer les mots courants
    words = clean_text.split()
    stop_words = {'le', 'la', 'les', 'du', 'de', 'des', 'un', 'une', 'et', 'en', 'à', 'au', 'aux', 
                  'ce', 'cette', 'ces', 'qui', 'que', 'quoi', 'dont', 'où', 'pour', 'par', 'sur', 'dans'}
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Compter les occurrences
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Garder les mots les plus fréquents
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
    return [word for word, _ in top_words]

def parse_date(date_str):
    """Convertit un format de date RSS en objet datetime"""
    try:
        if date_str:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt
        return datetime.utcnow()
    except Exception:
        return datetime.utcnow()

def fetch_and_store_articles():
    """Récupère les articles des flux RSS et les enregistre dans la base"""
    sources = Source.query.all()
    new_article_count = 0
    
    for source in sources:
        try:
            print(f"Récupération du flux RSS: {source.name}")
            feed = feedparser.parse(source.url)
            
            for entry in feed.entries:
                # Vérifier si l'article existe déjà
                if Article.query.filter_by(url=entry.link).first():
                    continue
                
                # Extraire les informations
                title = entry.title
                summary = clean_html(entry.get('description', ''))
                
                # Certains flux RSS stockent le contenu différemment
                if 'content' in entry and entry.content:
                    content = entry.content[0].value
                else:
                    content = summary
                
                # Récupérer l'image si disponible
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if 'url' in media:
                            image_url = media['url']
                            break
                
                # Créer le nouvel article
                new_article = Article(
                    source_id=source.id,
                    category_id=source.category_id,
                    title=title,
                    content=content,
                    summary=summary,
                    url=entry.link,
                    image_url=image_url,
                    published_date=parse_date(entry.get('published', ''))
                )
                
                db.session.add(new_article)
                db.session.commit()
                
                # Extraire et stocker les mots-clés
                keywords = extract_keywords(title + ' ' + summary)
                for keyword in keywords:
                    keyword_obj = Keyword(
                        article_id=new_article.id,
                        keyword=keyword,
                        weight=1.0
                    )
                    db.session.add(keyword_obj)
                
                new_article_count += 1
            
            # Mettre à jour la date de dernière mise à jour de la source
            source.last_update = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du traitement de la source {source.name}: {str(e)}")
    
    return new_article_count