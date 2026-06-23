from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
import auth
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Betting API")


# DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# REGISTER USER
# -------------------------
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")

    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username exists")

    hashed = auth.get_password_hash(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------------
# LOGIN (NOW SHOWS IN SWAGGER UI)
# -------------------------
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token = auth.create_access_token(data={"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# GET GAMES
# -------------------------
@app.get("/games", response_model=list[schemas.GameOut])
def get_games(db: Session = Depends(get_db)):
    return db.query(models.Game).all()


# -------------------------
# CREATE GAME (ADMIN TEST)
# -------------------------
@app.post("/games")
def create_game(
    team_a: str,
    team_b: str,
    odds_a: float,
    odds_b: float,
    db: Session = Depends(get_db)
):

    game = models.Game(
        team_a=team_a,
        team_b=team_b,
        odds_a=odds_a,
        odds_b=odds_b,
        status="upcoming"
    )

    db.add(game)
    db.commit()
    db.refresh(game)

    return game


# -------------------------
# PLACE BET
# -------------------------
@app.post("/bet", response_model=schemas.BetOut)
def place_bet(bet: schemas.BetCreate, db: Session = Depends(get_db)):

    game = db.query(models.Game).filter(models.Game.id == bet.game_id).first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != "upcoming":
        raise HTTPException(status_code=400, detail="Betting closed")

    if bet.pick not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Pick must be A or B")

    new_bet = models.Bet(
        game_id=bet.game_id,
        amount=bet.amount,
        pick=bet.pick,
        status="pending"
    )

    db.add(new_bet)
    db.commit()
    db.refresh(new_bet)

    return new_bet


# -------------------------
# GET ALL BETS
# -------------------------
@app.get("/bets", response_model=list[schemas.BetOut])
def get_bets(db: Session = Depends(get_db)):
    return db.query(models.Bet).all()