from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class State(db.Model):
    __tablename__ = "states"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))

    regions = db.relationship(
        "Region",
        backref="state",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Region(db.Model):
    __tablename__ = "regions"

    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey("states.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))

    stories = db.relationship(
        "FolkStory",
        backref="region",
        lazy=True,
        cascade="all, delete-orphan"
    )


class FolkStory(db.Model):
    __tablename__ = "folk_stories"

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    story_text = db.Column(db.Text)
    image = db.Column(db.String(255))
    audio = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    translations = db.relationship(
        "Translation",
        backref="story",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "StoryLike",
        backref="story",
        lazy=True,
        cascade="all, delete-orphan"
    )

    comments = db.relationship(
        "StoryComment",
        backref="story",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Translation(db.Model):
    __tablename__ = "translations"

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey("folk_stories.id"), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    language_code = db.Column(db.String(20), nullable=False)
    translated_text = db.Column(db.Text)


class StoryLike(db.Model):
    __tablename__ = "story_likes"

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey("folk_stories.id"), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StoryComment(db.Model):
    __tablename__ = "story_comments"

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey("folk_stories.id"), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
