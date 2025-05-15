import feedparser
from datetime import datetime
import re
import urllib.request
import urllib.error
from app.models.source import Source
from app.models.category import Category

# Importer le service spécifique pour Les Échos
from app.services.les_echos_service import get_les_echos_articles

def clean_html(raw_html):
    """Nettoie les tags HTML du texte"""
    if not raw_html:
        return ""
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)
    return clean_text

def fetch_rss_feeds(category_id=None, limit=20):
    """
    Récupère les articles des flux RSS en direct
    
    Args:
        category_id: ID de la catégorie pour filtrer les sources
        limit: Nombre maximum d'articles à récupérer
    
    Returns:
        Liste d'articles formatés
    """
    print(f"Appel de fetch_rss_feeds avec category_id={category_id}, limit={limit}")
    
    # Récupérer les sources appropriées
    query = Source.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    sources = query.all()
    
    if not sources:
        print(f"Aucune source trouvée pour la catégorie {category_id}")
        return []
    
    all_articles = []
    
    # User-Agent pour éviter d'être bloqué
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    source_count = len(sources)
    print(f"Traitement de {source_count} sources")
    
    # Récupérer la catégorie pour Les Échos (si filtrée)
    category_name = None
    if category_id:
        category = Category.query.get(category_id)
        if category:
            category_name = category.name
    
    # Ajouter les articles des Échos (en utilisant le service spécial)
    try:
        echos_articles = get_les_echos_articles(category=category_name, limit=5)
        if echos_articles:
            all_articles.extend(echos_articles)
            print(f"Ajout de {len(echos_articles)} articles des Échos")
    except Exception as e:
        print(f"Erreur lors de la récupération des articles des Échos: {e}")
    
    # Flux alternatifs pour les sources connues
    alternative_urls = {
        # Le Monde
        "https://www.lemonde.fr/rss/une.xml": "https://www.lemonde.fr/actualite-en-continu/rss_full.xml",
    }
    
    # Traiter les autres sources RSS
    for i, source in enumerate(sources):
        # Ignorer les sources des Échos (déjà traitées)
        if "Échos" in source.name:
            continue
            
        print(f"Source {i+1}/{source_count}: {source.name} - {source.url}")
        
        try:
            # Utiliser l'URL alternative si disponible
            url = alternative_urls.get(source.url, source.url)
            print(f"  URL utilisée: {url}")
            
            # Préparation de la requête
            request = urllib.request.Request(
                url,
                headers={'User-Agent': user_agent}
            )
            
            # Récupération du flux
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    feed_content = response.read()
                    print(f"  ✅ Flux récupéré ({len(feed_content)} octets)")
            except urllib.error.HTTPError as e:
                print(f"  ❌ Erreur HTTP {e.code} pour {url}")
                continue
            except Exception as e:
                print(f"  ❌ Erreur lors de la requête: {e}")
                continue
            
            # Analyse du flux
            feed = feedparser.parse(feed_content)
            
            # Vérifier si des entrées sont présentes
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"  ⚠️ Aucune entrée dans le flux")
                continue
            
            # Informations sur le flux
            entry_count = len(feed.entries)
            print(f"  📰 {entry_count} articles trouvés")
            
            # Traiter les articles
            processed_count = min(entry_count, 5)  # Maximum 5 articles par source
            print(f"  ⏩ Traitement de {processed_count} articles")
            
            # Récupérer le nom de la catégorie (méthode sécurisée)
            try:
                # Essayer d'obtenir la catégorie via la relation
                if hasattr(source, 'category') and source.category:
                    category_name = source.category.name
                else:
                    # Si la relation n'existe pas, chercher directement
                    category = Category.query.get(source.category_id)
                    category_name = category.name if category else "Divers"
            except Exception as e:
                print(f"  ⚠️ Erreur de récupération de catégorie: {e}")
                category_name = "Divers"
            
            for entry in feed.entries[:processed_count]:
                try:
                    # Titre
                    title = entry.get('title', 'Sans titre')
                    
                    # Lien
                    link = entry.get('link', '')
                    if not link:
                        print(f"  ⚠️ Article sans lien: {title[:30]}...")
                        continue
                    
                    # Description / Résumé
                    summary = ""
                    if hasattr(entry, 'description'):
                        summary = clean_html(entry.description)
                    elif hasattr(entry, 'summary'):
                        summary = clean_html(entry.summary)
                    
                    # Image - PARTIE MODIFIÉE
                    image_url = None
                    
                    # 1. Vérifier d'abord les enclosures (format FranceInfo)
                    if hasattr(entry, 'enclosures') and entry.enclosures:
                        print(f"  🔍 Enclosures trouvées ({len(entry.enclosures)})")
                        for enclosure in entry.enclosures:
                            if 'url' in enclosure and enclosure.get('type', '').startswith('image/'):
                                image_url = enclosure['url']
                                print(f"  🖼️ Image trouvée (enclosure): {image_url[:50]}...")
                                break
                    
                    # 2. Si aucune image trouvée, essayer media_content
                    if not image_url and hasattr(entry, 'media_content') and entry.media_content:
                        print(f"  🔍 Media content trouvé ({len(entry.media_content)})")
                        for media in entry.media_content:
                            if 'url' in media:
                                image_url = media['url']
                                print(f"  🖼️ Image trouvée (media_content): {image_url[:50]}...")
                                break
                    
                    if not image_url:
                        print(f"  ⚠️ Pas d'image trouvée pour: {title[:30]}...")
                    
                    # Date de publication
                    published = datetime.now().strftime('%d/%m/%Y')
                    if hasattr(entry, 'published'):
                        try:
                            # Format standard des flux RSS
                            dt = datetime.strptime(entry.published[:25], '%a, %d %b %Y %H:%M:%S')
                            published = dt.strftime('%d/%m/%Y')
                        except Exception:
                            try:
                                # Format alternatif (avec fuseau horaire)
                                dt = datetime.strptime(entry.published[:25], '%a, %d %b %Y %H:%M:%S %z')
                                published = dt.strftime('%d/%m/%Y')
                            except Exception as e:
                                print(f"  ⚠️ Erreur de parsing de date: {e}")
                    
                    # Créer l'article
                    article = {
                        'title': title,
                        'url': link,
                        'summary': summary[:200] + "..." if len(summary) > 200 else summary,
                        'image_url': image_url,
                        'source_name': source.name,
                        'source_logo': source.logo_url,
                        'published_date': published,
                        'category_name': category_name,
                        'article_direct': True  # Marquer comme article direct
                    }
                    
                    all_articles.append(article)
                    print(f"  ✅ Article ajouté: {title[:30]}...")
                    
                except Exception as e:
                    print(f"  ❌ Erreur traitement article: {e}")
            
        except Exception as e:
            print(f"  ❌ Erreur générale: {e}")
    
    article_count = len(all_articles)
    print(f"Total: {article_count} articles récupérés")
    
    # Tronquer à la limite demandée
    result = all_articles[:limit]
    print(f"Renvoi de {len(result)} articles (limite: {limit})")
    
    return result

def get_categories():
    """
    Récupère toutes les catégories disponibles
    
    Returns:
        Liste des catégories
    """
    categories = Category.query.all()
    return [{'id': cat.id, 'name': cat.name, 'description': cat.description} for cat in categories]