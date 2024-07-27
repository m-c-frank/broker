from dbstuff import DBSQLite as DB
from models import Node, Note
import os

def ingest_node(node: Node):
    db = DB()
    db.create_table(tablename="notes")

    try:
        db.select(node.node_id)
        # todo not implemented yet
        db.update(node)
    except AttributeError:
        db.insert(node)
    except ValueError:
        db.insert(node)

    del db

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
