from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, time
import psycopg

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "appuser")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # from secret via env

def get_conn():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        dbname=DB_NAME,
        password=DB_PASSWORD,
        autocommit=True,
    )

def init_db():
    # retry loop so we don't crash if DB isn't ready yet
    for _ in range(30):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS notes (
                            id SERIAL PRIMARY KEY,
                            text TEXT NOT NULL
                        )
                    """)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("DB not reachable after retries")

@app.on_event("startup")
def on_startup():
    if not DB_PASSWORD:
        raise RuntimeError("DB_PASSWORD not set")
    init_db()

class NoteIn(BaseModel):
    text: str

@app.get("/healthz")
def healthz():
    return "ok"

@app.post("/notes")
def create_note(n: NoteIn):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO notes(text) VALUES (%s) RETURNING id", (n.text,))
                note_id = cur.fetchone()[0]
                return {"id": note_id, "text": n.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes")
def list_notes():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, text FROM notes ORDER BY id ASC")
                rows = cur.fetchall()
                return [{"id": r[0], "text": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

