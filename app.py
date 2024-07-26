from fastapi import FastAPI, Request, HTTPException
import json
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import List, Union
import time
import os

from models import Note
from db import DB


class Message(BaseModel):
    id: Union[int, str]
    role: str
    content: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/message")
async def receive_message(request: Request):
    data = await request.json()

    os.makedirs("./messages", exist_ok=True)
    with open(f"./messages/{str(int(1000*time.time()))}.json", "w") as f:
        f.write(json.dumps(data))

    note_request = Note(content=str(data["message"]), node_id=str(uuid.uuid4()))

    make_note_response = await make_note(note_request)

    return JSONResponse(content={"message": f"Message received: {data}", "note": str(make_note_response.body)})


@app.post("/note")
async def make_note(note_request_node: Note) -> JSONResponse:
    note_request_node.saveFile()

    db = DB("db/notes-v0.0.1.db", "note")

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


class ChatRequest(BaseModel):
    history: List[Message]

class ChatResponse(BaseModel):
    message: Message

@ app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    print(request)
    response=Message(
        id=str(uuid.uuid4()),
        role="assistant",
        content=f"mirror {request.history[-1].content}"
    )
    return ChatResponse(message=response)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
