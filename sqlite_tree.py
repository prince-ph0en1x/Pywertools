import sqlite3
import pickle
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from cachetools import LRUCache

Base = declarative_base()

# ---------- Tree Node Table ----------
class TreeNode(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('nodes.id'), nullable=True)
    data_blob = Column(LargeBinary)

    children = relationship("TreeNode", cascade="all, delete-orphan", backref="parent")

# ---------- Tree Manager ----------
class LazyTree:
    def __init__(self, db_url='sqlite:///tree.db', cache_size=10):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.cache = LRUCache(maxsize=cache_size)

    def add_node(self, name, data, parent_id=None):
        session = self.Session()
        node = TreeNode(name=name, parent_id=parent_id, data_blob=pickle.dumps(data))
        session.add(node)
        session.commit()
        session.close()
        return node.id

    def get_node_data(self, node_id):
        if node_id in self.cache:
            return self.cache[node_id]

        session = self.Session()
        node = session.query(TreeNode).filter_by(id=node_id).first()
        session.close()

        if node is None:
            raise ValueError("Node not found")

        data = pickle.loads(node.data_blob)
        self.cache[node_id] = data
        return data

    def print_tree(self, node_id=None, level=0):
        session = self.Session()
        nodes = session.query(TreeNode).filter_by(parent_id=node_id).all()
        for node in nodes:
            print("  " * level + f"- {node.name} (id: {node.id})")
            self.print_tree(node.id, level + 1)
        session.close()

# ---------- Usage Example ----------
if __name__ == "__main__":
    tree = LazyTree(cache_size=3)

    root_id = tree.add_node("Root", {"value": 1})
    child1_id = tree.add_node("Child 1", {"value": 10}, parent_id=root_id)
    child2_id = tree.add_node("Child 2", {"value": 20}, parent_id=root_id)
    gchild1_id = tree.add_node("Grandchild 1", {"value": 100}, parent_id=child1_id)

    print("\nTree structure:")
    tree.print_tree()

    print("\nAccessing node data:")
    print(tree.get_node_data(child1_id))   # Cached
    print(tree.get_node_data(child2_id))   # Cached
    print(tree.get_node_data(gchild1_id))  # Cached — triggers LRU eviction if cache size exceeded

    print("\nAccessing again to see cache reuse:")
    print(tree.get_node_data(child1_id))   # Might trigger re-load if evicted
