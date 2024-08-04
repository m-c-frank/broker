import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from fastapi.staticfiles import StaticFiles

from models import Message, Note, Node
from dbstuff import DBSQLite as DB
import os
import llm
import llmfun
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if ./static exists, serve it at /

class DependentNote(Note):
    depends_on: str
    

@app.post("/message")
async def message(message: Message) -> JSONResponse:
    timestamp = int(1000 * time.time())
    print(message)

    message_note = Note(
        node_id=str(uuid.uuid4()),
        type="message",
        origin="telegram",
        author=message.role,
        content=message.content,
        timestamp=timestamp
    )

    await make_note(message_note)

    messages = llmfun.define_russian_word(message.content)

    response_message = llm.api(messages)

    timestamp = int(1000 * time.time())
    response_message_note = DependentNote(
        node_id=str(uuid.uuid4()),
        type="message",
        origin="llm",
        author="llm",
        content=response_message,
        depends_on=message_note.node_id,
        timestamp=timestamp
    )

    await make_note(response_message_note)

    return JSONResponse(content={"message": response_message})


@app.post("/note")
async def make_note(note_request_node: Note) -> JSONResponse:
    note_request_node.saveFile()

    db = DB()

    try:
        db.select(note_request_node.node_id)
        # todo not implemented yet
        db.update(note_request_node)
    except AttributeError:
        db.insert(note_request_node)
    except ValueError:
        db.insert(note_request_node)

    del db

    return JSONResponse(content={"message": "Note created", "note": note_request_node.model_dump_json()})


@app.get("/nodes")
async def get_nodes():
    db = DB()
    nodes: List[Node] = db.select_all()
    del db
    return JSONResponse(content={"nodes": [node.model_dump() for node in nodes]})

@app.get("/notes")
async def get_notes():
    db = DB()
    nodes: List[Node] = db.select_all_notes()
    del db
    return JSONResponse(content={"nodes": [node.model_dump() for node in nodes]})

if os.path.exists("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
