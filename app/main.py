from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys
import hashlib
import time
import json
import asyncio

# Add current directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.analyzer import BookAnalyzer
from app.models.generator import StoryGenerator
from app.api_key import GEMINI_API_KEY
from app.utils.logger import story_logger

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

class StoryRequest(BaseModel):
    book_filename: str
    length: Optional[str] = "medium"
    style: Optional[str] = "same"

class StoryProducerService:
    def __init__(self):
        self.analyzer = BookAnalyzer()
        self.generator = StoryGenerator(GEMINI_API_KEY)
        self._analysis_cache = {}  # Cache book analysis results

    def produce(self, file_path: str, length: str = "medium", style: str = "same") -> dict:
        # 1. Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Book file not found")
        
        # 2. Check cache - has this book been analyzed before?
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if text_hash in self._analysis_cache:
            analysis_data = self._analysis_cache[text_hash]
        else:
            analysis_data = self.analyzer.analyze(text)
            self._analysis_cache[text_hash] = analysis_data
        
        # 3. Generate with options
        story = self.generator.generate(analysis_data, length=length, style=style)
        
        return {
            "story": story,
            "analysis": analysis_data
        }

    async def produce_with_progress(self, file_path: str, length: str = "medium", style: str = "same"):
        """Story generation with progress status - generator for SSE."""
        
        # Get book name
        book_name = os.path.basename(file_path)
        
        # Start logging session
        story_logger.start_session(book_name, length, style)
        
        try:
            # 1. File reading
            story_logger.log_step("File Reading")
            yield f"data: {json.dumps({'step': 1, 'status': 'Reading file...', 'progress': 5})}\n\n"
            await asyncio.sleep(0.05)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                story_logger.log_metric("file_size_bytes", len(text))
            except FileNotFoundError:
                story_logger.log_error("Book file not found", "File Reading")
                story_logger.end_session(success=False)
                yield f"data: {json.dumps({'error': 'Book file not found'})}\n\n"
                return
            
            # 2. Cache check
            text_hash = hashlib.md5(text.encode()).hexdigest()
            story_logger.log_metric("text_hash", text_hash)
            
            if text_hash in self._analysis_cache:
                story_logger.log_cache_hit(book_name)
                cache_msg = json.dumps({'step': 2, 'status': "Loading from cache...", 'progress': 50, 'cached': True})
                yield f"data: {cache_msg}\n\n"
                await asyncio.sleep(0.1)
                analysis_data = self._analysis_cache[text_hash]
            else:
                # 3. Text cleaning
                story_logger.log_step("Text Cleaning")
                yield f"data: {json.dumps({'step': 2, 'status': 'Cleaning text...', 'progress': 10})}\n\n"
                await asyncio.sleep(0.05)
                
                original_size = len(text)
                cleaned_text = await asyncio.to_thread(self.analyzer._clean_text, text)
                story_logger.log_text_stats(original_size, len(cleaned_text))
                
                # 4. Sampling
                story_logger.log_step("Sampling")
                yield f"data: {json.dumps({'step': 3, 'status': 'Sampling text...', 'progress': 20})}\n\n"
                await asyncio.sleep(0.05)
                
                samples = self.analyzer._get_strategic_samples(cleaned_text)
                total_sample_size = sum(len(s) for s in samples)
                story_logger.log_sampling(len(samples), self.analyzer.sample_size, total_sample_size)
                
                # 5. NLP Analysis
                story_logger.log_step("NLP Analysis")
                yield f"data: {json.dumps({'step': 4, 'status': 'Performing NLP analysis...', 'progress': 30})}\n\n"
                
                analysis_data = await asyncio.to_thread(
                    self.analyzer._analyze_samples, samples, cleaned_text
                )
                story_logger.log_analysis_results(analysis_data)
                
                # Save to cache
                self._analysis_cache[text_hash] = analysis_data
                
                story_logger.log_step("Analysis Completed")
                yield f"data: {json.dumps({'step': 5, 'status': 'Analysis completed!', 'progress': 60, 'analysis': analysis_data})}\n\n"
            
            # 6. Story generation
            story_logger.log_step("Story Generation")
            yield f"data: {json.dumps({'step': 6, 'status': 'Writing story...', 'progress': 70})}\n\n"
            await asyncio.sleep(0.05)
            
            story = await asyncio.to_thread(
                self.generator.generate, analysis_data, length, style
            )
            story_logger.log_story_generated(story)
            
            # 7. Completed
            story_logger.log_step("Completed")
            story_logger.end_session(success=True)
            
            yield f"data: {json.dumps({'step': 7, 'status': 'Completed!', 'progress': 100, 'story': story, 'analysis': analysis_data})}\n\n"
            
        except Exception as e:
            story_logger.log_error(str(e))
            story_logger.end_session(success=False)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

# Service instance
service = StoryProducerService()

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
        result = service.produce(
            file_path, 
            length=request.length, 
            style=request.style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/produce-story-stream")
async def produce_story_stream(book_filename: str, length: str = "medium", style: str = "same"):
    """SSE endpoint - real-time progress status."""
    file_path = os.path.join("static/books", book_filename)
    
    return StreamingResponse(
        service.produce_with_progress(file_path, length=length, style=style),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
