import uuid
import json
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from typing import Dict
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from .models import Message, Note, Node, Embedding, Link, ForceLink, ForceGraph
# todo factor out force graph into plugins
from .llm import llm
from .dbstuff import DBSQLite as DB
import os

HOST = os.environ["HOST_BROKER"]
PORT = int(os.environ["PORT_BROKER"])

app = FastAPI()

# factor out to test
db = DB()
db.create_table("nodes")
db.create_table("notes")
db.create_table("links")
db.create_table("embeddings")
del db

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class DependentNote(Note):
    depends_on: str

class ResponseMessage(BaseModel):
    response: Message

@app.post("/message")
async def message(message: Message) -> ResponseMessage:
    timestamp = int(1000 * time.time())
    print(message)

    message_note = Note(
        node_id=str(uuid.uuid4()),
        type="message",
        origin="message",
        author=message.role,
        content=message.content,
        timestamp=timestamp
    )

    await make_note(message_note)

    response_message = llm.api(messages=[
        {
            "role": "system",
            "content": "just answer in a natural way in all lowercase and dont be very concise no big fancy words. imagine im taking a note."
        },
        {
            "role": message.role,
            "content": message.content
        }
    ])

    timestamp = int(1000 * time.time())

    response_message_note = Note(
        node_id=str(uuid.uuid4()),
        type="message",
        origin="llm",
        author="llm",
        content=response_message,
        timestamp=timestamp
    )

    link = Link(
        node_id=str(uuid.uuid4()),
        source=message_note.node_id,
        target=response_message_note.node_id
    )

    await make_note(response_message_note)

    note_link = Note.from_link(link)

    await make_note(note_link)

    return {
        "message:response": {
            "role": "llm",
            "content": response_message
        }
    }


@app.post("/note")
async def make_note(note_request_node: Note):
    note_request_node.saveFile()

    note_embedding = Embedding.from_note(note_request_node)

    db = DB()

    try:
        db.insert(note_request_node)
        db.insert(note_embedding)
    except Exception as e:
        print(e)
        del db

    del db

@app.post("/link")
async def make_link(link: Link):
    db = DB()
    db.insert(link)
    del db



@app.get("/nodes")
async def get_nodes():
    db = DB()
    nodes: List[Node] = db.select_all()
    del db
    return JSONResponse(content={"nodes": [node.model_dump() for node in nodes]})


@app.get("/notes")
async def get_notes() -> List[Note]:
    db = DB()
    nodes: List[Node] = db.select_all_notes()
    del db
    return nodes


def cosine_similarity(v1, v2):
    import numpy as np

    v1 = np.array(v1)
    v2 = np.array(v2)

    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

class Graph(BaseModel):
    nodes: List[Note]
    links: List[Link]

@app.get("/graph/notes")
async def get_note_graph() -> Graph:
    """
    generate a graph of notes
    returns a { "nodes": [], "links": [] } object
    """
    # Fetch notes and parse the response
    notes_response = await get_notes()
    notes = json.loads(notes_response.body)["nodes"]
    links = json.loads(notes_response.body)["links"]

    return Graph(
        nodes=notes,
        links=links
    )

@app.get("/graph/notes/force")
# async def get_note_force_graph() -> Dict
# infer typing with pydantic
async def get_note_force_graph() -> ForceGraph:
    """
    Generate a graph of notes with similarity scores.
    - Creates a 2D array of similarity scores using cosine similarity for each pair of notes.
    - Returns a list of links with start and end nodes and a similarity score.
    """
    # Fetch notes and parse the response
    notes_response = await get_notes()
    # notes = json.loads(notes_response.body)["nodes"]
    notes = [Note.model_validate(note) for note in notes_response]

    links = []
    nodes = []

    for note_a in notes:
        nodes.append(note_a)
        for note_b in notes:
            if note_a.node_id != note_b.node_id:
                similarity = cosine_similarity(note_a.embedding.vector, note_b.embedding.vector)
                links.append(
                    ForceLink(
                        node_id=str(uuid.uuid4()),
                        source=note_a.node_id,
                        target=note_b.node_id,
                        similarity=similarity,
                        type="link:force"
                    )
                )
    

    return ForceGraph(
        node_id=str(uuid.uuid4()),
        version="0.0.1",
        type="graph:force",
        nodes=nodes,
        links=links
    )

if os.path.exists("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")


if __name__ == '__main__':
    import uvicorn
    print(f"Running on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
