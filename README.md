This repo is about a self made project.
It is a book based story producer.
If a person wants to read a short story regarding to a literary book, They are able to create a shorter version of it. The produced story must contain same mood, features and vibe of the original literary book. So person would have an idea what the book make them feels like.

# Book-Based Story Producer

This project takes a novel in PDF or TXT format as input, analyzes the text, and extracts the literary identity of the book (character names, emotions, atmosphere, important words). It then uses AI to generate a new story that matches the literary style, without giving the original book to the AI—only the extracted data.

## Features

- PDF/TXT file reading
- Text analysis (NER, sentiment, keyword extraction)
- Data categorization
- AI-based story generation

## Setup

1. Install requirements:

   ```
   pip install -r requirements.txt
   ```

2. Download Spacy model:

   ```
   python -m spacy download en_core_web_sm
   ```

3. Download NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt_tab')"
   ```

## Usage

1. Define your Gemini API key in `api_key.py`:

   ```python
   GEMINI_API_KEY = "your-gemini-api-key"
   ```

2. Run the Python script:

   ```python
   from main import StoryProducer

   producer = StoryProducer()
   producer.analyze_book('your_book.pdf')  # or .txt
   producer.generate_story('output_story.txt')
   ```

3. Alternatively, edit and run example.py.

## Features

- **PDF/TXT Reading:** pdfplumber for PDF, standard reading for TXT.
- **Text Analysis:**
  - NER for character names (spaCy).
  - Sentiment analysis (TextBlob).
  - Keyword extraction (RAKE).
  - Mood/Atmosphere words (ADJ/ADV with sentiment).
  - Literary features (common adjectives, verbs).
- **Story Generation:** Google Gemini generates original stories from analysis data.

## Output

- `analysis_data.json`: Analysis data.
- `generated_story.txt`: Generated story.

## Notes

- Currently optimized for English texts.
- May need performance improvements for large files.
- Requires Google Gemini API credits.
