from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# Load data from the JSON file
with open("articles_5.json", "r", encoding="utf-8") as f:
    articles_data = json.load(f)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Articles API"}

@app.get("/articles")
def get_articles():
    return JSONResponse(content=articles_data)

@app.get("/articles/{index}")
def get_article(index: int):
    if 0 <= index < len(articles_data):
        return JSONResponse(content=articles_data[index])
    return {"error": "Article not found"}
