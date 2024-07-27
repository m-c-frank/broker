from typing import Dict
from pydantic import BaseModel, Field
import os
import time
import uuid


class Node(BaseModel):
    # id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # id_root: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # id_parent: str = Field(default_factory=lambda: str(uuid.uuid4()))
    #if is root node then id_root = id = id_parent
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "0.0.1"
    type: str = "node"

class Message(Node):
    role: str
    content: str


# also add date?
# sometimes the parsing is via date and it may not always work
# so if date exists and timestamp not then create timestamp from date and use that

class Note(Node):
    h0: str = "note"
    timestamp: str = Field(default_factory= lambda: str(int(1000* time.time())))
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
    

if __name__=="__main__":
    note = Note(content="This is a note")
    print(note)
    print(note.to_md())
    note.saveFile()
    print