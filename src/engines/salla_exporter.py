import pandas as pd
import io
from .ai_core import ai
from ..utils.mahwous_logging import get_logger

_logger = get_logger(__name__)

class SallaExporter:
    """محرك تصدير المنتجات لمنصة سلة بتنسيق 40 عموداً V27"""
    
    HEADERS = [
        "النوع", "أسم المنتج", "تصنيف المنتج", "صورة المنتج", "وصف صورة المنتج", 
        "نوع المنتج", "سعر المنتج", "الوصف", "هل يتطلب شحن؟", "رمز المنتج sku", 
        "سعر التكلفة", "السعر المخفض", "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض", 
        "اقصي كمية لكل عميل", "إخفاء خيار تحديد الكمية", "اضافة صورة عند الطلب", 
        "الوزن", "وحدة الوزن", "الماركة", "العنوان الترويجي", "تثبيت المنتج", 
        "الباركود", "السعرات الحرارية", "MPN", "GTIN", "خاضع للضريبة ؟", 
        "سبب عدم الخضوع للضريبة", "[1] الاسم", "[1] النوع", "[1] القيمة", 
        "[1] الصورة / اللون", "[2] الاسم", "[2] النوع", "[2] القيمة", 
        "[2] الصورة / اللون", "[3] الاسم", "[3] النوع", "[3] القيمة", "[3] الصورة / اللون"
    ]

    def __init__(self, missing_df):
        self.df = missing_df

    def _generate_seo_descriptions(self, progress_callback=None):
        """توليد وصف SEO لكل منتج باستخدام ذكاء مهووس"""
        total = len(self.df)
        for idx, row in self.df.iterrows():
            if not row.get('seo_description'):
                details = f"الاسم: {row['normalized_name'] or row['comp_name']}\nالماركة: {row['comp_brand']}\nالسعر: {row['comp_price']}"
                html_desc = ai.generate_seo_description(details)
                if html_desc:
                    self.df.at[idx, 'seo_description'] = html_desc
            
            if progress_callback:
                progress_callback((idx + 1) / total)

    def export_to_salla_csv(self, progress_callback=None):
        """تحويل البيانات إلى ملف CSV متوافق مع سلة"""
        # 1. توليد الأوصاف أولاً
        self._generate_seo_descriptions(progress_callback)
        
        # 2. بناء الـ DataFrame النهائي
        salla_rows = []
        for _, row in self.df.iterrows():
            salla_row = {h: "" for h in self.HEADERS}
            
            # ملء البيانات الأساسية
            salla_row["النوع"] = "منتج جاهز"
            salla_row["أسم المنتج"] = row['normalized_name'] or row['comp_name']
            salla_row["تصنيف المنتج"] = "عطور"
            salla_row["صورة المنتج"] = row['comp_image']
            salla_row["سعر المنتج"] = row['comp_price']
            salla_row["الوصف"] = row['seo_description']
            salla_row["هل يتطلب شحن؟"] = "نعم"
            salla_row["الماركة"] = row['comp_brand']
            salla_row["خاضع للضريبة ؟"] = "نعم"
            
            salla_rows.append(salla_row)
        
        export_df = pd.DataFrame(salla_rows, columns=self.HEADERS)
        
        # تحويل لـ CSV مع BOM لدعم الأكسل بالعربية
        output = io.StringIO()
        export_df.to_csv(output, index=False, encoding="utf-8-sig")
        return output.getvalue()
