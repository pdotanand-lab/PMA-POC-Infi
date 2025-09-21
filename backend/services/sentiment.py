from typing import List, Dict
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

def score_sentiment(segments: List[Dict]) -> List[float]:
    scores = []
    for seg in segments:
        s = sia.polarity_scores(seg['text'])['compound']
        scores.append(s)
    return scores
