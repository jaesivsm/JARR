from bootstrap import db
from sqlalchemy import Index


class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    idx_category_uid = Index('user_id')

    def dump(self):
        return {key: getattr(self, key) for key in ('id', 'name', 'user_id')}
