from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

# 1️⃣ CREATE APP FIRST
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Vibe Check Polling API is running"}


# 2️⃣ DATABASE SETUP
conn = sqlite3.connect("polls.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS polls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id INTEGER,
    text TEXT,
    votes INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    poll_id INTEGER,
    user_id TEXT
)
""")

conn.commit()

# 3️⃣ MODELS
class PollCreate(BaseModel):
    question: str
    options: List[str]

class VoteRequest(BaseModel):
    user_id: str
    option_id: int

# 4️⃣ ROUTES
@app.post("/polls")
def create_poll(poll: PollCreate):
    cursor.execute("INSERT INTO polls (question) VALUES (?)", (poll.question,))
    poll_id = cursor.lastrowid

    for option in poll.options:
        cursor.execute(
            "INSERT INTO options (poll_id, text) VALUES (?, ?)",
            (poll_id, option)
        )

    conn.commit()
    return {"poll_id": poll_id}


@app.get("/polls/{poll_id}")
def get_poll(poll_id: int):
    cursor.execute("SELECT question FROM polls WHERE id = ?", (poll_id,))
    poll = cursor.fetchone()

    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    cursor.execute(
        "SELECT id, text, votes FROM options WHERE poll_id = ?",
        (poll_id,)
    )

    options = [
        {"option_id": o[0], "text": o[1], "votes": o[2]}
        for o in cursor.fetchall()
    ]

    return {
        "poll_id": poll_id,
        "question": poll[0],
        "options": options
    }


@app.post("/polls/{poll_id}/vote")
def vote(poll_id: int, vote: VoteRequest):
    cursor.execute(
        "SELECT 1 FROM votes WHERE poll_id = ? AND user_id = ?",
        (poll_id, vote.user_id)
    )

    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User already voted")

    cursor.execute(
        "UPDATE options SET votes = votes + 1 WHERE id = ? AND poll_id = ?",
        (vote.option_id, poll_id)
    )

    cursor.execute(
        "INSERT INTO votes (poll_id, user_id) VALUES (?, ?)",
        (poll_id, vote.user_id)
    )

    conn.commit()
    return {"message": "Vote recorded"}
