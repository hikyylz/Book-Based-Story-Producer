This repo is about a self made project.
It is a book based story producer.
If a person wants to read a short story regarding to a literary book, They are able to create a shorter version of it. The produced story must contain same mood, features and vibe of the original literary book. So person would have an idea what the book make them feels like.

# Book-Based Story Producer

Bu proje, bir romanın PDF veya TXT dosyasını girdi olarak alır, metni analiz eder ve romanın edebi kimliğini (kişi isimleri, duygular, atmosfer, önemli kelimeler) çıkarır. Daha sonra bu verilerle AI kullanarak yeni bir hikaye üretir.

## Özellikler

- PDF/TXT dosya okuma
- Metin analizi (NER, sentiment, keyword extraction)
- Veri kategorizasyonu
- AI tabanlı hikaye üretimi

## Kurulum

1. Gereksinimleri yükleyin:

   ```
   pip install -r requirements.txt
   ```

2. Spacy modelini indirin:

   ```
   python -m spacy download en_core_web_sm
   ```

3. NLTK verilerini indirin:
   ```
   python -c "import nltk; nltk.download('punkt_tab')"
   ```

## Kullanım

1. OpenAI API anahtarınızı ortam değişkenine ayarlayın:

   ```
   export OPENAI_API_KEY='your-openai-api-key'
   ```

2. Python scriptini çalıştırın:

   ```python
   from main import StoryProducer

   producer = StoryProducer()
   producer.analyze_book('your_book.pdf')  # veya .txt
   producer.generate_story('output_story.txt')
   ```

3. Alternatif olarak example.py'yi düzenleyip çalıştırın.

## Özellikler

- **PDF/TXT Okuma:** pdfplumber ile PDF, standart okuma ile TXT.
- **Metin Analizi:**
  - NER ile kişi isimleri çıkarımı (spaCy).
  - Sentiment analizi (TextBlob).
  - Keyword extraction (RAKE).
  - Mood/Atmosfer kelimeleri (ADJ/ADV + sentiment).
  - Edebi özellikler (sık kullanılan sıfatlar, fiiller).
- **Hikaye Üretimi:** OpenAI GPT ile analiz verilerinden özgün hikaye.

## Çıktı

- `analysis_data.json`: Analiz verileri.
- `generated_story.txt`: Üretilen hikaye.

## Notlar

- Şu anda İngilizce metinler için optimize edilmiş.
- Büyük dosyalar için performans iyileştirmesi gerekebilir.
- API kullanımı için OpenAI kredisi gerekli.
