import os
import logging
import pathlib
#import json
import sqlite3
import hashlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.DEBUG
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# def hash_image(file):
#     with open(file, 'rb') as f:
#         sha256 = hashlib.sha256(f.read()).hexdigest()
#     return sha256

def hash_image(file):
    hs = hashlib.sha256(file.encode()).hexdigest()
    return hs+'.jpg'

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    con = sqlite3.connect('../db/mercari.sqlite3')
    cur = con.cursor()
    category_id = cur.execute("SELECT id FROM category WHERE category = ?", (category,)).fetchall()
    sql = "INSERT INTO items (name, category_id, image) VALUES (?, ?, ?)"
    cur = con.cursor()
    cur.execute(sql, (name, category_id[0][0], hash_image(image) + ".jpg",))
    #cur.execute(sql, (name, category_id, image))
    con.commit()
    con.close()
    # with open("items.json") as f:
    #     df = json.load(f)
    # df["items"].append({"name": name, "category": category})
    # with open("items.json", "w") as f:
    #     json.dump(df, f, indent = 4)
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    con = sqlite3.connect('../db/mercari.sqlite3')
    con.row_factory = dict_factory
    cur = con.cursor()
    sql = '''SELECT items.name, category.category, items.image 
        FROM items, category 
        WHERE items.category_id = category.id'''
    cur.execute(sql)
    items_dic = {}
    items_dic["items"] = cur.fetchall()
    con.close()
    return items_dic
    # with open("items.json") as f:
    #     df = json.load(f)
    # return df

@app.get("/search")
def search_item(keyword: str):
    con = sqlite3.connect('../db/mercari.sqlite3')
    con.row_factory = dict_factory
    cur = con.cursor()
    sql = '''SELECT items.name, category.category, items.image 
        FROM items
        LEFT JOIN category 
        ON items.category_id=category.id 
        WHERE items.name=?'''
    cur.execute(sql, (keyword,))
    items_dic = {}
    items_dic["items"] = cur.fetchall()
    con.close()
    return items_dic

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.get("/items/{item_id}")
def get_item_from_id(item_id):
    con = sqlite3.connect('../db/mercari.sqlite3')
    con.row_factory = dict_factory
    cur = con.cursor()
    sql = "SELECT name, category, image FROM items WHERE id = ?"
    cur.execute(sql, (item_id,))
    item = cur.fetchall()
    con.close()
    return item[0]
