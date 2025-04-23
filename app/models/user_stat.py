from datetime import datetime
from app import db

class UserStat(db.Model):
    __tablename__ = 'user_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_time_spent = db.Column(db.Integer, default=0)  # en secondes
    articles_viewed = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('stats', lazy=True))
    
    def __repr__(self):
        return f'<UserStat user_id={self.user_id}>'