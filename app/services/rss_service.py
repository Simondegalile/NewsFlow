import feedparser
from datetime import datetime
import re
from app import db
from app.models.article import Article
from app.models.source import Source
from app.models.keyword import Keyword

def clean_html(raw_html):
    """Nettoie les tags HTML du texte"""
    if not raw_html:
        return ""
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
            try:
                # Format standard des flux RSS
                dt = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
                return dt
            except Exception:
                try:
                    # Format alternatif (avec fuseau horaire)
                    dt = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S %z')
                    return dt
                except Exception:
                    return datetime.utcnow()
        return datetime.utcnow()
    except Exception:
        return datetime.utcnow()

def extract_image_from_html(html_content):
    """Extrait l'URL d'une image à partir du contenu HTML"""
    if not html_content:
        return None
    
    # Rechercher les balises img
    img_pattern = re.compile(r'<img[^>]+src="([^">]+)"')
    match = img_pattern.search(html_content)
    if match:
        return match.group(1)
    
    # Rechercher les URLs d'images
    img_url_pattern = re.compile(r'(https?://\S+\.(jpg|jpeg|png|gif))')
    match = img_url_pattern.search(html_content)
    if match:
        return match.group(1)
    
    return None

def find_image_url(entry):
    """Trouve l'URL de l'image dans une entrée de flux RSS"""
    image_url = None
    
    # 1. Vérifier les enclosures (FranceInfo, etc.)
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enclosure in entry.enclosures:
            if 'url' in enclosure and enclosure.get('type', '').startswith('image/'):
                image_url = enclosure['url']
                break
    
    # 2. Vérifier media_content
    if not image_url and hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                image_url = media['url']
                break
    
    # 3. Vérifier media:thumbnail (pour Numerama)
    if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        if isinstance(entry.media_thumbnail, list) and len(entry.media_thumbnail) > 0:
            if 'url' in entry.media_thumbnail[0]:
                image_url = entry.media_thumbnail[0]['url']
    
    # 4. Vérifier le contenu pour extraire une image (si aucune image trouvée)
    if not image_url:
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
            image_url = extract_image_from_html(content)
        elif hasattr(entry, 'description'):
            image_url = extract_image_from_html(entry.description)
    
    # 5. Vérifier le champ image s'il existe
    if not image_url and hasattr(entry, 'image'):
        if hasattr(entry.image, 'url'):
            image_url = entry.image.url
        elif isinstance(entry.image, dict) and 'url' in entry.image:
            image_url = entry.image['url']
    
    return image_url

def fetch_and_store_articles():
    """Récupère les articles des flux RSS et les enregistre dans la base"""
    sources = Source.query.all()
    new_article_count = 0
    
    for source in sources:
        try:
            print(f"Récupération du flux RSS: {source.name}")
            
            # Configuration de User-Agent pour éviter les blocages
            import urllib.request
            req = urllib.request.Request(
                source.url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            )
            
            # Récupération du flux avec timeout
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    feed_content = response.read()
                    feed = feedparser.parse(feed_content)
            except Exception as e:
                print(f"Erreur lors de la récupération du flux {source.name}: {e}")
                continue
            
            # Vérifier si des entrées sont présentes
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"Aucune entrée dans le flux: {source.name}")
                continue
                
            print(f"Nombre d'articles trouvés: {len(feed.entries)}")
            
            for entry in feed.entries:
                # Vérifier si l'article existe déjà
                url = entry.link if hasattr(entry, 'link') else None
                if not url or Article.query.filter_by(url=url).first():
                    continue
                
                # Extraire le titre
                title = entry.title if hasattr(entry, 'title') else "Sans titre"
                
                # Extraire le résumé/description
                summary = ""
                if hasattr(entry, 'description'):
                    summary = clean_html(entry.description)
                elif hasattr(entry, 'summary'):
                    summary = clean_html(entry.summary)
                
                # Extraire le contenu complet
                content = summary
                if hasattr(entry, 'content') and entry.content:
                    if isinstance(entry.content, list) and len(entry.content) > 0:
                        content = entry.content[0].value
                    else:
                        content = entry.content
                
                # Trouver l'URL de l'image
                image_url = find_image_url(entry)
                
                # Extraire la date de publication
                published_date = parse_date(entry.get('published', '')) if hasattr(entry, 'published') else datetime.utcnow()
                
                # Créer le nouvel article
                new_article = Article(
                    source_id=source.id,
                    category_id=source.category_id,
                    title=title,
                    content=content,
                    summary=summary[:500] if summary else "",  # Limite pour éviter les résumés trop longs
                    url=url,
                    image_url=image_url,
                    published_date=published_date
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
                print(f"Article ajouté: {title[:50]}...")
            
            # Mettre à jour la date de dernière mise à jour de la source
            source.last_update = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du traitement de la source {source.name}: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    return new_article_count