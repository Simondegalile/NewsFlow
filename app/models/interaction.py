from datetime import datetime
from app import db

class Interaction(db.Model):
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=True)
    interaction_type = db.Column(db.String(50), nullable=False)  # 'view', 'read', 'visit_feed', etc.
    duration_seconds = db.Column(db.Integer, nullable=True)      # Durée de lecture/visualisation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Interaction type={self.interaction_type}, user_id={self.user_id}, article_id={self.article_id}>'