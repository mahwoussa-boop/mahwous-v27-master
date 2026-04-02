import pandas as pd
import re
from ..utils.mahwous_logging import get_logger

_logger = get_logger(__name__)

# قائمة الكلمات الممنوعة المحدثة (Zero-Error Blacklist)
# ملاحظة: تم استبعاد "تستر" لأنها مربحة ومطلوبة.
BLACKLIST_KEYWORDS = [
    "عينة", "سمبل", "مجاني", "فارغ", "تقسيط", "تمارا", "تابي", 
    "sample", "decant", "توزيعات", "vial", "vials"
]

def apply_strict_pipeline_filters(df, name_col="name"):
    """
    تصفية صارمة للمنتجات (Zero-Error Policy):
    - حذف العناصر غير البيعية (عينات، تقسيط، سمبل).
    - حماية الـ "تستر" (Tester) لضمان مرورها.
    - حذف الأحجام أقل من 15 مل (Vials/Samples).
    """
    if df.empty:
        return df, pd.DataFrame(), 0

    initial_count = len(df)
    
    # 1. فلترة الكلمات الممنوعة (مع ضمان عدم مس كلمة تستر)
    pattern = "|".join(BLACKLIST_KEYWORDS)
    blocked_by_keyword = df[df[name_col].str.contains(pattern, case=False, na=False)]
    df = df[~df[name_col].str.contains(pattern, case=False, na=False)]
    
    # 2. فلترة الأحجام الصغير (أقل من 15 مل)
    size_pattern = r'(\d+\.?\d*)\s*(ml|مل)'
    def is_large_enough(name):
        matches = re.findall(size_pattern, str(name).lower())
        for val, unit in matches:
            if float(val) < 15: # القاعدة الجديدة: 15 مل كحد أدنى
                return False
        return True
    
    blocked_by_size = df[~df[name_col].apply(is_large_enough)]
    df = df[df[name_col].apply(is_large_enough)]
    
    # تجميع المطرودات للمراجعة اللاحقة
    blocked_df = pd.concat([blocked_by_keyword, blocked_by_size]).drop_duplicates()
    
    removed = initial_count - len(df)
    _logger.info(f"Strict Filter: {removed} items blocked (History archived).")
    
    return df, blocked_df, removed

def validate_export_product_dataframe(df):
    """
    بوابة سلة النهائية: التأكد من مطابقة الـ 40 عموداً بدقة 100%.
    """
    issues = []
    # يجب أن يكون عدد الأعمدة 40 بالضبط أو الأعمدة الأساسية موجودة
    expected_count = 40
    
    required_cols = ["أسم المنتج", "سعر المنتج", "الماركة", "الوصف"]
    
    # التحقق من وجود الأعمدة الأساسية (باعتبارها الأهم)
    missing_essential = [c for c in required_cols if c not in df.columns]
    if missing_essential:
        issues.append(f"الأعمدة الأساسية مفقودة: {missing_essential}")
        return False, issues

    # التحقق من البيانات الفارغة
    for col in required_cols:
        if df[col].isnull().any() or (df[col].astype(str).str.strip() == "").any():
            issues.append(f"توجد قيم فارغة في العمود الإلزامي: {col}")

    # التحقق من هيكل سلة (40 عمود)
    if len(df.columns) < expected_count:
        issues.append(f"هيكل الملف غير مكتمل. المسجل: {len(df.columns)} عمود، المطلوب: {expected_count} عمود.")

    return len(issues) == 0, issues
