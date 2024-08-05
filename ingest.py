from .dbstuff import DBSQLite as DB
from .models import Node, Note, Embedding, EmbeddedNote
from typing import List
import os

#factor out to init
db = DB()
db.create_table(tablename="nodes")
db.create_table(tablename="notes")
db.create_table(tablename="embeddings")
del db

def ingest_node(node: Node):
    print(f"Ingesting node {node.node_id}")
    print(node)
    db = DB()

    try:
        db.insert(node)
    except Exception as e:
        print(f"Error inserting node {node.node_id}")
        print(e)
        del db
        raise e

    del db

    return

def ingest_repo_notes(repo_path: str):
    #ingest notes with embedding
    # need to factor out embedding i think
    path_notes = []

    filenames = os.listdir(repo_path)
    for filename in filenames:
        if filename.endswith(".md"):
            path_notes.append(os.path.join(repo_path, filename))
    
    notes = []
    embeddings = []
    for path_note in path_notes:
        ## get author by file owner
        note_content=open(path_note, "r").read()

        note = Note.from_note(note_content, path_note)
        note.type = "note"

        # why do the embeddings all have the same id?
        note_embedding = Embedding.from_note(note=note)

        notes.append(note)
        embeddings.append(note_embedding)

    for i in range(len(notes)):
        ingest_node(notes[i])
        ingest_node(embeddings[i])

    embedded_notes = [EmbeddedNote.from_note_and_embedding(note, embedding) for note, embedding in zip(notes, embeddings)]

    return embedded_notes

def ingest_text_directory_without_embedding(repo_path: str) -> List[Note]:
    #ingest notes with embedding
    # need to factor out embedding i think
    path_notes = []

    filenames = os.listdir(repo_path)
    for filename in filenames:
        if filename.endswith(".md"):
            path_notes.append(os.path.join(repo_path, filename))
    
    notes = []
    for path_note in path_notes:
        ## get author by file owner
        note_content=open(path_note, "r").read()

        note = Note.from_note(note_content, path_note)
        note.type = "note"


        notes.append(note)

    for i in range(len(notes)):
        ingest_node(notes[i])

    return notes


if __name__=="__main__":
    ingest_repo_notes("./notes")
