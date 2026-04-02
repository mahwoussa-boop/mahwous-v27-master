import json
import requests
import time
from ..utils.mahwous_logging import get_logger
from .prompts import (
    SYSTEM_MATCH_VERIFIER, SYSTEM_PRICING_EXPERT, SYSTEM_SEO_EXPERT, 
    SYSTEM_NAME_NORMALIZER, SYSTEM_MARKET_RESEARCHER, SYSTEM_PASTE_ANALYZER,
    SYSTEM_FRAGRANTICA_RESEARCHER
)
from config import GEMINI_API_KEYS, ANTHROPIC_API_KEY

_logger = get_logger(__name__)

class AICore:
    """إدارة استدعاءات الذكاء الاصطناعي (Anthropic + Gemini) V27"""
    
    def __init__(self):
        self.gemini_keys = GEMINI_API_KEYS
        self.anthropic_key = ANTHROPIC_API_KEY
        self.current_key_idx = 0

    def _get_next_gemini_key(self):
        if not self.gemini_keys: return None
        key = self.gemini_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.gemini_keys)
        return key

    def call_anthropic(self, prompt, system_instruction="", response_type="text"):
        """محرك Anthropic (Claude 3 Haiku/Sonnet) المفضل للسيو والأوصاف"""
        if not self.anthropic_key:
            return None
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "system": system_instruction,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                text = data['content'][0]['text']
                if response_type == "json":
                    try: return json.loads(text)
                    except: return None
                return text.strip()
            else:
                _logger.warning(f"Anthropic API Error {resp.status_code}: {resp.text}")
        except Exception as e:
            _logger.error(f"Anthropic Call Exception: {e}")
        return None

    def call_gemini(self, prompt, system_instruction="", retries=3, response_type="json"):
        """محرك Gemini (المحرك الافتراضي والاحتياطي)"""
        for _ in range(retries):
            key = self._get_next_gemini_key()
            if not key: break
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}],
            }
            if response_type == "json":
                payload["generationConfig"] = {"response_mime_type": "application/json"}
            
            try:
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    if response_type == "json":
                        try: return json.loads(text)
                        except: return None
                    return text.strip()
            except Exception: pass
            time.sleep(1)
        return None

    def call_ai(self, prompt, system_instruction="", response_type="json", prefer_anthropic=False):
        """الموزع الذكي: يحاول Anthropic أولاً إذا طُلب، ثم Gemini كبديل"""
        if prefer_anthropic and self.anthropic_key:
            res = self.call_anthropic(prompt, system_instruction, response_type)
            if res: return res
        
        return self.call_gemini(prompt, system_instruction, response_type=response_type)

    def verify_match(self, our_name, comp_name, our_price=0, comp_price=0):
        prompt = f"منتجنا: {our_name} (سعر: {our_price})\nمنتج المنافس: {comp_name} (سعر: {comp_price})"
        return self.call_ai(prompt, SYSTEM_MATCH_VERIFIER, response_type="json")

    def suggest_price(self, our_name, comp_price, cost_price=0):
        prompt = f"المنتج: {our_name}\nسعر المنافس: {comp_price}\nسعر التكلفة لدينا: {cost_price}"
        return self.call_ai(prompt, SYSTEM_PRICING_EXPERT, response_type="json")

    def normalize_name(self, raw_name):
        return self.call_ai(raw_name, SYSTEM_NAME_NORMALIZER, response_type="text", prefer_anthropic=True)

    def generate_seo_description(self, product_details):
        return self.call_ai(product_details, SYSTEM_SEO_EXPERT, response_type="text", prefer_anthropic=True)

    def search_market_price(self, product_name):
        """إجراء بحث سوقي شامل وجلب الأسعار الحقيقية"""
        return self.call_ai(product_name, SYSTEM_MARKET_RESEARCHER, response_type="json")

    def analyze_pasted_data(self, raw_text):
        """تحليل النصوص المنسوخة من إكسيل وتحويلها لجدول منظم"""
        return self.call_ai(raw_text, SYSTEM_PASTE_ANALYZER, response_type="json")

    def get_fragrantica_details(self, perfume_name):
        """جلب تفاصيل المكونات والصورة من فراجرانتيكا عبر AI"""
        return self.call_ai(perfume_name, SYSTEM_FRAGRANTICA_RESEARCHER, response_type="json")

# تصدير الكائن الافتراضي
ai = AICore()
