from datetime import datetime
from app import db

class UserCategoryPreference(db.Model):
    __tablename__ = 'user_category_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('category_preferences', lazy=True))
    category = db.relationship('Category', backref=db.backref('user_preferences', lazy=True))
    
    def __repr__(self):
        return f'<UserCategoryPreference user_id={self.user_id}, category_id={self.category_id}>'