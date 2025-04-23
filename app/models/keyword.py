from app import db

class Keyword(db.Model):
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    keyword = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, default=1.0)  # Poids/importance du mot-clé
    
    def __repr__(self):
        return f'<Keyword {self.keyword}, article_id={self.article_id}>'