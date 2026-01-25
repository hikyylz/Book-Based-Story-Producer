# Example Usage

from main import StoryProducer

# Define your Gemini API key in api_key.py

producer = StoryProducer()

# Test with a long story
test_text = """[Long story content here]"""  # Removed, using file instead

# Write test text to file (already done)
# with open('test_book.txt', 'w', encoding='utf-8') as f:
#     f.write(test_text)

# Analyze the book
producer.analyze_book('my_book_1.txt')

# Show analysis data
import json
with open('analysis_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print("Analysis Data:")
print(json.dumps(data, indent=2, ensure_ascii=False))

# Generate story (if API key is set)
producer.generate_story('my_generated_story.txt')

print("Test completed!")