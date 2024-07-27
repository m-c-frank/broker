import dbstuff as db
import os
from models import Node, Note
import os

def ingest_node(node: Node):
    _db = db.DB()
    _db.create_table(tablename="notes")

    try:
        _db.select(node.node_id)
        # todo not implemented yet
        _db.update(node)
    except AttributeError:
        _db.insert(node)
    except ValueError:
        _db.insert(node)

    del _db

    return

def ingest_repo_notes(repo_path: str):
    path_notes = []

    filenames = os.listdir(repo_path)
    for filename in filenames:
        if filename.endswith(".md"):
            path_notes.append(os.path.join(repo_path, filename))
    
    notes = []
    for path_note in path_notes:
        ## get author by file owner
        note = Note.from_note(
            note_content=open(path_note, "r").read()
        )
        notes.append(note)

    for note in notes:
        ingest_node(note)

    return

if __name__=="__main__":
    ingest_repo_notes("./notes")
