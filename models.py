# backend/models.py

from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class ArticleTagLink(SQLModel, table=True):
    article_id: Optional[int] = Field(default=None, foreign_key="article.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    articles: List["Article"] = Relationship(back_populates="user")
    tags: List["Tag"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str

class TagBase(SQLModel):
    name: str = Field(index=True)

class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tags")
    
    articles: List["Article"] = Relationship(back_populates="tags", link_model=ArticleTagLink)

class ArticleBase(SQLModel):
    url: str
    title: str
    memo: Optional[str] = None
    is_read: bool = False

class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="articles")

    tags: List[Tag] = Relationship(back_populates="articles", link_model=ArticleTagLink)

class ArticleUpdate(SQLModel):
    is_read: Optional[bool] = None

class ArticlePublic(ArticleBase):
    id: int
    tags: List[Tag] = []

class TagPublic(TagBase):
    id: int