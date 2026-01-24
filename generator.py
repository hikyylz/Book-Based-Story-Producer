import google.generativeai as genai

class StoryGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate(self, analysis_data):
        """Generate a story from analysis data."""
        prompt = self._build_prompt(analysis_data)

        response = self.model.generate_content(prompt)

        return response.text.strip()

    def _build_prompt(self, data):
        """Build prompt from data."""
        prompt = "Based on the following literary features, write an original short story that captures a similar literary identity:\n\n"

        if 'characters' in data:
            prompt += f"Characters: {', '.join(data['characters'].keys())}\n"

        if 'sentiments' in data:
            sent = data['sentiments']
            prompt += f"Overall Sentiment: Polarity {sent['polarity']:.2f}, Subjectivity {sent['subjectivity']:.2f}\n"

        if 'keywords' in data:
            prompt += f"Important Keywords: {', '.join(data['keywords'][:10])}\n"

        if 'mood_words' in data:
            prompt += f"Mood/Atmosphere Words: {', '.join(data['mood_words'].keys())}\n"

        if 'literary_features' in data:
            feats = data['literary_features']
            prompt += f"Common Adjectives: {', '.join(feats['common_adjectives'].keys())}\n"
            prompt += f"Common Verbs: {', '.join(feats['common_verbs'].keys())}\n"

        prompt += "\nThe story should be about 500 words and reflect the above elements in an original narrative."

        return prompt