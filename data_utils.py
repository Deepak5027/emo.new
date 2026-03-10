
"""Data Processing & Management Module"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_to_csv(self, data: pd.DataFrame, filename: str = "journal_entries.csv"):
        filepath = self.data_dir / filename
        data.to_csv(filepath, index=False)
        print(f"✅ Data saved to {filepath}")
        return filepath
    
    def load_from_csv(self, filename: str = "journal_entries.csv") -> pd.DataFrame:
        filepath = self.data_dir / filename
        if not filepath.exists():
            print(f"⚠️ File {filepath} not found")
            return pd.DataFrame()
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        print(f"✅ Loaded {len(df)} entries from {filename}")
        return df
    
    def save_to_json(self, data: List[Dict], filename: str = "journal_entries.json"):
        filepath = self.data_dir / filename
        json_data = []
        for item in data:
            item_copy = item.copy()
            if 'date' in item_copy and hasattr(item_copy['date'], 'isoformat'):
                item_copy['date'] = item_copy['date'].isoformat()
            json_data.append(item_copy)
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        print(f"✅ Data saved to {filepath}")
        return filepath
    
    def load_from_json(self, filename: str = "journal_entries.json") -> List[Dict]:
        filepath = self.data_dir / filename
        if not filepath.exists():
            print(f"⚠️ File {filepath} not found")
            return []
        with open(filepath, 'r') as f:
            data = json.load(f)
        for item in data:
            if 'date' in item and isinstance(item['date'], str):
                item['date'] = datetime.fromisoformat(item['date'])
        print(f"✅ Loaded {len(data)} entries from {filename}")
        return data

class DataValidator:
    @staticmethod
    def validate_entry(entry: Dict) -> Tuple[bool, str]:
        required_fields = ['date', 'text', 'primary_emotion']
        for field in required_fields:
            if field not in entry:
                return False, f"Missing required field: {field}"
        if not isinstance(entry['text'], str) or len(entry['text'].strip()) == 0:
            return False, "Text field cannot be empty"
        valid_emotions = ['happy', 'anxious', 'sad', 'neutral', 'overwhelmed']
        if entry.get('primary_emotion') not in valid_emotions:
            return False, f"Invalid emotion: {entry.get('primary_emotion')}"
        return True, "Valid"
    
    @staticmethod
    def validate_dataset(data: List[Dict]) -> Dict:
        results = {
            'total_entries': len(data),
            'valid_entries': 0,
            'invalid_entries': 0,
            'errors': []
        }
        for i, entry in enumerate(data):
            is_valid, message = DataValidator.validate_entry(entry)
            if is_valid:
                results['valid_entries'] += 1
            else:
                results['invalid_entries'] += 1
                results['errors'].append(f"Entry {i}: {message}")
        return results

class DataGenerator:
    @staticmethod
    def generate_sample_data(num_entries: int = 30) -> List[Dict]:
        emotions_list = ['happy', 'anxious', 'sad', 'neutral', 'overwhelmed']
        sample_texts = {
            'happy': [
                "Today was amazing! I accomplished so much and feel incredibly grateful.",
                "Had a wonderful day with amazing people. Feeling on top of the world!",
                "Everything is going great. My mood is fantastic!",
            ],
            'anxious': [
                "Feeling very worried about the upcoming presentation. My heart won't stop racing.",
                "The stress is getting to me. I can't stop thinking about everything.",
                "Nervous about what tomorrow will bring. Can't sleep well.",
            ],
            'sad': [
                "Today was really difficult. I'm struggling with some deep feelings.",
                "Feeling down and low. Missing someone important.",
                "Everything feels hopeless right now. I don't know what to do.",
            ],
            'neutral': [
                "Another regular day. Nothing particularly exciting happened.",
                "Pretty much a normal day. Just going through the motions.",
                "Day was okay. Nothing special to report.",
            ],
            'overwhelmed': [
                "So many things to do and not enough time. Feeling completely drained.",
                "Everything is piling up. I feel lost and confused about what to do first.",
                "Burnt out. Too many demands and not enough capacity.",
            ]
        }
        entries = []
        base_date = datetime.now() - timedelta(days=num_entries)
        for i in range(num_entries):
            emotion = np.random.choice(emotions_list)
            date = base_date + timedelta(days=i)
            text = np.random.choice(sample_texts.get(emotion, sample_texts['neutral']))
            entry = {
                'date': date,
                'text': text,
                'primary_emotion': emotion,
                'emotions': np.random.choice(emotions_list, size=np.random.randint(1, 3), replace=False).tolist(),
                'sentiment_score': np.random.uniform(-1, 1),
                'mood_stability': np.random.uniform(0, 100),
                'word_count': len(text.split()),
                'emotional_intensity': np.random.uniform(0, 100),
                'timestamp': datetime.now().isoformat(),
            }
            entries.append(entry)
        return entries

class DataAnalyzer:
    @staticmethod
    def compute_statistics(data: List[Dict]) -> Dict:
        if not data:
            return {}
        df = pd.DataFrame(data)
        stats = {
            'total_entries': len(df),
            'avg_word_count': df['word_count'].mean() if 'word_count' in df else 0,
            'avg_sentiment': df['sentiment_score'].mean() if 'sentiment_score' in df else 0,
            'avg_intensity': df['emotional_intensity'].mean() if 'emotional_intensity' in df else 0,
            'avg_stability': df['mood_stability'].mean() if 'mood_stability' in df else 0,
        }
        if 'primary_emotion' in df:
            stats['emotion_distribution'] = df['primary_emotion'].value_counts().to_dict()
        return stats
