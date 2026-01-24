import openai

class StoryGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def generate(self, analysis_data):
        """Analiz verilerinden hikaye üret."""
        prompt = self._build_prompt(analysis_data)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Veya gpt-4
            messages=[
                {"role": "system", "content": "Sen bir hikaye yazarısın. Verilen verilere dayanarak özgün bir kısa hikaye yaz."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    def _build_prompt(self, data):
        """Verilerden prompt oluştur."""
        prompt = "Aşağıdaki edebi özelliklere dayanarak, benzer bir edebi kimliğe sahip özgün bir kısa hikaye yaz:\n\n"

        if 'characters' in data:
            prompt += f"Kişiler: {', '.join(data['characters'].keys())}\n"

        if 'sentiments' in data:
            sent = data['sentiments']
            prompt += f"Genel Duygu: Polarity {sent['polarity']:.2f}, Subjectivity {sent['subjectivity']:.2f}\n"

        if 'keywords' in data:
            prompt += f"Önemli Kelimeler: {', '.join(data['keywords'][:10])}\n"

        if 'mood_words' in data:
            prompt += f"Atmosfer Kelimeleri: {', '.join(data['mood_words'].keys())}\n"

        if 'literary_features' in data:
            feats = data['literary_features']
            prompt += f"Sık Kullanılan Sıfatlar: {', '.join(feats['common_adjectives'].keys())}\n"
            prompt += f"Sık Kullanılan Fiiller: {', '.join(feats['common_verbs'].keys())}\n"

        prompt += "\nHikaye yaklaşık 500 kelime olsun ve yukarıdaki unsurları yansıtarak özgün bir öykü olsun."

        return prompt