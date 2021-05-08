# ################################
#   Copyright (c) 2021 Jim Bray
#       All Rights Reserved
# ################################
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from database import Base


class Movie(Base):
    """
    model for the movie database
    """
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    title = Column(String(250), unique=True, nullable=False)
    year = Column(DateTime, default=datetime.now().year)
    description = Column(String(250), unique=False, nullable=False)
    rating = Column(Float(50), unique=False, nullable=True)
    ranking = Column(Integer(), unique=False, nullable=True)
    review = Column(String(250), unique=False, nullable=False)
    img_url = Column(String(250), unique=False, nullable=True)

    def __init__(self, timestamp=None, title=None, year=None, description=None, rating=None, ranking=None, review=None, img_url=None):
        self.timestamp = timestamp
        self.title = title
        self.year = year
        self.description = description
        self.rating = rating
        self.ranking = ranking
        self.review = review
        self.img_url = img_url

    def __repr__(self):
        return '<Movie %r>' % (self.title)
