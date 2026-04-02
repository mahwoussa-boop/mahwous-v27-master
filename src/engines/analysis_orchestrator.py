import pandas as pd
from .matcher import CompIndex
from .ai_core import ai
from ..utils.mahwous_logging import get_logger
from config import AUTO_DECISION_CONFIDENCE, MATCH_THRESHOLD

_logger = get_logger(__name__)

class AnalysisOrchestrator:
    """منسق عمليات التحليل والمطابقة V27"""
    
    def __init__(self, our_df, competitor_df, name_col="name"):
        self.our_df = our_df
        self.comp_df = competitor_df
        self.index = CompIndex(competitor_df, name_col)

    def run_analysis(self, progress_callback=None):
        """تشغيل التحليل الكامل لمنتجاتنا مقابل المنافس"""
        results = []
        total = len(self.our_df)
        
        for idx, row in self.our_df.iterrows():
            our_name = str(row.get('product_name', row.get('name', '')))
            our_price = float(row.get('price', 0))
            our_cost = float(row.get('cost_price', 0))
            
            # 1. البحث الأولي (Fuzzy Search)
            matches = self.index.search(our_name, top_n=3)
            
            best_match = None
            if matches:
                highest_fuzzy = matches[0]
                
                # 2. التحقق بـ AI إذا كان البحث غير يقيني (مثلاً سكور بين 50 و 95)
                if 50 < highest_fuzzy['score'] < 95:
                    ai_res = ai.verify_match(our_name, highest_fuzzy['name'], our_price, highest_fuzzy['price'])
                    if ai_res.get('match'):
                        best_match = highest_fuzzy
                        best_match['ai_verified'] = True
                        best_match['confidence'] = ai_res.get('confidence', 0.8)
                elif highest_fuzzy['score'] >= 95:
                    best_match = highest_fuzzy
                    best_match['ai_verified'] = False
                    best_match['confidence'] = 1.0

            # 3. تصنيف النتيجة
            entry = {
                "our_id": row.get('product_id', ''),
                "our_name": our_name,
                "our_price": our_price,
                "cost_price": our_cost,
                "match_name": best_match['name'] if best_match else "لم يتم العثور على مطابقة",
                "comp_price": best_match['price'] if best_match else 0,
                "score": best_match['score'] if best_match else 0,
                "status": self._determine_status(our_price, best_match['price'] if best_match else 0),
                "ai_verified": best_match.get('ai_verified', False) if best_match else False
            }
            results.append(entry)
            
            if progress_callback:
                progress_callback((idx + 1) / total)

        return pd.DataFrame(results)

    def _determine_status(self, our_price, comp_price):
        if comp_price <= 0: return "missing"
        if our_price < comp_price: return "lower"
        if our_price > comp_price: return "higher"
        return "approved"

def load_data_file(file):
    """محمل ملفات ذكي يدعم Excel و CSV"""
    import pandas as pd
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        _logger.error(f"Error loading file: {e}")
        return None
