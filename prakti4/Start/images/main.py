from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from pydantic import BaseModel
import numpy as np
from models import Base, User, Criteria, Car, CarSpecification, CarReview, CrashTest
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Car Selection Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserProfile(BaseModel):
    usage_goals: List[str]
    budget: int
    body_type: str
    fuel_type: str
    transmission: str
    drivetrain: str
    engine_power: int
    fuel_consumption: float
    safety_features: List[str]
    comfort_features: List[str]

class CriteriaWeights(BaseModel):
    price: float
    safety: float
    reliability: float
    economy: float
    comfort: float
    capacity: float
    dynamics: float
    appearance: float
    maintenance_cost: float
    additional_options: float

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def calculate_ahp_weights(comparison_matrix: np.ndarray) -> np.ndarray:
    """Calculate weights using the Analytic Hierarchy Process"""
    normalized_matrix = comparison_matrix / comparison_matrix.sum(axis=0)
    weights = normalized_matrix.mean(axis=1)
    return weights

def calculate_consistency_ratio(comparison_matrix: np.ndarray) -> float:
    """Calculate the consistency ratio for AHP"""
    n = comparison_matrix.shape[0]
    weights = calculate_ahp_weights(comparison_matrix)
    lambda_max = np.sum((comparison_matrix @ weights) / weights) / n
    consistency_index = (lambda_max - n) / (n - 1)
    random_index = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    consistency_ratio = consistency_index / random_index.get(n, 1.49)
    return consistency_ratio

@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name
    )
    new_user.set_password(user.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/profile")
async def update_profile(
    profile: UserProfile,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user.set_usage_goals(profile.usage_goals)
    user.budget = profile.budget
    user.body_type = profile.body_type
    user.fuel_type = profile.fuel_type
    user.transmission = profile.transmission
    user.drivetrain = profile.drivetrain
    user.engine_power = profile.engine_power
    user.fuel_consumption = profile.fuel_consumption
    user.set_safety_features(profile.safety_features)
    user.set_comfort_features(profile.comfort_features)

    db.commit()
    return {"message": "Profile updated successfully"}

@app.post("/criteria/weights")
async def update_criteria_weights(
    weights: CriteriaWeights,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user.set_criteria(weights.dict())
    db.commit()
    return {"message": "Criteria weights updated successfully"}

@app.get("/cars/recommendations")
async def get_car_recommendations(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    criteria_weights = user.get_criteria()
    
    cars = db.query(Car).all()
    
    car_scores = []
    for car in cars:
        score = 0
        car_scores.append({
            "car": car,
            "score": score
        })
    
    car_scores.sort(key=lambda x: x["score"], reverse=True)
    
    return car_scores[:10]