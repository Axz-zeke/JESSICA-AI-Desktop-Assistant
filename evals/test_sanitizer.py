import re
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def sanitize_for_speech_and_display(raw_text: str):
    emotion = "warm"
    emo_match = re.search(r'<(?:emotion|EMOTION):\s*([a-zA-Z]+)>|\[(?:emotion|EMOTION):\s*([a-zA-Z]+)\]', raw_text)
    if emo_match:
        emotion = (emo_match.group(1) or emo_match.group(2)).lower().strip()
    
    text = re.sub(r'<(?:emotion|EMOTION):\s*[a-zA-Z]+>|\[(?:emotion|EMOTION):\s*[a-zA-Z]+\]', '', raw_text)
    # Remove markdown bold/italic formatting keeping the text inside
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', '', text)  # Actions like *smiles*
    
    # Remove emojis
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    text = re.sub(r'[\uFE00-\uFE0F]', '', text)
    text = re.sub(r'[\u200D]', '', text)
    
    # Remove ASCII emoticons
    text = re.sub(r'(?:[:;=8][\-~]?[)D(\]\[pP/\\*|oO]|<3|\b(?:lol|rofl|lmao)\b)', '', text, flags=re.IGNORECASE)
    
    # Remove markdown headings, backticks, list prefixes
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'`+', '', text)
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+[\.\)]\s+', '', text, flags=re.MULTILINE)
    
    # Normalize spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s+([,?.!])', r'\1', text)
    text = text.strip()
    return text, emotion

if __name__ == "__main__":
    input_sample = "<emotion: playful> *smiles* Hey there! \U0001F60A :) **How's it going?**"
    cleaned, emo = sanitize_for_speech_and_display(input_sample)
    print("Input:  ", input_sample)
    print("Cleaned:", repr(cleaned))
    print("Emotion:", emo)
    assert cleaned == "Hey there! How's it going?", f"Expected 'Hey there! How\'s it going?', got {cleaned!r}"
    assert emo == "playful", f"Expected 'playful', got {emo!r}"
    print("Unit test PASSED perfectly!")
