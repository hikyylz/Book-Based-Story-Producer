from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import os
import sys

# Add current directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.analyzer import BookAnalyzer
from app.models.generator import StoryGenerator
from app.api_key import GEMINI_API_KEY

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

class StoryRequest(BaseModel):
    book_filename: str

class StoryProducerService:
    def __init__(self):
        self.analyzer = BookAnalyzer()
        self.generator = StoryGenerator(GEMINI_API_KEY)

    def produce(self, file_path: str) -> str:
        # 1. Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Book file not found")
        
        # 2. Analyze
        analysis_data = self.analyzer.analyze(text)
        
        # 3. Generate
        story = self.generator.generate(analysis_data)
        return story

# Service instance
print("Initializing Story Producer Service (Loading AI 🧠)...")
service = StoryProducerService()
print("Service Ready! 🚀")

@app.get("/")
async def read_root(request: Request):
    # List books in static/books
    books_dir = "static/books"
    books = []
    if os.path.exists(books_dir):
        books = [f for f in os.listdir(books_dir) if f.endswith(".txt") or f.endswith(".pdf")]
    
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@app.post("/produce-story")
async def produce_story(request: StoryRequest):
    file_path = os.path.join("static/books", request.book_filename)
    try:
        story = service.produce(file_path)
        return {"story": story}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
