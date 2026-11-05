import re
import string

# English stopwords with clinical/negation words carefully retained
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
    'now'
}
# Notice: 'not', 'no', 'never', 'severe', 'urgent' are deliberately excluded from STOPWORDS

CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "'re": " are",
    "'s": " is",
    "'d": " would",
    "'ll": " will",
    "'t": " not",
    "'ve": " have",
    "'m": " am"
}

def expand_contractions(text: str) -> str:
    for contraction, expansion in CONTRACTIONS.items():
        text = text.replace(contraction, expansion)
    return text

def clean_text(text: str) -> str:
    """Normalize text, remove excess whitespace and non-standard characters."""
    if not text:
        return ""
    text = text.lower().strip()
    text = expand_contractions(text)
    # Remove special punctuation but keep spaces and alphanumeric
    text = re.sub(r'[^a-zA-Z0-9\s\-\?\!\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text: str) -> list[str]:
    """Tokenize cleaned text into word tokens."""
    cleaned = clean_text(text)
    # Split on whitespace and strip trailing punctuation
    tokens = [re.sub(r'[^\w\-]', '', tok) for tok in cleaned.split()]
    return [tok for tok in tokens if tok]

def remove_stopwords(tokens: list[str]) -> list[str]:
    """Filter out common stopwords while preserving negation and clinically important words."""
    return [tok for tok in tokens if tok not in STOPWORDS]

def preprocess(text: str, filter_stops: bool = False) -> str:
    """Full preprocessing pipeline returning a normalized string."""
    tokens = tokenize(text)
    if filter_stops:
        tokens = remove_stopwords(tokens)
    return " ".join(tokens)
