from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from jarr.bootstrap import Base


class Icon(Base):
    __tablename__ = 'icon'

    url = Column(String, primary_key=True)
    content = Column(String, default=None)
    mimetype = Column(String, default="application/image")

    # relationships
    feeds = relationship('Feed', backref='icon')
