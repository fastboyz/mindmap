import os
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
import motor.motor_asyncio
from fastapi.responses import JSONResponse, PlainTextResponse

from models.model import NodeModel, Leaf, TreeCreate

import queue

MIND_MAP_NOT_FOUND = "Mind map not found"

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URI"])
db = client.mindmap


@app.post("/maps")
async def create(node: TreeCreate):
    head = jsonable_encoder(NodeModel(name=node["id"]))
    await db["maps"].insert_one(head)
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@app.post("/maps/{id}/leafs")
async def add_leaf(id: str, leaf: Leaf):
    head = await db["maps"].find_one({"name": id})
    if not head:
        raise HTTPException(status_code=404, detail=MIND_MAP_NOT_FOUND)
    add_childrens(head, leaf)
    await db["maps"].update_one({"_id": head['_id']}, {"$set": head})
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get("/maps/{map_id}/leafs/{leaf_id}")
async def read_leaf(map_id: str, leaf_id: str):
    head = await db["maps"].find_one({"name": map_id})
    if not head:
        raise HTTPException(status_code=404, detail=MIND_MAP_NOT_FOUND)
    path, text = read_leaves(head, leaf_id, set())
    if path is None:
        raise HTTPException(status_code=404, detail="Leaf not found")
    path = path.replace(head["name"]+'/', '')
    return JSONResponse(status_code=status.HTTP_200_OK, content={"path": path, "text": text})


@app.get("/prettyPrint/{map_id}")
async def pretty_print(map_id: str):
    head = await db["maps"].find_one({"name": map_id})
    if not head:
        raise HTTPException(status_code=404, detail=MIND_MAP_NOT_FOUND)
    return PlainTextResponse(status_code=status.HTTP_200_OK, content=pretty_print_node(head))


def pretty_print_node(head, indent=0):
    res = ""
    stack = [(head, indent)]
    while len(stack) > 0:
        node, indent = stack.pop()
        res += "  " * indent + node["name"] + '\\\n'
        if node["text"]:
            res += "  " * (indent+1) + node["text"] + '\n'
        for child in node["childs"]:
            stack.append((child, indent + 1))
    return res


def add_childrens(head: NodeModel, leaf: Leaf) -> NodeModel:
    leaves = leaf.path.split('/')
    for id, data in enumerate(leaves):
        found = recursive_find(head, data)
        node = NodeModel(name=data)
        if id == len(leaves) - 1:
            node.text = leaf.text
        if found is None:
            head['childs'].append(dict(node))
            head = node
        else:
            head = found


def recursive_find(head, data):
    if head['name'] == data:
        return head
    for child in head['childs']:
        if child['name'] == data:
            return child
        else:
            return recursive_find(child, data)
    return None


def read_leaves(head, data, visited):
    fifo = queue.Queue()
    fifo.put((head, head["name"], ""))
    while not fifo.empty():
        current, path, text = fifo.get()
        if current["name"] == data:
            return path, text
        for child in current['childs']:
            if child["name"] not in visited:
                visited.add(child["name"])
                fifo.put((child, path + '/' + child["name"], child["text"]))
    return None, None
