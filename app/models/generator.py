import google.genai as genai

class StoryGenerator:
    """Class for generating stories using Gemini AI."""

    def __init__(self, api_key):
        """Initialize with API key and client."""
        self.client = genai.Client(api_key=api_key)
        
        # Word count mapping
        self.length_map = {
            "short": 500,
            "medium": 1000,
            "long": 2000
        }
        
        # Style descriptions
        self.style_map = {
            "same": "in the same literary style as the original work",
            "modern": "with a modern, contemporary twist while keeping the core themes",
            "dramatic": "with heightened drama and emotional intensity",
            "poetic": "with poetic, lyrical prose and rich imagery"
        }

    def generate(self, analysis_data, length="medium", style="same"):
        """Generate a story from analysis data with customization options."""
        prompt = self._build_prompt(analysis_data, length, style)

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        return response.text

    def _build_prompt(self, data, length="medium", style="same"):
        """Build prompt from data with length and style options."""
        word_count = self.length_map.get(length, 1000)
        style_desc = self.style_map.get(style, self.style_map["same"])
        
        prompt = f"""Based on the following literary analysis of a classic novel, write an original short story that captures its essence {style_desc}.

=== LITERARY ANALYSIS ===

"""

        if 'characters' in data and data['characters']:
            char_list = list(data['characters'].keys())[:8]
            prompt += f"**Main Characters:** {', '.join(char_list)}\n"
            prompt += "(You may use these characters or create new ones inspired by their archetypes)\n\n"

        if 'sentiments' in data:
            sent = data['sentiments']
            mood = "positive and uplifting" if sent['polarity'] > 0.1 else "dark and melancholic" if sent['polarity'] < -0.1 else "neutral and contemplative"
            prompt += f"**Emotional Tone:** {mood} (Polarity: {sent['polarity']:.2f})\n"
            prompt += f"**Narrative Style:** {'Subjective and personal' if sent['subjectivity'] > 0.5 else 'Objective and observational'}\n\n"

        if 'keywords' in data and data['keywords']:
            keywords = data['keywords'][:12]
            prompt += f"**Key Themes & Concepts:** {', '.join(keywords)}\n\n"

        if 'mood_words' in data and data['mood_words']:
            mood_list = list(data['mood_words'].keys())[:10]
            prompt += f"**Atmospheric Words:** {', '.join(mood_list)}\n\n"

        if 'literary_features' in data:
            feats = data['literary_features']
            if 'common_adjectives' in feats:
                adj_list = list(feats['common_adjectives'].keys())[:8]
                prompt += f"**Descriptive Style (Adjectives):** {', '.join(adj_list)}\n"
            if 'common_verbs' in feats:
                verb_list = list(feats['common_verbs'].keys())[:8]
                prompt += f"**Action Style (Verbs):** {', '.join(verb_list)}\n\n"

        prompt += f"""=== STORY REQUIREMENTS ===

1. **Length:** Approximately {word_count} words
2. **Style:** Write {style_desc}
3. **Originality:** Create a NEW story inspired by the above elements, not a retelling
4. **Structure:** Include a clear beginning, middle, and end
5. **Language:** Use rich, literary prose that matches the source material's quality

Write the story now, starting directly with the narrative (no titles or meta-commentary):"""

        return prompt