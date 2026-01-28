import spacy
from textblob import TextBlob
from rake_nltk import Rake
import nltk
import re

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
        self.nlp = spacy.load('en_core_web_sm')
        self.rake = Rake()
        
        # Gutenberg temizleme pattern'leri
        self.gutenberg_start_markers = [
            r'\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*',
            r'\*\*\*\s*START OF THIS PROJECT GUTENBERG.*?\*\*\*',
            r'START OF THE PROJECT GUTENBERG EBOOK',
        ]
        
        self.gutenberg_end_markers = [
            r'\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*',
            r'\*\*\*\s*END OF THIS PROJECT GUTENBERG.*?\*\*\*',
            r'END OF THE PROJECT GUTENBERG EBOOK',
            r'End of the Project Gutenberg EBook',
            r'End of Project Gutenberg',
        ]
        
        # Temizlenecek Gutenberg ile ilgili kelimeler/ifadeler
        self.gutenberg_noise_patterns = [
            r'Project Gutenberg',
            r'Gutenberg',
            r'eBook',
            r'E-text',
            r'ASCII',
            r'www\.gutenberg\.org',
            r'gutenberg\.org',
            r'promo\.net',
            r'Produced by.*',
            r'Transcriber[\'s]? [Nn]ote.*',
            r'\[Illustration.*?\]',
            r'\[Footnote.*?\]',
        ]

    def _clean_gutenberg_text(self, text):
        """Project Gutenberg'e özgü başlık, lisans ve meta verileri temizler."""
        
        # 1. Başlangıç marker'ını bul ve öncesini sil
        for pattern in self.gutenberg_start_markers:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                text = text[match.end():]
                break
        
        # 2. Bitiş marker'ını bul ve sonrasını sil
        for pattern in self.gutenberg_end_markers:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                text = text[:match.start()]
                break
        
        # 3. Kalan Gutenberg referanslarını temizle
        for pattern in self.gutenberg_noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 4. Çoklu boşlukları ve satır sonlarını düzenle
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # 5. Baştaki ve sondaki boşlukları temizle
        text = text.strip()
        
        return text

    def analyze(self, text):
        """Analyze text and extract data into categories."""
        
        # Önce Gutenberg kirliliğini temizle
        cleaned_text = self._clean_gutenberg_text(text)
        
        doc = self.nlp(cleaned_text)

        # Characters (NER)
        characters = self._extract_characters(doc)

        # Sentiments
        sentiments = self._analyze_sentiment(cleaned_text)

        # Keywords
        keywords = self._extract_keywords(cleaned_text)

        # Mood/Atmosphere words (emotional words)
        mood_words = self._extract_mood_words(doc)

        # Literary features (common adjectives, verbs)
        literary_features = self._extract_literary_features(doc)

        return {
            'characters': characters,
            'sentiments': sentiments,
            'keywords': keywords,
            'mood_words': mood_words,
            'literary_features': literary_features
        }

    def _extract_characters(self, doc):
        """Extract character names."""
        characters = []
        
        # Filtrelenecek isimler (Gutenberg veya genel kirlilik)
        excluded_names = {
            'gutenberg', 'project', 'ascii', 'ebook', 'kindle',
            'chapter', 'contents', 'illustration', 'transcriber'
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                name = ent.text.strip()
                # Küçük harfe çevirip kontrol et
                if name.lower() not in excluded_names and len(name) > 1:
                    characters.append(name)
        
        # Remove duplicates and count
        from collections import Counter
        char_counts = Counter(characters)
        return dict(char_counts.most_common(10))  # Top 10 most frequent characters

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
        
        # Gutenberg ile ilgili keyword'leri filtrele
        filtered_keywords = []
        noise_words = {'gutenberg', 'project', 'ebook', 'ascii', 'kindle', 'transcriber'}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if not any(noise in keyword_lower for noise in noise_words):
                filtered_keywords.append(keyword)
        
        return filtered_keywords[:20]  # First 20

    def _extract_mood_words(self, doc):
        """Extract mood/atmosphere words (emotional adjectives/adverbs)."""
        mood_words = []
        for token in doc:
            if token.pos_ in ['ADJ', 'ADV']:
                # Sentiment check with TextBlob
                blob = TextBlob(token.text)
                if abs(blob.sentiment.polarity) > 0.1:  # Slightly emotional
                    mood_words.append(token.text)
        from collections import Counter
        mood_counts = Counter(mood_words)
        return dict(mood_counts.most_common(15))

    def _extract_literary_features(self, doc):
        """Extract literary features (common adjectives, verbs)."""
        adjectives = []
        verbs = []
        for token in doc:
            if token.pos_ == 'ADJ':
                adjectives.append(token.text)
            elif token.pos_ == 'VERB':
                verbs.append(token.text)
        from collections import Counter
        return {
            'common_adjectives': dict(Counter(adjectives).most_common(10)),
            'common_verbs': dict(Counter(verbs).most_common(10))
        }