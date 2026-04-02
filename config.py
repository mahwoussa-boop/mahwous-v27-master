import os
import streamlit as st
from datetime import datetime

# ─── معلومات التطبيق ───────────────────────
APP_TITLE = "Mahwous Smart V27.0"
APP_ICON = "🦅"
VERSION = "27.0 - Rebirth"

# ─── مسارات الملفات ────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# مسار قاعدة البيانات الرئيسي
DB_PATH = os.environ.get("MAHWOUS_DB_PATH") or os.path.join(DATA_DIR, "mahwous_v27.db")

# ─── إعدادات الذكاء الاصطناعي (Safe Access) ──────────
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except:
        return default

def get_gemini_api_keys():
    """تحميل مفاتيح Gemini من الأسرار أو البيئة"""
    keys = []
    # 1. من Streamlit Secrets
    s_keys = get_secret("GEMINI_API_KEYS", get_secret("GEMINI_API_KEY", []))
    if isinstance(s_keys, list): keys.extend(s_keys)
    elif s_keys: keys.extend([k.strip() for k in str(s_keys).split(",") if k.strip()])
    
    # 2. من متغيرات البيئة
    env_v = os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", ""))
    if env_v:
        keys.extend([k.strip() for k in env_v.split(",") if k.strip()])
    
    return list(dict.fromkeys(keys))

GEMINI_API_KEYS = get_gemini_api_keys()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") or get_secret("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or get_secret("OPENROUTER_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY") or get_secret("COHERE_API_KEY")

# ─── عتبات المطابقة والأتمتة ────────────────
AUTO_DECISION_CONFIDENCE = 92
MATCH_THRESHOLD = 85
HIGH_CONFIDENCE = 95
REVIEW_THRESHOLD = 75
PRICE_TOLERANCE = 5

# ─── الكلمات المفتاحية والقوائم ────────────────
KNOWN_BRANDS = [
    "Dior", "Chanel", "Gucci", "Tom Ford", "Creed", "Roja", "Xerjoff", "Amouage",
    "Lancome", "Giorgio Armani", "Yves Saint Laurent", "Versace", "Prada", "Valentino",
    "Bvlgari", "Hermes", "Dolce & Gabbana", "Burberry", "Givenchy", "Carolina Herrera",
    "Paco Rabanne", "Jean Paul Gaultier", "Hugo Boss", "Calvin Klein", "Lacoste",
    "Cartier", "Chloe", "Narciso Rodriguez", "Elie Saab", "Mancera", "Montale",
    "Byredo", "Diptyque", "Kilian", "Memo Paris", "Initio", "Parfums de Marly"
]

REJECT_KEYWORDS = ["sample", "عينة", "عينه", "decant", "تقسيم", "split", "miniature", "توزيعات"]
TESTER_KEYWORDS = ["tester", "تستر", "تيستر"]
SET_KEYWORDS = ["set", "طقم", "مجموعة", "gift", "هدية"]

# ─── الجدولة والأتمتة ──────────────────────
AUTO_SEARCH_INTERVAL_MINUTES = 360
AUTO_PUSH_TO_MAKE = False
