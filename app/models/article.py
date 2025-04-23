from datetime import datetime
from app import db

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    url = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))
    published_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    favorites = db.relationship('Favorite', backref='article', lazy=True, cascade='all, delete-orphan')
    interactions = db.relationship('Interaction', backref='article', lazy=True, cascade='all, delete-orphan')
    keywords = db.relationship('Keyword', backref='article', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Article {self.title}>'