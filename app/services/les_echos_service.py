"""
Service pour récupérer les articles des Échos en contournant la protection
"""
import requests
from datetime import datetime
import re
import random
from bs4 import BeautifulSoup

def get_les_echos_articles(category=None, limit=5):
    """
    Récupère les articles des Échos via le scraping du site web plutôt que le flux RSS
    
    Args:
        category: Catégorie d'articles (économie, politique, etc.)
        limit: Nombre maximum d'articles à récupérer
        
    Returns:
        Liste d'articles formatés
    """
    # URLs des pages par catégorie
    category_urls = {
        "À la une": "https://www.lesechos.fr/",
        "Économie": "https://www.lesechos.fr/economie-france",
        "Politique": "https://www.lesechos.fr/politique-societe",
        "Entreprise": "https://www.lesechos.fr/industrie-services",
        "Finance et Marchés": "https://www.lesechos.fr/finance-marches",
        "Idées": "https://www.lesechos.fr/idees-debats",
        "Tech et Médias": "https://www.lesechos.fr/tech-medias",
    }
    
    # URL par défaut
    url = "https://www.lesechos.fr/"
    
    # Si une catégorie est spécifiée et existe dans notre mapping
    if category and category in category_urls:
        url = category_urls[category]
    
    # Préparer les headers pour éviter d'être bloqué
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    try:
        # Effectuer la requête
        response = requests.get(url, headers=headers, timeout=10)
        
        # Vérifier que la requête a fonctionné
        if response.status_code != 200:
            print(f"Erreur lors de la récupération de la page Les Échos: {response.status_code}")
            return []
        
        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Récupérer les articles
        articles = []
        
        # Différents sélecteurs CSS pour les articles
        article_selectors = [
            'article.article-small', 
            'article.article-medium',
            'article.article-large',
            '.article-preview',
            '.article-block'
        ]
        
        # Trouver tous les articles correspondant aux sélecteurs
        article_elements = []
        for selector in article_selectors:
            article_elements.extend(soup.select(selector))
        
        # Limiter le nombre d'articles
        article_elements = article_elements[:limit]
        
        for article_elem in article_elements:
            try:
                # Trouver le titre
                title_elem = article_elem.select_one('h2, h3, .title')
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                
                # Trouver le lien
                link_elem = article_elem.select_one('a[href]')
                if not link_elem:
                    continue
                
                link = link_elem['href']
                
                # S'assurer que le lien est complet
                if not link.startswith('http'):
                    link = f"https://www.lesechos.fr{link}"
                
                # Trouver la description/résumé
                summary_elem = article_elem.select_one('.chapo, .preview-text, p')
                summary = summary_elem.text.strip() if summary_elem else ""
                
                # Trouver l'image (s'il y en a une)
                image_elem = article_elem.select_one('img')
                image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else None
                
                # Créer l'article
                article = {
                    'title': title,
                    'url': link,
                    'summary': summary[:200] + "..." if len(summary) > 200 else summary,
                    'image_url': image_url,
                    'source_name': "Les Échos",
                    'source_logo': "https://www.lesechos.fr/favicon.ico",
                    'published_date': datetime.now().strftime('%d/%m/%Y'),
                    'category_name': category or "À la une"
                }
                
                articles.append(article)
                
            except Exception as e:
                print(f"Erreur lors de l'extraction d'un article Les Échos: {e}")
        
        return articles
        
    except Exception as e:
        print(f"Erreur lors de la récupération des articles Les Échos: {e}")
        return []