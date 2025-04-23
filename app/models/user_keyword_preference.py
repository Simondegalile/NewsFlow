from datetime import datetime
from app import db

class UserKeywordPreference(db.Model):
    __tablename__ = 'user_keyword_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    keyword = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('keyword_preferences', lazy=True))
    
    def __repr__(self):
        return f'<UserKeywordPreference user_id={self.user_id}, keyword={self.keyword}>'