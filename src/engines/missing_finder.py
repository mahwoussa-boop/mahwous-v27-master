import pandas as pd
from rapidfuzz import process, fuzz
from .ai_core import ai
from .mahwous_core import apply_strict_pipeline_filters
from ..utils.mahwous_logging import get_logger

_logger = get_logger(__name__)

class MissingFinder:
    """محرك اكتشاف الفجوات البيعية والمنتجات المفقودة V27 - نسخة الحاجز الذكي التلقائي"""
    
    def __init__(self, our_df, competitor_df):
        self.our_df = our_df if our_df is not None else pd.DataFrame()
        self.comp_df = competitor_df if competitor_df is not None else pd.DataFrame()
        self.blocked_items = pd.DataFrame() # مستودع المطرودات للمراجعة اللاحقة
        self._prepare_our_data()

    def _prepare_our_data(self):
        """تجهيز بيانات متجرنا للمطابقة العكسية الصارمة"""
        if self.our_df.empty:
            self.our_names = []
            self.our_skus = set()
            return
            
        # تحديد أسماء الأعمدة (توقع salla format أو التنسيقات العامة)
        name_col = "المنتج" if "المنتج" in self.our_df.columns else "product_name"
        if name_col not in self.our_df.columns: name_col = self.our_df.columns[0]
        
        sku_col = "رقم_المنتج" if "رقم_المنتج" in self.our_df.columns else "sku"
        if sku_col not in self.our_df.columns: sku_col = "رمز المنتج sku" if "رمز المنتج sku" in self.our_df.columns else None

        self.our_names = self.our_df[name_col].dropna().astype(str).tolist()
        self.our_skus = set(self.our_df[sku_col].dropna().astype(str).tolist()) if sku_col else set()

    def find_gaps(self, progress_callback=None):
        """البحث الأولي عن الفجوات (سيتم تمرير النتائج عبر الحاجز آلياً)"""
        # في V27 المطور، استدعاء find_gaps يشغل الحاجز تلقائياً
        return self.smart_missing_barrier(progress_callback)

    def smart_missing_barrier(self, progress_callback=None, threshold=88):
        """الحاجز الذكي التلقائي: التصفية، حماية التستر، ومنع التكرار (Zero-Error)"""
        if self.comp_df.empty: 
            return pd.DataFrame()
        
        # 🟢 الخطوة 1: الفلترة الصارمة (قواعد mahwous_core: حجم 15مل، عينات، كلمات ممنوعة)
        name_col = "name" if "name" in self.comp_df.columns else "product_name"
        filtered_comp, blocked_by_core, _ = apply_strict_pipeline_filters(self.comp_df, name_col=name_col)
        
        missing_entries = []
        barrier_blocked = []
        total = len(filtered_comp)
        
        for idx, row in filtered_comp.iterrows():
            comp_name = str(row.get(name_col, ""))
            comp_sku = str(row.get("sku", row.get("gtin", ""))).strip()
            
            # 🟢 الخطوة 2: فحص الـ SKU (حماية مطلقة من التكرار)
            if comp_sku and comp_sku in self.our_skus:
                barrier_blocked.append(row)
                continue
                
            # 🟢 الخطوة 3: فحص المطابقة المزدوجة (Token Set Ratio)
            if self.our_names:
                # التحقق هل المنتج مكرر فعلياً عندنا باسم مختلف أو هجين
                match = process.extractOne(comp_name, self.our_names, scorer=fuzz.token_set_ratio)
                if match and match[1] >= threshold:
                    barrier_blocked.append(row)
                    continue # مكرر بنسبة عالية، إزاحته للمطرودات
            
            # منتج مفقود حقيقي وآمن للرفع
            entry = {
                "comp_name": comp_name,
                "comp_price": float(row.get('price', 0)),
                "comp_brand": row.get('brand', 'غير محدد'),
                "comp_image": row.get('image', ''),
                "comp_url": row.get('url', ''),
                "status": "missing",
                "normalized_name": "",
                "seo_description": "",
            }
            missing_entries.append(entry)
            
            if progress_callback:
                progress_callback((idx + 1) / total)

        # حفظ المطرودات للمراجعة في "مجلد مخفي" أو session state
        self.blocked_items = pd.concat([blocked_by_core, pd.DataFrame(barrier_blocked)]).drop_duplicates()
        
        return pd.DataFrame(missing_entries)

    def normalize_missing_names(self, missing_df, progress_callback=None):
        """تنسيق الأسماء بـ AI المزدوج (نفضل Anthropic)"""
        total = len(missing_df)
        for idx, row in missing_df.iterrows():
            if not row['normalized_name']:
                norm_name = ai.normalize_name(row['comp_name'])
                if norm_name:
                    missing_df.at[idx, 'normalized_name'] = norm_name
            if progress_callback:
                progress_callback((idx + 1) / total)
        return missing_df
