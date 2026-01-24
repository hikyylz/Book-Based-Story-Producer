import spacy
from textblob import TextBlob
from rake_nltk import Rake
import nltk

# NLTK verilerini indir (gerekirse)
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

    def analyze(self, text):
        """Analyze text and extract data into categories."""
        doc = self.nlp(text)

        # Characters (NER)
        characters = self._extract_characters(doc)

        # Sentiments
        sentiments = self._analyze_sentiment(text)

        # Keywords
        keywords = self._extract_keywords(text)

        # Mood/Atmosphere words (duygusal kelimeler)
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
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                characters.append(ent.text)
        # Tekrarları kaldır ve say
        from collections import Counter
        char_counts = Counter(characters)
        return dict(char_counts.most_common(10))  # En sık 10 karakter

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
        return self.rake.get_ranked_phrases()[:20]  # İlk 20

    def _extract_mood_words(self, doc):
        """Extract mood/atmosphere words (emotional adjectives/adverbs)."""
        mood_words = []
        for token in doc:
            if token.pos_ in ['ADJ', 'ADV']:
                # TextBlob ile sentiment kontrolü
                blob = TextBlob(token.text)
                if abs(blob.sentiment.polarity) > 0.1:  # Hafif duygusal
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