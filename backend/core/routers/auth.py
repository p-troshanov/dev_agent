# backend/core/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.database import get_db
from backend.core.db_init import create_system_agents_if_needed
from backend.core.auth import get_password_hash, verify_password, create_access_token, get_current_user
from backend.core.schemas import UserCreate, Token, UserData
from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, DEFAULT_SETTINGS
from backend.core.tools.registry import sync_user_tools
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register_user(user: UserCreate):
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT id FROM users WHERE username = %s", (user.username,))
            if c.fetchone():
                raise HTTPException(status_code=400, detail="Username already registered")
            
            hashed_pw = get_password_hash(user.password)
            c.execute("INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id",
                       (user.username, hashed_pw))
            user_id = c.fetchone()[0]
            
            c.execute("INSERT INTO user_settings (user_id, user_name, weather_city, avatar) VALUES (%s, %s, %s, %s)",
                      (user_id, DEFAULT_SETTINGS["user_name"], DEFAULT_SETTINGS["weather_city"], DEFAULT_SETTINGS.get("avatar")))
        conn.commit()
        
    create_system_agents_if_needed(user_id)
    sync_user_tools(user_id)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT id, hashed_password FROM users WHERE username = %s", (form_data.username,))
            user = c.fetchone()
            
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    sync_user_tools(user[0])
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user[0])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserData)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
