# Notes API — a demo component "generated" by the Hermes agent (developer).
# A minimal in-memory notes CRUD service built on FastAPI.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from itertools import count

app = FastAPI(title="Notes API", version="1.0.0")

_notes: dict[int, dict] = {}
_ids = count(1)


class NoteIn(BaseModel):
    title: str
    body: str = ""


class Note(NoteIn):
    id: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes", response_model=list[Note])
def list_notes():
    return list(_notes.values())


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteIn):
    nid = next(_ids)
    rec = {"id": nid, **note.model_dump()}
    _notes[nid] = rec
    return rec


@app.get("/notes/{nid}", response_model=Note)
def get_note(nid: int):
    if nid not in _notes:
        raise HTTPException(status_code=404, detail="note not found")
    return _notes[nid]


@app.delete("/notes/{nid}", status_code=204)
def delete_note(nid: int):
    if _notes.pop(nid, None) is None:
        raise HTTPException(status_code=404, detail="note not found")
    return None
