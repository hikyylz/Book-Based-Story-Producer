import os
import json
from analyzer import BookAnalyzer
from generator import StoryGenerator
from api_key import GEMINI_API_KEY

class StoryProducer:
    """Main class for book-based story production."""

    def __init__(self, api_key=None):
        """Initialize with API key and components."""
        self.api_key = api_key or GEMINI_API_KEY
        self.analyzer = BookAnalyzer()
        self.generator = StoryGenerator(self.api_key)
        self.analysis_data = {}

    def analyze_book(self, file_path):
        """Analyze book file and extract features."""
        text = self._load_text(file_path)
        self.analysis_data = self.analyzer.analyze(text)
        # Save data
        with open('analysis_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
        print("Analysis completed and saved.")

    def generate_story(self, output_file='generated_story.txt'):
        """Generate new story from analysis data."""
        if not self.analysis_data:
            raise ValueError("Analyze the book first.")
        story = self.generator.generate(self.analysis_data)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(story)
        print(f"Story generated: {output_file}")

    def _load_text(self, file_path):
        """Load text from PDF or TXT file."""
        if file_path.endswith('.pdf'):
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() + '\n'
            return text
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError("Unsupported file format. Use PDF or TXT.")

if __name__ == "__main__":
    producer = StoryProducer()
    # Example usage
    # producer.analyze_book('book.pdf')
    # producer.generate_story()