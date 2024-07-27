from models import Message, Note, Node
from typing import List
import os
import sqlite3


class DB:
    type: str = "node"

    def __init__(self, db_name: str, _type: str = "node", path_db: str = "db/") -> None:
        """initialize the database connection"""

        self.db_path = os.path.join(path_db, db_name)

        self.type = _type

        if self.type != "node":
            os.makedirs(path_db, exist_ok=True)
            self.db_path_nodes = os.path.join(path_db, "nodes-v0.0.1.db")

        self.connection_nodes = sqlite3.connect(self.db_path_nodes)
        self.connection = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self) -> None:
        """create the node tables if they dont exist"""
        if self.type != "node":
            with self.connection:
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id TEXT PRIMARY KEY,
                        nodenode_id TEXT,
                        h0 TEXT,
                        timestamp INTEGER,
                        origin TEXT,
                        author TEXT,
                        content TEXT,
                        FOREIGN KEY (node_id) REFERENCES nodes(id)
                    );
                    """
                )

        with self.connection_nodes:
            self.connection_nodes.execute(
                """
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    version TEXT
                );
                """
            )

    def insert(self, node: Node) -> None:
        """Insert a new node into the databases."""
        if self.type != "node":
            if self.type == "note":
                if not isinstance(node, Note):
                    raise ValueError(f"Expected Note, got {type(node)}")
                
                with self.connection:
                    self.connection.execute(
                        """
                        INSERT INTO notes (id, node_id, h0, timestamp, origin, author, content)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (node.node_id, node.node_id, node.h0, node.timestamp, node.origin, node.author, node.content)
                    )

        with self.connection_nodes:
            self.connection_nodes.execute(
                """
                INSERT INTO nodes (id, version, type)
                VALUES (?, ?, ?);
                """,
                (node.node_id, node.version, node.type)
            )

    def select(self, node_id: str) -> List[Node]:
        """Select a node by its ID."""
        nodes = []
        print(node_id)
        cursor = self.connection_nodes.execute(
            """
            SELECT id, type, version
            FROM nodes
            WHERE id = ?;
            """,
            (str(node_id),)
        )
        row = cursor.fetchone()
        if row:
            nodes.append(Node(node_id=row[0], type=row[1], version=row[2]))
        else:
            raise ValueError(f"No node with ID {node_id}")
        
        if self.type != "node":
            if self.type == "note":
                cursor = self.connection.execute(
                    """
                    SELECT id, node_id, h0, timestamp, origin, author, content
                    FROM notes
                    WHERE id = ?;
                    """,
                    (str(node_id),)
                )
                row = cursor.fetchone()
                if row:
                    nodes.append(Note(node_id=row[0], nodenode_id=row[1], h0=row[2], timestamp=row[3], origin=row[4], author=row[5], content=row[6]))
                else:
                    raise ValueError(f"No note with ID {node_id}")

        return nodes


    def select_all_ids(self) -> List[Message]:
        """get all the ids of the nodes"""
        cursor = self.connection_nodes.execute(
            """
            SELECT id
            FROM nodes;
            """
        )
        return [row[0] for row in cursor.fetchall()]
    
    def select_all(self) -> List[Node]:
        """get all the nodes"""
        nodes = []
        cursor = self.connection_nodes.execute(
            """
            SELECT id, type, version
            FROM nodes;
            """
        )
        for row in cursor.fetchall():
            nodes.append(Node(node_id=row[0], type=row[1], version=row[2]))
        return nodes

    # not required as of now
    # not required as of now
    # def update(self, old_nodes: List[Node], new_nodes: List[Node]) -> None:
        """Update a node in the database."""
        # retrieved_old_message = self.select(old_message.id)
        # if 

        # if retrieved_old_message != old_message:
        #     raise ValueError(f"Out of sync: {retrieved_old_message} != {old_message}")
        
        # if retrieved_old_message == new_message:
        #     return

        # with self.connection:
        #     self.connection.execute(
        #         """
        #         UPDATE messages
        #         SET role = ?, content = ?, version = ?
        #         WHERE id = ?;
        #         """,
        #         (new_message.role, new_message.content, new_message.version, new_message.id)
        #     )

    # def delete(self, message: Message) -> None:
    #     """Delete a message from the database."""
    #     with self.connection:
    #         self.connection.execute(
    #             """
    #             DELETE FROM messages
    #             WHERE id = ?;
    #             """,
    #             (message.id,)
    #         )

    # def delete_all(self) -> None:
    #     """Delete all messages from the database."""
    #     with self.connection:
    #         self.connection.execute(
    #             """
    #             DELETE FROM messages;
    #             """
    #         )

    def __del__(self) -> None:
        """Ensure the database connection is closed when the object is deleted."""
        self.connection.close()
        self.connection_nodes.close()