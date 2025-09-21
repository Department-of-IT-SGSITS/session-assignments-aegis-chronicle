import io
from typing import Iterable, Optional, Set, Dict, Any
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

def generate_wordcloud_image(
    articles: Iterable[Dict[str, Any]],
    custom_stopwords: Optional[Set[str]] = None,
    width: int = 800,
    height: int = 400,
    background_color: str = "white",
    fallback_text: str = "news world update",
    collocations: bool = True,
    stopwords_base: Optional[Set[str]] = None,
    random_state: Optional[int] = None
) -> bytes:
    text = " ".join(
        ((a.get("title") or "") + " " + (a.get("description") or "")).strip()
        for a in articles
    ).strip()

    if not text:
        text = fallback_text
        
    if stopwords_base is None:
        try:
            sw = set(stopwords.words('english'))
        except LookupError:            
            nltk.download('stopwords')
            sw = set(stopwords.words('english'))
    else:        
        sw = set(stopwords_base)

    if custom_stopwords:
        sw.update({s.lower() for s in custom_stopwords})
    
    wc = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        stopwords=sw,
        collocations=collocations,
        random_state=random_state
    ).generate(text)
    
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    return buf.getvalue()