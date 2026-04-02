import sys
import os
import pandas as pd
import io

# إضافة المسار الحالي لتمكين الاستيراد من المجلد المحلي
sys.path.append(os.getcwd())

from src.engines.missing_finder import MissingFinder
from src.engines.salla_exporter import SallaExporter

def run_test():
    print("🚀 بدء تجربة نظام مهووس V27...")

    # 1. بيانات منتجات وهمية للتجربة
    our_data = {
        "product_name": ["Dior Sauvage EDT 100ml"],
        "price": [450]
    }
    comp_data = {
        "name": ["Dior Sauvage EDT 100ml", "Chanel No 5 Parfum 50ml"],
        "price": [440, 650],
        "brand": ["Dior", "Chanel"],
        "image": ["http://img1.jpg", "http://img2.jpg"]
    }
    
    our_df = pd.DataFrame(our_data)
    comp_df = pd.DataFrame(comp_data)
    
    print(f"📦 كتالوجنا: {len(our_df)} منتج")
    print(f"🏢 ملف المنافس: {len(comp_df)} منتج")

    # 2. البحث عن المفقودات
    finder = MissingFinder(our_df, comp_df)
    missing_df = finder.find_gaps()
    print(f"🔍 تم العثور على {len(missing_df)} منتج مفقود (المتوقع: 1 - Chanel)")

    # 3. توحيد الأسماء بـ AI (Normalizer)
    print("🪄 جاري توحيد الأسماء بـ AI...")
    missing_df = finder.normalize_missing_names(missing_df)
    for _, row in missing_df.iterrows():
        print(f"   - الأصل: {row['comp_name']} -> المنسق: {row['normalized_name']}")

    # 4. تصدير سلة (SEO + 40 عمود)
    print("📥 جاري توليد أوصاف SEO وتجهيز ملف سلة...")
    exporter = SallaExporter(missing_df)
    csv_content = exporter.export_to_salla_csv()
    
    # 5. التحقق من النتيجة
    result_df = pd.read_csv(io.StringIO(csv_content))
    print(f"📊 عدد أعمدة الملف الناتج: {len(result_df.columns)} (المتوقع: 40)")
    
    if len(result_df.columns) == 40:
        print("✅ تم التحقق: الملف يحتوي على 40 عموداً بدقة.")
    else:
        print(f"❌ خطأ: عدد الأعمدة {len(result_df.columns)} غير صحيح!")

    print("\n📝 لقطة من عمود الوصف (HTML):")
    desc_sample = result_df.iloc[0]['الوصف']
    print(str(desc_sample)[:300] + "...")
    
    # حفظ الملف للمراجعة اليدوية
    output_path = os.path.join(os.getcwd(), "test_salla_export.csv")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(csv_content)
    print(f"\n✅ تم حفظ ملف التجربة في: {output_path}")

if __name__ == "__main__":
    run_test()
