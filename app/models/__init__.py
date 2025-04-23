# app/models/__init__.py
# Import des modèles pour faciliter l'accès
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.source import Source
from app.models.favorite import Favorite
from app.models.interaction import Interaction
from app.models.keyword import Keyword
from app.models.user_keyword_preference import UserKeywordPreference
from app.models.user_category_preference import UserCategoryPreference
from app.models.user_stat import UserStat
from app.models.session import Session