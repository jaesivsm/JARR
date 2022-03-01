from jarr.bootstrap import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import RelationshipProperty, relationship


class Icon(Base):  # type: ignore
    __tablename__ = 'icon'

    url = Column(String, primary_key=True)
    content = Column(String, default=None)
    mimetype = Column(String, default="application/image")

    # relationships
    feeds: RelationshipProperty = relationship('Feed', backref='icon')
