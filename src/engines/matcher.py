import re
import pandas as pd
from rapidfuzz import fuzz, process as rf_process
from ..utils.mahwous_logging import get_logger
from config import (KNOWN_BRANDS, REJECT_KEYWORDS, TESTER_KEYWORDS, SET_KEYWORDS)

_logger = get_logger(__name__)

# ─── قاموس المرادفات ────────────────────────
_SYN = {
    "eau de parfum":"edp", "parfum":"edp", "eau de toilette":"edt",
    "eau de cologne":"edc", "extrait de parfum":"extrait",
    "مل":"ml", "جرام":"g", "لتر":"l",
    "أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي"
}

_NOISE_RE = re.compile(
    r'\b(عطر|تستر|تيستر|tester|edp|edt|edc|parfum|perfume|'
    r'الرجالي|النسائي|للجنسين|رجالي|نسائي|'
    r'ml|مل|oz)\b|\b\d+(?:\.\d+)?\b',
    re.UNICODE | re.IGNORECASE
)

def normalize(text):
    """تطبيع قياسي للنصوص"""
    if not isinstance(text, str): return ""
    t = text.strip().lower()
    for src, dst in _SYN.items():
        t = t.replace(src, dst)
    t = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def normalize_name(text):
    """تطبيع هجومي للمطابقة (حذف كلمات الضجيج والأرقام)"""
    if not isinstance(text, str): return ""
    t = normalize(text)
    t = _NOISE_RE.sub(' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def extract_size(text):
    if not isinstance(text, str): return 0.0
    ml = re.findall(r'(\d+(?:\.\d+)?)\s*(?:ml|مل|oz)', text.lower())
    return float(ml[0]) if ml else 0.0

def extract_brand(text):
    if not isinstance(text, str): return ""
    n = normalize(text)
    for b in KNOWN_BRANDS:
        if normalize(b) in n: return b
    return ""

class CompIndex:
    """فهرس المنافس المطبَّع مسبقاً للمطابقة السريعة"""
    
    def __init__(self, df, name_col):
        self.df = df.reset_index(drop=True)
        self.raw_names = df[name_col].fillna("").astype(str).tolist()
        self.agg_names = [normalize_name(n) for n in self.raw_names]
        self.brands = [extract_brand(n) for n in self.raw_names]
        self.sizes = [extract_size(n) for n in self.raw_names]

    def search(self, our_name, our_brand="", our_size=0, top_n=5):
        """بحث سريع باستخدام RapidFuzz"""
        our_agg = normalize_name(our_name)
        
        # البحث الأولي
        matches = rf_process.extract(
            our_agg, self.agg_names,
            scorer=fuzz.token_set_ratio,
            limit=min(20, len(self.agg_names))
        )
        
        results = []
        for _, score, idx in matches:
            if score < 40: continue
            
            # فلاتر الماركة والحجم
            if our_brand and self.brands[idx] and normalize(our_brand) != normalize(self.brands[idx]):
                continue
            if our_size > 0 and self.sizes[idx] > 0 and abs(our_size - self.sizes[idx]) > 5:
                continue
                
            results.append({
                "name": self.raw_names[idx],
                "score": score,
                "index": idx,
                "brand": self.brands[idx],
                "size": self.sizes[idx]
            })
            
            if len(results) >= top_n: break
            
        return results
