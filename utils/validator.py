import re
import unicodedata

def sanitize_text(text: str, mode: str='game', max_length: int=None) -> str:
    if not text:
        return ''
    text = unicodedata.normalize('NFKC', text)
    text = ''.join((c for c in text if unicodedata.category(c) != 'Mn'))
    if mode == 'game':
        limit = max_length or 60
        text = re.sub('[^\\w\\s]', '', text)
        return re.sub('\\s+', ' ', text).strip()[:limit]
    if mode == 'info':
        limit = max_length or 4000
        text = re.sub('[^\\w\\s\\.,!\\?\\(\\)\\-_\\*]', '', text)
        return text[:limit]
    limit = max_length or 4000
    return text.replace('<', '&lt;').replace('>', '&gt;')[:limit]