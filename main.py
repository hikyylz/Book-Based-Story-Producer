import os
import json
from analyzer import BookAnalyzer
from generator import StoryGenerator
from api_key import GEMINI_API_KEY

class StoryProducer:
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.analyzer = BookAnalyzer()
        self.generator = StoryGenerator(self.api_key)
        self.analysis_data = {}

    def analyze_book(self, file_path):
        """Kitabı analiz et ve verileri çıkar."""
        text = self._load_text(file_path)
        self.analysis_data = self.analyzer.analyze(text)
        # Verileri kaydet
        with open('analysis_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
        print("Analiz tamamlandı ve kaydedildi.")

    def generate_story(self, output_file='generated_story.txt'):
        """Analiz verilerinden hikaye üret."""
        if not self.analysis_data:
            raise ValueError("Önce kitabı analiz edin.")
        story = self.generator.generate(self.analysis_data)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(story)
        print(f"Hikaye üretildi: {output_file}")

    def _load_text(self, file_path):
        """PDF veya TXT dosyasını yükle."""
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
            raise ValueError("Desteklenmeyen dosya formatı. PDF veya TXT kullanın.")

if __name__ == "__main__":
    producer = StoryProducer()
    # Örnek kullanım
    # producer.analyze_book('book.pdf')
    # producer.generate_story()