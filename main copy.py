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

#add post data content and title
@app.post("/articles")
def create_article(article: dict):
    if "title" not in article or "content" not in article:
        return JSONResponse(status_code=400, content={"error": "Title and content are required"})
    
    articles_data.append(article)
    with open("articles_5.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)
    
    return JSONResponse(status_code=201, content=article)