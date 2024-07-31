from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from fastapi.staticfiles import StaticFiles

from models import Note, Node
from dbstuff import DBSQLite as DB
import os

HOST=os.environ["HOST"]
PORT=int(os.environ["PORT"])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    print(f"Running on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
