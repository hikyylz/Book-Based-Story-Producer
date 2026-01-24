# Örnek Kullanım

from main import StoryProducer

# Gemini API anahtarınızı api_key.py dosyasında tanımlayın

producer = StoryProducer()

# Kısa test metni ile test
test_text = """
In the quiet town of Eldridge, where the autumn leaves whispered secrets to the wind, lived a young woman named Eliza. She was known for her mysterious smile and the way her eyes held stories untold. One foggy morning, as the sun struggled to pierce the mist, Eliza discovered an old letter hidden in her grandmother's attic. The letter spoke of a hidden treasure, buried beneath the ancient oak tree that stood sentinel at the edge of town.

Eliza's heart raced with excitement and fear. The treasure promised wealth, but also danger. She decided to embark on this adventure, unaware that it would change her life forever. Along the way, she met a kind stranger named Thomas, whose gentle nature contrasted with the stormy weather that seemed to follow them.

As they dug beneath the oak, the ground trembled, and a hidden chamber revealed itself. Inside were not gold coins, but ancient books filled with wisdom and forgotten tales. Eliza realized that the true treasure was the knowledge and the bonds formed in the pursuit.

The story ended with Eliza and Thomas sharing stories by the fireplace, their laughter echoing through the night, proving that some treasures are found not in gold, but in the warmth of human connection.
"""

# Test için metni dosyaya yaz
with open('test_book.txt', 'w', encoding='utf-8') as f:
    f.write(test_text)

# Kitabı analiz et
producer.analyze_book('test_book.txt')

# Analiz verilerini göster
import json
with open('analysis_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print("Analiz Verileri:")
print(json.dumps(data, indent=2, ensure_ascii=False))

# Hikaye üret (API anahtarı varsa)
# producer.generate_story('output_story.txt')

print("Test tamamlandı!")