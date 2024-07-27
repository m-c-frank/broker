from models import Note, Node
from typing import List
import sqlite3
import os

URL_DB = os.environ.get("URL_DB", "db/notes-v0.0.1.db")
if URL_DB == "db/notes-v0.0.1.db":
    os.makedirs(os.path.dirname(URL_DB), exist_ok=True)

class DBSQLite:
    type: str = "node"

    def __init__(self, url_db=URL_DB) -> None:
        """initialize the database connection"""
        self.connection = sqlite3.connect(url_db)
        self.create_table()

    def create_table(self, tablename=None) -> None:
        """create the node tables if they dont exist"""
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

            if tablename is not None:
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

    def insert(self, node: Node) -> None:
        """insert a new node into the databases"""
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO nodes (id, version, type)
                VALUES (?, ?, ?);
                """,
                (node.node_id, node.version, node.type)
            )
            if node.type == "note":
                if not isinstance(node, Note):
                    raise ValueError(f"Expected Note, got {type(node)}")
                
                with self.connection:
                    self.connection.execute(
                        """
                        INSERT INTO notes (node_id, h0, timestamp, origin, author, content)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        (node.node_id, node.h0, node.timestamp, node.origin, node.author, node.content)
                    )


    def select(self, node_id: str) -> Node:
        """Select a node by its ID."""
        node = None
        cursor = self.connection.execute(
            """
            SELECT id, type, version
            FROM nodes
            WHERE id = ?;
            """,
            (str(node_id),)
        )
        row = cursor.fetchone()
        if row:
            node = Node(node_id=row[0], type=row[1], version=row[2])
        else:
            raise ValueError(f"No node with ID {node_id}")
        
        if node.type == "note":
            cursor = self.connection.execute(
                """
                SELECT node_id, h0, timestamp, origin, author, content
                FROM notes
                WHERE node_id = ?;
                """,
                (str(node_id),)
            )
            row = cursor.fetchone()
            if row:
                node = Note(node_id=row[0], h0=row[1], timestamp=row[2], origin=row[3], author=row[4], content=row[5], type="note", version=node.version)
            else:
                raise ValueError(f"No note with ID {node_id}")

        if node is None:
            raise ValueError(f"No node with ID {node_id}")

        return node


    def get_all_ids(self) -> List[Node]:
        """get all the ids of the nodes"""
        cursor = self.connection.execute(
            """
            SELECT id
            FROM nodes;
            """
        )
        return [row[0] for row in cursor.fetchall()]
    
    def select_all(self) -> List[Node]:
        """get all the nodes"""
        nodes = []
        cursor = self.connection.execute(
            """
            SELECT id, type, version
            FROM nodes;
            """
        )

        rows = cursor.fetchall()
        if rows:
            for row in rows:
                nodes.append(Node(node_id=row[0], type=row[1], version=row[2]))
        
        if not nodes:
            raise ValueError(f"No nodes found")

        return nodes

    def select_all_notes(self) -> List[Note]:
        """get all the notes"""
        nodes = []
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
                    notes.content
                FROM 
                    nodes
                JOIN 
                    notes 
                ON 
                    nodes.id = notes.node_id;
            """
        )

        rows = cursor.fetchall()
        if rows:
            for row in rows:
                nodes.append(Note(note_id=row[3], h0=row[4], timestamp=str(row[5]), origin=row[6], author=row[7], content=row[8], type=row[1], version=row[2]))
            
        if not nodes:
            raise ValueError(f"No nodes found")

        return nodes

    def __del__(self) -> None:
        """Ensure the database connection is closed when the object is deleted."""
        self.connection.close()