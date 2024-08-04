from typing import Union, List
from pydantic import BaseModel, Field
import os
import time
import uuid
import yaml
import embedder


class Node(BaseModel):
    # id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # id_root: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # id_parent: str = Field(default_factory=lambda: str(uuid.uuid4()))
    #if is root node then id_root = id = id_parent
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "0.0.1"
    type: str = "node"

class Embedding(Node):
    type: str = "embedding"
    vector: List
    embedding_model: str

    @staticmethod
    def from_note(note: "Note") -> "Embedding":
        embedding_vector = embedder.embed_text(note.content, "all-minilm")
        embedding = Embedding(
            node_id=note.node_id,
            vector=embedding_vector,
            embedding_model="all-minilm"
        )
        return embedding


class Message(Node):
    role: str
    content: str


# also add date?
# sometimes the parsing is via date and it may not always work
# so if date exists and timestamp not then create timestamp from date and use that


class Note(Node):
    h0: str = "note"
    timestamp: Union[int, str] = Field(default_factory= lambda: str(int(1000* time.time())))
    type: str = "note"
    origin: str = "/notes"
    author: str = "mcfrank"
    content: str

    def frontmatter(self) -> str:
        lines = [
            "---",
            f"id: {self.node_id}",
            f"version: {self.version}",
            f"type: {self.type}",
            f"h0: {self.h0}",
            f"timestamp: {self.timestamp}",
            f"origin: {self.origin}",
            f"author: {self.author}",
            "---\n\n"
        ]

        return "\n".join(lines)
    
    def to_md(self) -> str:
        return self.frontmatter() + self.content
    
    def saveFile(self) -> None:
        os.makedirs("./notes", exist_ok=True)
        with open(f"./notes/{self.timestamp}.md", "w") as f:
            f.write(self.to_md())
    
    @staticmethod
    def from_note(note_content, note_path):
        parts = note_content.split("---")
        assert len(parts) == 3
        frontmatter_raw = parts[1]
        frontmatter = yaml.safe_load(frontmatter_raw)

        if "timestamp" not in frontmatter:
            tsfilename = None
            tsdate = None
            if "date" in frontmatter:
                #date: "2024-07-25T21:45:38+02:00"
                tsdate = int(time.mktime(time.strptime(frontmatter["date"], "%Y-%m-%dT%H:%M:%S%z")))
            if len(note_path.split("/")[-1].replace(".md","")) == len("1722093491207") and note_path.isdigit():
                tsfilename = int(note_path.split("/")[-1].replace(".md",""))

            if tsdate:
                frontmatter["timestamp"] = tsdate

            if tsfilename:
                frontmatter["timestamp"] = tsfilename
                


        return Note(
            **frontmatter,
            content=parts[2]
        )
    
    @staticmethod
    def from_chat_history(chat_history):
        "Markdown note from chat history"
        lines = []
        # timestamp=str(int(1000*time.time()))
        # for message in chat_history:
        #     lines.append(f"{message.role}: {message.content}")
        
        # return Note(
        #     content="\n".join(lines)
        #     type="note-chat",
        #     timestamp=timestamp
        # )
        timestamp=str(int(1000*time.time()))
        return Note(
            content="\n".join([f"{message.role}: {message.content}" for message in chat_history]),
            type="note-chat",
            timestamp=timestamp
        )


class EmbeddedNote(Note):
    embedding: Embedding

    @staticmethod
    def from_note_and_embedding(note: Note, embedding: Embedding) -> "EmbeddedNote":
        return EmbeddedNote(
            node_id=note.node_id,
            version=note.version,
            type=note.type,
            h0=note.h0,
            timestamp=note.timestamp,
            origin=note.origin,
            author=note.author,
            content=note.content,
            embedding=embedding
        )

if __name__=="__main__":
    note = Note(content="This is a note")
    print(note)
    print(note.to_md())
    note.saveFile()
    print