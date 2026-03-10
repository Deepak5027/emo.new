
"""Emotion Detection Model Module"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class EmotionClassifier:
    def __init__(self):
        self.emotions = ['happy', 'anxious', 'sad', 'neutral', 'overwhelmed']
        self.emotion_keywords = {
            'happy': ['happy', 'great', 'wonderful', 'amazing', 'joy', 'love', 'fantastic', 'excited', 'positive', 'grateful'],
            'anxious': ['anxious', 'worried', 'nervous', 'stress', 'panic', 'fear', 'tense', 'uneasy', 'dread', 'apprehensive'],
            'sad': ['sad', 'depressed', 'unhappy', 'miserable', 'grief', 'sorrow', 'devastated', 'hopeless', 'lonely', 'blue'],
            'neutral': ['okay', 'fine', 'normal', 'regular', 'usual', 'routine', 'ordinary', 'typical', 'average'],
            'overwhelmed': ['overwhelmed', 'exhausted', 'tired', 'burnt out', 'drained', 'helpless', 'lost', 'confused', 'scattered']
        }
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        emotion_scores = {emotion: 0.0 for emotion in self.emotions}
        for emotion, keywords in self.emotion_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = min(matches / max(len(keywords), 1), 1.0)
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v / total for k, v in emotion_scores.items()}
        else:
            emotion_scores = {emotion: 1.0 / len(self.emotions) for emotion in self.emotions}
        return emotion_scores
    
    def get_dominant_emotion(self, text: str) -> Tuple[str, float]:
        scores = self.detect_emotions(text)
        dominant = max(scores.items(), key=lambda x: x[1])
        return dominant
    
    def analyze_multiple_entries(self, texts: List[str]) -> pd.DataFrame:
        results = []
        for text in texts:
            emotion_scores = self.detect_emotions(text)
            dominant_emotion, confidence = self.get_dominant_emotion(text)
            results.append({
                'text': text,
                'primary_emotion': dominant_emotion,
                'confidence': confidence,
                **emotion_scores
            })
        return pd.DataFrame(results)

class SentimentAnalyzer:
    def __init__(self):
        self.positive_words = [
            'good', 'great', 'amazing', 'wonderful', 'excellent', 'fantastic',
            'love', 'happy', 'joy', 'beautiful', 'perfect', 'awesome',
            'best', 'incredible', 'brilliant', 'outstanding'
        ]
        self.negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'sad', 'depressed',
            'angry', 'frustrated', 'annoyed', 'worst', 'pathetic', 'useless',
            'stupid', 'angry', 'disgusting', 'disappointing'
        ]
        self.intensifiers = ['very', 'so', 'really', 'extremely', 'absolutely']
    
    def analyze_sentiment(self, text: str) -> float:
        text_lower = text.lower()
        words = text_lower.split()
        sentiment_score = 0.0
        for i, word in enumerate(words):
            intensity = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensity = 1.5
            if word in self.positive_words:
                sentiment_score += intensity * 0.1
            elif word in self.negative_words:
                sentiment_score -= intensity * 0.1
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        return sentiment_score
    
    def get_sentiment_label(self, score: float) -> str:
        if score > 0.3:
            return "Positive"
        elif score < -0.3:
            return "Negative"
        else:
            return "Neutral"

class TextPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = ' '.join(text.split())
        return text
    
    @staticmethod
    def extract_features(text: str) -> Dict[str, float]:
        cleaned = TextPreprocessor.clean_text(text)
        words = cleaned.split()
        features = {
            'word_count': len(words),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            'sentence_count': cleaned.count('.') + cleaned.count('!') + cleaned.count('?'),
            'has_exclamation': '!' in text,
            'has_question': '?' in text,
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        }
        return features
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> List[str]:
        cleaned = TextPreprocessor.clean_text(text).lower()
        words = cleaned.split()
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'is', 'are', 'was', 'were', 'been', 'be',
        }
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        from collections import Counter
        counter = Counter(keywords)
        return [word for word, _ in counter.most_common(top_n)]
