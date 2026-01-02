import re

def chunk_text_smart(text, max_words=180, min_words=32):
    paras = [p for p in re.split(r'[\n\.]{2,}|[\r\n]{2,}', text) if p.strip()]
    chunks = []
    for para in paras:
        words = para.split()
        if len(words) < min_words:
            continue
        elif len(words) > max_words:
            for i in range(0, len(words), max_words):
                cw = words[i:i+max_words]
                if len(cw) >= min_words:
                    chunks.append(" ".join(cw))
        else:
            chunks.append(para)
    return chunks