from .models import Embedding, Note, Node, EmbeddedNote, Link, ForceLink
import json
from typing import List, Union
import sqlite3
import os

URL_DB = os.environ.get("URL_DB", "db/notes-v0.0.1.db")
if URL_DB == "db/notes-v0.0.1.db":
    os.makedirs(os.path.dirname(URL_DB), exist_ok=True)

class DBSQLite:
    # delete this
    type: str = "node"

    def __init__(self, url_db: str = URL_DB) -> None:
        """Initialize the database connection"""
        self.connection = sqlite3.connect(url_db)
        self.create_table()

    def create_table(self, tablename: Union[str, None] = None) -> None:
        """Create the node tables if they don't exist"""
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    version TEXT
                );
                """
            )

            if tablename == "notes":
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        node_id TEXT PRIMARY KEY,
                        h0 TEXT,
                        timestamp INTEGER,
                        origin TEXT,
                        author TEXT,
                        content TEXT,
                        FOREIGN KEY (node_id) REFERENCES nodes(id)
                    );
                    """
                )
            if tablename == "embeddings":
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS embeddings (
                        node_id TEXT PRIMARY KEY,
                        vector TEXT,
                        embedding_model TEXT,
                        FOREIGN KEY (node_id) REFERENCES nodes(id)
                    );
                    """
                )
            
            if tablename == "links":
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS links (
                        node_id TEXT PRIMARY KEY,
                        source TEXT,
                        target TEXT,
                        force REAL,
                        FOREIGN KEY (node_id) REFERENCES nodes(id)
                    );
                    """
                )

    def insert(self, node: Node) -> None:
        print(node.node_id)
        print(node.type)
        """Insert a new node into the databases"""
        with self.connection:
            type_tags = node.type.split(":")
            if "link" in type_tags:
                if not isinstance(node, Link):
                    raise ValueError(f"Expected Link, got {type(node)}")

                self.connection.execute(
                    """
                    INSERT INTO nodes (id, type, version)
                    VALUES (?, ?, ?);
                    """,
                    (node.node_id, node.type, node.version)
                )

                if "force" in type_tags:
                    if not isinstance(node, ForceLink):
                        raise ValueError(f"Expected ForceLink, got {type(node)}")

                    self.connection.execute(
                        """
                        INSERT INTO links (node_id, source, target, force)
                        VALUES (?, ?, ?, ?);
                        """,
                        #todo is to factor out node.similarity from force nodes
                        (node.node_id, node.source, node.target, node.similarity)
                    )
                else:
                    self.connection.execute(
                        """
                        INSERT INTO links (node_id, source, target)
                        VALUES (?, ?, ?);
                        """,
                        (node.node_id, node.source, node.target)
                    )

            if "note" in type_tags:
                if not isinstance(node, Note):
                    raise ValueError(f"Expected Note, got {type(node)}")

                self.connection.execute(
                    """
                    INSERT INTO nodes (id, version, type)
                    SELECT ?, ?, ?
                    """,
                    (node.node_id, node.version, node.type)
                )

                self.connection.execute(
                    """
                    INSERT INTO notes (node_id, h0, timestamp, origin, author, content)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (node.node_id, node.h0, node.timestamp, node.origin, node.author, node.content)
                )

            if "embedding" in type_tags:
                if not isinstance(node, Embedding):
                    raise ValueError(f"Expected Embedding, got {type(node)}")
                # check that corresponding node exists
                cursor = self.connection.execute(
                    """
                    SELECT id
                    FROM nodes
                    WHERE id = ?;
                    """,
                    (node.node_id,)
                )
                if not cursor.fetchone():
                    raise ValueError(f"No node with ID {node.node_id}")

                self.connection.execute(
                    """
                    INSERT INTO embeddings (node_id, vector, embedding_model)
                    VALUES (?, ?, ?);
                    """,
                    (node.node_id, json.dumps(node.vector), node.embedding_model)
                )


    def select(self, node_id: str) -> Node:
        """Select a node by its ID."""
        cursor = self.connection.execute(
            """
            SELECT id, type, version
            FROM nodes
            WHERE id = ?;
            """,
            (node_id,)
        )
        row = cursor.fetchone()
        if not row:
            # raise ValueError(f"No node with ID {node_id}")
            return None

        node = Node(node_id=row[0], type=row[1], version=row[2])
        
        if node.type == "note":
            cursor = self.connection.execute(
                """
                SELECT node_id, h0, timestamp, origin, author, content
                FROM notes
                WHERE node_id = ?;
                """,
                (node_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No note with ID {node_id}")
            note = Note(node_id=row[0], h0=row[1], timestamp=row[2], origin=row[3], author=row[4], content=row[5], type=node.type, version=node.version)
            # check if nodeid has embedding
            cursor = self.connection.execute(
                """
                SELECT node_id, vector, embedding_model
                FROM embeddings
                WHERE node_id = ?;
                """,
                (node_id,)
            )
            row = cursor.fetchone()
            if not row:
                return note
            
            vector = json.loads(row[1])
            assert isinstance(vector, list)
            assert isinstance(vector[0], float) or len(vector[0]) == 0
            embedding = Embedding(node_id=row[0], vector=row[1], embedding_model=row[2], type="embedding", version=node.version)
            # unpack note into embedded note
            embeddedNote = EmbeddedNote.from_note_and_embedding(note, embedding)

            return embeddedNote


    def get_all_ids(self) -> List[str]:
        """Get all the IDs of the nodes"""
        cursor = self.connection.execute(
            """
            SELECT id
            FROM nodes;
            """
        )
        return [row[0] for row in cursor.fetchall()]

    def select_all(self) -> List[Node]:
        """Get all the nodes"""
        nodes = []
        cursor = self.connection.execute(
            """
            SELECT id, type, version
            FROM nodes;
            """
        )
        rows = cursor.fetchall()
        for row in rows:
            nodes.append(Node(node_id=row[0], type=row[1], version=row[2]))
        return nodes

    def select_all_notes(self) -> List[Note]:
        """Get all the notes"""
        notes = []
        cursor = self.connection.execute(
            """
SELECT 
    nodes.id, 
    nodes.type, 
    nodes.version, 
    notes.node_id, 
    notes.h0, 
    notes.timestamp, 
    notes.origin, 
    notes.author, 
    notes.content,
    embeddings.vector,
    embeddings.embedding_model
FROM 
    nodes
JOIN 
    notes 
ON 
    nodes.id = notes.node_id
JOIN
    embeddings
ON
    nodes.id = embeddings.node_id;
            """
        )
        rows = cursor.fetchall()
        for row in rows:
            note = Note(node_id=row[3], h0=row[4], timestamp=row[5], origin=row[6], author=row[7], content=row[8], type=row[1], version=row[2])
            embedding = Embedding(node_id=row[3], vector=json.loads(row[9]), embedding_model=row[10], version=row[2])
            embedded_note = EmbeddedNote.from_note_and_embedding(note, embedding)
            notes.append(embedded_note)
        return notes

    def __del__(self) -> None:
        """Ensure the database connection is closed when the object is deleted."""
        self.connection.close()
