from fastapi import FastAPI, HTTPException
import asyncpg
import os, sys
import json
from pydantic import BaseModel

class ArticleIn(BaseModel):
    title: str
    content: str

# Ambil kredensial dari environment variables (atau cara lain yang aman)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD") 
if not DB_PASSWORD:
    print("ERROR: DB_PASSWORD environment variable is not set.")
    sys.exit(1)

DATABASE_URL = f"postgresql://postgres.invcmkrnevoihlyxitdg:{DB_PASSWORD}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres" 

app = FastAPI()

async def create_db_pool():
    app.state.pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20,
        statement_cache_size=0  # <-- Add this line
    )
async def close_db_pool():
    await app.state.pool.close()

@app.on_event("startup")
async def startup():
    await create_db_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()

async def load_data_from_json(filename: str = "articles_5.json"):
    """Loads data from a JSON file and inserts it into the database."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except UnicodeDecodeError:
        # Try cp1252 if utf-8 fails
        with open(filename, "r", encoding="cp1252") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON format in file: {filename}")
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the Articles API"}
@app.post("/articles/")
async def create_articles():
    """Inserts all articles from the JSON file into the database."""

    articles = await load_data_from_json()
    conn = await app.state.pool.acquire()
    try:
        for article in articles:
            await conn.execute(
                "INSERT INTO articles (title, content) VALUES ($1, $2)",
                article["title"],
                article["content"]
            )
        return {"message": "Articles inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)

@app.get("/articles/")
async def read_articles():
    """Retrieves all articles from the database."""
    conn = await app.state.pool.acquire()
    try:
        rows = await conn.fetch("SELECT id, title, content FROM articles")
        articles = [{"id": row["id"], "title": row["title"], "content": row["content"]} for row in rows]
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)

@app.get("/articles/{article_id}")
async def read_article(article_id: int):
    """Retrieves a specific article by ID."""
    conn = await app.state.pool.acquire()
    try:
        row = await conn.fetchrow("SELECT id, title, content FROM articles WHERE id = $1", article_id)
        if row:
            return {"id": row["id"], "title": row["title"], "content": row["content"]}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)

#add one post data content and title

@app.post("/one-article/")
async def create_article(article: ArticleIn):
    """Inserts a new article into the database."""
    conn = await app.state.pool.acquire()
    try:
        await conn.execute(
            "INSERT INTO articles (title, content) VALUES ($1, $2)",
            article.title,
            article.content
        )
        return {"message": "Article created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)

#add more data to db
@app.post("/add-more-data/")
async def add_more_data():
    """Adds more data to the database from a JSON file."""
    data = await load_data_from_json("articles_5.json")
    conn = await app.state.pool.acquire()
    try:
        for article in data:
            await conn.execute(
                "INSERT INTO articles (title, content) VALUES ($1, $2)",
                article["title"],
                article["content"]
            )
        return {"message": "More data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)


#find article by title matching
@app.get("/articles/search/{title}")
async def search_articles(title: str):
    """Searches for articles by title."""
    conn = await app.state.pool.acquire()
    try:
        rows = await conn.fetch("SELECT id, title, content FROM articles WHERE title ILIKE $1", f"%{title}%")
        if not rows:
            raise HTTPException(status_code=404, detail="No articles found with that title")
        articles = [{"id": row["id"], "title": row["title"], "content": row["content"]} for row in rows]
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)

#delete article by id
@app.delete("/articles/{article_id}")
async def delete_article(article_id: int):
    """Deletes an article by ID."""
    conn = await app.state.pool.acquire()
    try:
        result = await conn.execute("DELETE FROM articles WHERE id = $1", article_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Article not found")
        return {"message": "Article deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)

#update article by id
@app.put("/articles/{article_id}")
async def update_article(article_id: int, article: ArticleIn):
    """Updates an article by ID."""
    conn = await app.state.pool.acquire()
    try:
        result = await conn.execute(
            "UPDATE articles SET title = $1, content = $2 WHERE id = $3",
            article.title,
            article.content,
            article_id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Article not found")
        return {"message": "Article updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        await app.state.pool.release(conn)
