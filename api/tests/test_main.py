from fastapi.testclient import TestClient
import pytest
from models.model import NodeModel, Leaf
from main import add_childrens, pretty_print_node, read_leaves, app
from unittest import mock


LEAF_TEXT = "leaf text"
LEAF_RAW_PATH = "this/is/a/leaf"
DATABASE_STRING = "main.db"

client = TestClient(app)
fake_db = {}


def test_add_children():
    node = NodeModel(name="test")
    leaf = Leaf(path="leaf", text=LEAF_TEXT)
    add_childrens(node, leaf)
    assert node["childs"][0]["name"] == "leaf"
    assert node["childs"][0]["text"] == LEAF_TEXT


def test_pretty_print():
    expected_result = "test\\\n  this\\\n    is\\\n      a\\\n        leaf\\\n          leaf text\n"
    node = NodeModel(name="test")
    leaf = Leaf(path=LEAF_RAW_PATH, text=LEAF_TEXT)
    add_childrens(node, leaf)
    __add_to_db(node)
    result = pretty_print_node(node)
    assert result == expected_result


def test_read_leaves():
    node = NodeModel(name="test")
    leaf = Leaf(path=LEAF_RAW_PATH, text=LEAF_TEXT)
    add_childrens(node, leaf)
    __add_to_db(node)
    path, text = read_leaves(node, "leaf", set())
    assert path == "test/this/is/a/leaf"
    assert text == LEAF_TEXT


def test_add_node():
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].insert_one = mock.AsyncMock(
            return_value=fake_db["root"])
        response = client.post("/maps", json={"id": "test"})
        assert response.status_code == 201


def test_add_leaf_return_404_when_map_not_found():
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].find_one = mock.AsyncMock(return_value=None)
        response = client.post(
            "/maps/test/leafs", json={"path": LEAF_RAW_PATH, "text": LEAF_TEXT})
        assert response.status_code == 404


def test_read_leaf_return_200_and_correct_awnser():
    node = NodeModel(name="test")
    leaf = Leaf(path=LEAF_RAW_PATH, text=LEAF_TEXT)
    add_childrens(node, leaf)
    __add_to_db(node)
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].find_one = mock.AsyncMock(return_value=node)
        response = client.get("/maps/test/leafs/leaf")
        assert response.status_code == 200
        assert response.json() == {"path": LEAF_RAW_PATH, "text": LEAF_TEXT}


def test_read_leaf_return_404_when_map_not_found():
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].find_one = mock.AsyncMock(return_value=None)
        response = client.get("/maps/test/leafs/leaf")
        assert response.status_code == 404


def test_read_leaf_return_404_when_leaf_not_found():
    node = NodeModel(name="test")
    leaf = Leaf(path=LEAF_RAW_PATH, text=LEAF_TEXT)
    add_childrens(node, leaf)
    __add_to_db(node)
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].find_one = mock.AsyncMock(return_value=node)
        response = client.get("/maps/test/leafs/leaf2")
        assert response.status_code == 404


def test_pretty_print_return_404_when_map_not_found():
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].find_one = mock.AsyncMock(return_value=None)
        response = client.get("/prettyPrint/pretty")
        assert response.status_code == 404


def test_pretty_print_return_200_and_correct_awnser():
    node = NodeModel(name="test")
    leaf = Leaf(path=LEAF_RAW_PATH, text=LEAF_TEXT)
    add_childrens(node, leaf)
    __add_to_db(node)
    with mock.patch(DATABASE_STRING) as mock_db:
        mock_db["maps"].find_one = mock.AsyncMock(return_value=node)
        response = client.get("/prettyPrint/test")
        assert response.status_code == 200
        assert response.text == "test\\\n  this\\\n    is\\\n      a\\\n        leaf\\\n          leaf text\n"


@pytest.fixture(autouse=True)
def populate_db():
    __add_to_db(NodeModel(name="root", children=[]))
    node = NodeModel(name="test")
    leaf = Leaf(path=LEAF_RAW_PATH, text=LEAF_TEXT)
    add_childrens(node, leaf)
    yield


def __add_to_db(node):
    fake_db[node.name] = node
