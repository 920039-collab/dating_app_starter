from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import os
from jose import jwt, JWTError

app = FastAPI(title="Dating App API (MVP)")

# In-memory stores for demo only
USERS = {}
PROFILES = {}
MATCHES = set()
LIKES = set()
MESSAGES = []

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

class SignUp(BaseModel):
    phone: str
    password: str
    display_name: str

class SignIn(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Profile(BaseModel):
    user_id: int
    bio: Optional[str] = ""
    interests: List[str] = []
    gender: Optional[str] = None
    looking_for: Optional[str] = None
    city: Optional[str] = None
    birthdate: Optional[str] = None
    verified: bool = False
    compatibility_hint: Optional[float] = 0.0

class CandidateCard(BaseModel):
    user_id: int
    display_name: str
    age: Optional[int] = None
    city: Optional[str] = None
    interests: List[str] = []
    compatibility: float = 0.0

class Swipe(BaseModel):
    target_user_id: int
    action: str = Field(pattern="^(like|pass)$")

class Message(BaseModel):
    from_user_id: int
    to_user_id: int
    text: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=6)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/signup", response_model=Token)
def signup(body: SignUp):
    if body.phone in USERS:
        raise HTTPException(400, "Phone already registered")
    user_id = len(USERS) + 1
    USERS[body.phone] = {"id": user_id, "password": body.password, "display_name": body.display_name}
    PROFILES[user_id] = Profile(user_id=user_id, bio="", interests=[], verified=False)
    token = create_access_token({"sub": str(user_id)})
    return Token(access_token=token)

@app.post("/auth/signin", response_model=Token)
def signin(body: SignIn):
    user = USERS.get(body.phone)
    if not user or user["password"] != body.password:
        raise HTTPException(400, "Invalid credentials")
    token = create_access_token({"sub": str(user["id"])}) 
    return Token(access_token=token)

@app.get("/profiles/me", response_model=Profile)
def my_profile(authorization: str):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    return PROFILES[user_id]

@app.put("/profiles/me", response_model=Profile)
def update_profile(body: Profile, authorization: str):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    if body.user_id != user_id:
        raise HTTPException(403, "user_id mismatch")
    PROFILES[user_id] = body
    return body

def _compatibility(a: Profile, b: Profile) -> float:
    if not a or not b:
        return 0.0
    # toy score: Jaccard on interests + city match bonus
    s1 = set(a.interests); s2 = set(b.interests)
    j = len(s1 & s2) / max(1, len(s1 | s2))
    bonus = 0.1 if (a.city and b.city and a.city == b.city) else 0.0
    return round(min(1.0, j + bonus), 2)

@app.get("/candidates", response_model=List[CandidateCard])
def candidates(authorization: str, limit: int = 10):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    me = PROFILES[user_id]
    cards = []
    for uid, prof in PROFILES.items():
        if uid == user_id:
            continue
        comp = _compatibility(me, prof)
        urec = next((v for v in USERS.values() if v["id"] == uid), None)
        cards.append(CandidateCard(user_id=uid, display_name=urec["display_name"], city=prof.city, interests=prof.interests, compatibility=comp))
    cards.sort(key=lambda c: c.compatibility, reverse=True)
    return cards[:limit]

@app.post("/swipe")
def swipe(body: Swipe, authorization: str):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    if body.action == "like":
        LIKES.add((user_id, body.target_user_id))
        # check mutual
        if (body.target_user_id, user_id) in LIKES:
            MATCHES.add(tuple(sorted([user_id, body.target_user_id])))
            return {"status": "match", "match_with": body.target_user_id}
    return {"status": "ok"}

@app.get("/matches")
def get_matches(authorization: str):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    pairs = [list(m) for m in MATCHES if user_id in m]
    mate_ids = [pid for pair in pairs for pid in pair if pid != user_id]
    return {"matches": mate_ids}

@app.post("/messages")
def send_message(msg: Message, authorization: str):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    if user_id != msg.from_user_id:
        raise HTTPException(403, "from_user_id mismatch")
    key = tuple(sorted([msg.from_user_id, msg.to_user_id]))
    if key not in MATCHES:
        raise HTTPException(400, "Not matched")
    MESSAGES.append({"from": msg.from_user_id, "to": msg.to_user_id, "text": msg.text, "ts": datetime.utcnow().isoformat()})
    return {"status": "sent"}

@app.get("/messages/{peer_id}")
def list_messages(peer_id: int, authorization: str):
    user_id = get_current_user(authorization.replace("Bearer ", ""))
    key = tuple(sorted([user_id, peer_id]))
    if key not in MATCHES:
        raise HTTPException(400, "Not matched")
    return {"messages": [m for m in MESSAGES if {m["from"], m["to"]} == {user_id, peer_id}]}
