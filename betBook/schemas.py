from pydantic import BaseModel

# USER
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


# GAME
class GameOut(BaseModel):
    id: int
    team_a: str
    team_b: str
    odds_a: float
    odds_b: float
    status: str

    class Config:
        from_attributes = True


# BET
class BetCreate(BaseModel):
    game_id: int
    amount: float
    pick: str


class BetOut(BaseModel):
    id: int
    game_id: int
    amount: float
    pick: str
    status: str

    class Config:
        from_attributes = True