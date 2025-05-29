from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, DateTime, func, Text, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    refresh_token = Column(String, unique=True, nullable=False)
    device_id = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")

class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="unique_follower_following"),)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="author", cascade="all, delete")
    followers = relationship("UserFollow", foreign_keys=[UserFollow.following_id], back_populates="following", cascade="all, delete")
    following = relationship("UserFollow", foreign_keys=[UserFollow.follower_id], back_populates="follower", cascade="all, delete")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    posts = relationship("Post", back_populates="category")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    file_url = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    votes = relationship("PostVote", back_populates="post")
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")

    @property
    def rating_percentage(self) -> float:
        """Calculate the rating percentage."""
        total_votes = self.upvotes + self.downvotes
        if total_votes == 0:
            return 0.0
        return (self.upvotes / total_votes) * 100
    
class PostVote(Base):
    __tablename__ = "post_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    is_upvote = Column(Boolean, nullable=False)  # True for upvote, False for downvote

    post = relationship("Post", back_populates="votes")

    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_user_post_vote"),)