# backend/main.py

from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

import models
import auth
from database import create_db_and_tables, get_session

app = FastAPI()

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- 認証API ---
@app.post("/api/register/", response_model=models.User)
def register_user(user_create: models.UserCreate, session: Session = Depends(get_session)):
    hashed_password = auth.get_password_hash(user_create.password)
    db_user = models.User(username=user_create.username, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/api/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(models.User).where(models.User.username == form_data.username)).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 記事API (認証必須) ---
@app.get("/api/articles/", response_model=List[models.ArticlePublic])
def read_articles(current_user: models.User = Depends(auth.get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(models.Article).where(models.Article.user_id == current_user.id)).all()

@app.post("/api/articles/", response_model=models.ArticlePublic)
def create_article(article: models.ArticleBase, current_user: models.User = Depends(auth.get_current_user), session: Session = Depends(get_session)):
    db_article = models.Article.model_validate(article)
    db_article.user_id = current_user.id
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article

# (他のAPIも同様に認証を必須にできます)