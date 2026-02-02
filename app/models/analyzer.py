import spacy
from textblob import TextBlob
from rake_nltk import Rake
import nltk
import re
from collections import Counter

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class BookAnalyzer:
    def __init__(self):
        # FASTER: Customized pipeline for NER and POS tagging only
        self.nlp = spacy.load('en_core_web_sm', disable=['parser', 'lemmatizer', 'textcat'])
        # Increase max_length limit for large books
        self.nlp.max_length = 2_000_000
        self.rake = Rake()
        
        # Sampling parameters - FASTER
        self.sample_size = 30_000  # 50KB -> 30KB (faster)
        self.num_samples = 4  # 5 -> 4 samples
        
        # Pre-defined word lists for mood words (instead of TextBlob calls)
        self.positive_mood_words = {
            'beautiful', 'happy', 'bright', 'wonderful', 'lovely', 'gentle', 'warm', 
            'sweet', 'peaceful', 'joyful', 'pleasant', 'delightful', 'charming', 
            'graceful', 'brilliant', 'glorious', 'magnificent', 'splendid', 'tender',
            'cheerful', 'radiant', 'serene', 'tranquil', 'blissful', 'vibrant'
        }
        self.negative_mood_words = {
            'dark', 'sad', 'cold', 'terrible', 'horrible', 'gloomy', 'bitter', 
            'harsh', 'painful', 'miserable', 'dreadful', 'wretched', 'bleak', 
            'grim', 'somber', 'melancholy', 'dreary', 'dismal', 'ominous',
            'sinister', 'tragic', 'mournful', 'desolate', 'haunting', 'fierce'
        }
        
        # ===== PRECOMPILE ALL REGEX PATTERNS =====
        self._compile_patterns()

    def _compile_patterns(self):
        """Precompile all regex patterns - for performance."""
        
        # === 1. GUTENBERG SPECIFIC ===
        self._gutenberg_start = re.compile(
            r'\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*|'
            r'START OF THE PROJECT GUTENBERG EBOOK',
            re.IGNORECASE | re.DOTALL
        )
        self._gutenberg_end = re.compile(
            r'\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*|'
            r'END OF THE PROJECT GUTENBERG EBOOK|'
            r'End of the Project Gutenberg EBook|'
            r'End of Project Gutenberg',
            re.IGNORECASE
        )
        
        # === 2. BOOK END MARKERS ===
        self._book_end_markers = re.compile(
            r'(?:^|\n)(?:'
            r'(?:THE\s+)?END\.?\s*$|'
            r'FINIS\.?\s*$|'
            r'~+\s*(?:THE\s+)?END\s*~+|'
            r'\*\s*\*\s*\*\s*(?:THE\s+)?END\s*\*\s*\*\s*\*'
            r')',
            re.IGNORECASE | re.MULTILINE
        )
        
        # === 3. PUBLISHER/PLATFORM INFO ===
        self._publisher_noise = re.compile(
            r'(?:'
            r'Project Gutenberg|\bGutenberg\b|'
            r'Amazon\.com|Kindle Edition|ASIN[:\s]+\w+|'
            r'\beBook\b|\bE-book\b|\bE-text\b|'
            r'Internet Archive|Archive\.org|Open Library|'
            r'Google Books|Digitized by Google|'
            r'HathiTrust|LibriVox|'
            r'Published by[^\n]*|'
            r'Printed (?:in|by)[^\n]*|'
            r'First (?:published|printed|edition)[^\n]*|'
            r'All rights reserved[^\n]*|'
            r'Copyright ©?[^\n]*|'
            r'ISBN[:\s]*[\d\-X]+|'
            r'Library of Congress[^\n]*'
            r')',
            re.IGNORECASE
        )
        
        # === 4. EDITORIAL NOTES ===
        self._editorial_notes = re.compile(
            r'(?:'
            r'Transcriber\'?s?\s+[Nn]ote[s]?[:\s][^\n]*|'
            r'Editor\'?s?\s+[Nn]ote[s]?[:\s][^\n]*|'
            r'Translator\'?s?\s+[Nn]ote[s]?[:\s][^\n]*|'
            r'Publisher\'?s?\s+[Nn]ote[s]?[:\s][^\n]*|'
            r'Produced by[^\n]*|'
            r'Prepared by[^\n]*|'
            r'Scanned by[^\n]*|'
            r'Digitized by[^\n]*|'
            r'Proofread by[^\n]*'
            r')',
            re.IGNORECASE
        )
        
        # === 5. FORMAT ARTIFACTS ===
        self._format_artifacts = re.compile(
            r'(?:'
            r'\[Illustration[^\]]*\]|'
            r'\[Footnote[^\]]*\]|'
            r'\[Note[^\]]*\]|'
            r'\[Page\s*\d+\]|'
            r'\[pg\s*\d+\]|'
            r'\[p\.\s*\d+\]|'
            r'\[Blank Page\]|'
            r'\[Missing[^\]]*\]|'
            r'\[Illegible[^\]]*\]|'
            r'\[unclear[^\]]*\]|'
            r'\[sic\]|'
            r'^\s*\d{1,4}\s*$|'
            r'^\s*[-—]\s*\d{1,4}\s*[-—]\s*$|'
            r'^[=\-_\*~#]{10,}$|'
            r'^[\.]{5,}$'
            r')',
            re.IGNORECASE | re.MULTILINE
        )
        
        # === 6. TECHNICAL INFO ===
        self._technical_info = re.compile(
            r'(?:'
            r'\bASCII\b|\bUTF-?8\b|\bUnicode\b|'
            r'Character set[^\n]*|'
            r'Encoding[:\s]+\w+|'
            r'www\.\w+\.\w+|'
            r'http[s]?://[^\s]+|'
            r'[\w\.-]+@[\w\.-]+\.\w+'
            r')',
            re.IGNORECASE
        )
        
        # === 7. WHITESPACE ADJUSTMENTS ===
        self._multi_newline = re.compile(r'\n{3,}')
        self._multi_space = re.compile(r' {2,}')

    def _clean_text(self, text):
        """General purpose text cleaning - works for ALL sources."""
        
        original_len = len(text)
        
        # 1. Check Gutenberg start/end markers
        match = self._gutenberg_start.search(text)
        if match:
            text = text[match.end():]
        
        match = self._gutenberg_end.search(text)
        if match:
            text = text[:match.start()]
        
        # 2. Find book end markers (THE END, FINIS etc.) - trim if in last 30%
        match = self._book_end_markers.search(text)
        if match and match.start() > len(text) * 0.7:
            text = text[:match.start()]
        
        # 3. Clean all noise patterns at once
        text = self._publisher_noise.sub('', text)
        text = self._editorial_notes.sub('', text)
        text = self._format_artifacts.sub('', text)
        text = self._technical_info.sub('', text)
        
        # 4. Normalize whitespace
        text = self._multi_newline.sub('\n\n', text)
        text = self._multi_space.sub(' ', text)
        text = text.strip()
        
        return text

    def _analyze_samples(self, samples, cleaned_text):
        """Analyze samples - separate method for SSE progress."""
        all_characters = Counter()
        all_mood_words = Counter()
        all_adjectives = Counter()
        all_verbs = Counter()
        
        # Batch processing with spaCy
        for doc in self.nlp.pipe(samples, batch_size=2):
            chars = self._extract_characters(doc)
            all_characters.update(chars)
            
            moods = self._extract_mood_words_fast(doc)
            all_mood_words.update(moods)
            
            for token in doc:
                if token.pos_ == 'ADJ':
                    all_adjectives[token.text.lower()] += 1
                elif token.pos_ == 'VERB':
                    all_verbs[token.text.lower()] += 1
        
        # Sentiment analysis
        sentiment_sample = cleaned_text[:20000]
        sentiments = self._analyze_sentiment(sentiment_sample)
        
        # Keywords
        keywords = self._extract_keywords(cleaned_text[:100000])
        
        return {
            'characters': dict(all_characters.most_common(10)),
            'sentiments': sentiments,
            'keywords': keywords,
            'mood_words': dict(all_mood_words.most_common(15)),
            'literary_features': {
                'common_adjectives': dict(all_adjectives.most_common(10)),
                'common_verbs': dict(all_verbs.most_common(10))
            }
        }

    def analyze(self, text):
        """Analyze text and extract data into categories - OPTIMIZED."""
        
        # General purpose text cleaning (for all sources)
        cleaned_text = self._clean_text(text)
        
        # Strategic sampling
        samples = self._get_strategic_samples(cleaned_text)
        
        # Analysis
        return self._analyze_samples(samples, cleaned_text)

    def _get_strategic_samples(self, text):
        """Get strategic samples from text - from beginning, middle and end."""
        text_len = len(text)
        
        # If text is already small, return as is
        if text_len <= self.sample_size:
            return [text]
        
        samples = []
        step = text_len // self.num_samples
        
        for i in range(self.num_samples):
            start = i * step
            end = min(start + self.sample_size, text_len)
            sample = text[start:end]
            
            # Find nearest period to avoid cutting in middle of sentence
            last_period = sample.rfind('.')
            if last_period > self.sample_size * 0.8:
                sample = sample[:last_period + 1]
            
            samples.append(sample)
        
        return samples

    def _extract_mood_words_fast(self, doc):
        """Fast mood word extraction - without TextBlob, using pre-defined lists."""
        mood_words = Counter()
        
        for token in doc:
            if token.pos_ in ['ADJ', 'ADV']:
                word_lower = token.text.lower()
                
                # Is it in pre-defined mood lists?
                if word_lower in self.positive_mood_words or word_lower in self.negative_mood_words:
                    mood_words[token.text] += 1
                # Or meaningful adjectives with 5+ characters
                elif len(word_lower) >= 6 and token.pos_ == 'ADJ' and word_lower.isalpha():
                    mood_words[token.text] += 1
        
        return mood_words

    def _extract_characters(self, doc):
        """Extract character names - returns Counter for aggregation."""
        characters = Counter()
        
        # Extended filtering list
        excluded_names = {
            # Platform names
            'gutenberg', 'project', 'ascii', 'ebook', 'kindle', 'amazon', 'google',
            # Book sections
            'chapter', 'contents', 'illustration', 'transcriber', 'volume', 'book',
            'introduction', 'preface', 'foreword', 'epilogue', 'appendix', 'index',
            # Roles
            'editor', 'translator', 'publisher', 'author', 'narrator',
            # Common false positives
            'god', 'lord', 'sir', 'madam', 'mr', 'mrs', 'miss', 'master', 'doctor'
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                name = ent.text.strip()
                name_lower = name.lower()
                
                # Filtering criteria
                if (name_lower not in excluded_names and 
                    len(name) > 1 and 
                    not name.isupper() and  # Not all uppercase
                    name[0].isupper()):  # First letter is uppercase
                    characters[name] += 1
        
        return characters

    def _analyze_sentiment(self, text):
        """Analyze overall sentiment."""
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,  # -1 to 1
            'subjectivity': blob.sentiment.subjectivity  # 0 to 1
        }

    def _extract_keywords(self, text):
        """Extract important keywords."""
        self.rake.extract_keywords_from_text(text)
        keywords = self.rake.get_ranked_phrases()
        
        # Extended noise filtering
        noise_words = {
            'gutenberg', 'project', 'ebook', 'ascii', 'kindle', 'transcriber',
            'copyright', 'published', 'edition', 'chapter', 'contents',
            'amazon', 'archive', 'google', 'library', 'digital', 'isbn',
            'translator', 'editor', 'introduction', 'preface', 'appendix'
        }
        
        filtered_keywords = [
            kw for kw in keywords 
            if not any(noise in kw.lower() for noise in noise_words)
        ]
        
        return filtered_keywords[:20]

    # Note: _extract_mood_words is now optimized as _extract_mood_words_fast
    # Note: _extract_literary_features is now done inline in analyze()