from datetime import datetime
from app import db

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    logo_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    articles = db.relationship('Article', backref='source', lazy=True)
    
    def __repr__(self):
        return f'<Source {self.name}>'