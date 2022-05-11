import os
import logging
import pathlib
import json
import sqlite3
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    db = sqlite3.connect('../db/mercari.sqlite3')
    cur = db.cursor()
    sql = "INSERT INTO items (name, category) VALUES (?, ?)"
    cur.execute(sql, (name, category,))
    db.commit()
    db.close()
    # with open("items.json") as f:
    #     df = json.load(f)
    # df["items"].append({"name": name, "category": category})
    # with open("items.json", "w") as f:
    #     json.dump(df, f, indent = 4)
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    db = sqlite3.connect('../db/mercari.sqlite3')
    cur = db.cursor()
    sql = "SELECT name, category FROM items"
    cur.execute(sql)
    items_list = cur.fetchall()
    db.close()
    return items_list
    # with open("items.json") as f:
    #     df = json.load(f)
    # return df

@app.get("/search")
def search_item(keyword: str):
    db = sqlite3.connect('../db/mercari.sqlite3')
    cur = db.cursor()
    sql = "SELECT name, category FROM items WHERE name=?"
    cur.execute(sql, (keyword,))
    docs = cur.fetchall()
    db.close()
    return docs

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
