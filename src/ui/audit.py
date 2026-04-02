import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz
from ..engines.analysis_orchestrator import load_data_file
from ..engines.mahwous_core import validate_export_product_dataframe
from ..engines.ai_core import ai

def show_audit_ui():
    st.title("🛠️ التدقيق والتحسين V27 (Zero-Error)")
    st.markdown("أدوات v11 المعزولة لضمان دقة البيانات وتحسين السيو.")
    
    tabs = st.tabs(["🔀 المقارنة", "🏪 مدقق المتجر", "🔍 معالج السيو"])
    
    with tabs[0]:
        st.subheader("🔀 المقارنة الذكية (Duplicate Checker)")
        st.info("قارن ملف المنتجات الجديدة بملف المتجر الأساسي لاكتشاف التكرار قبل الرفع.")
        
        c1, c2 = st.columns(2)
        new_file = c1.file_uploader("📦 ملف المنتجات الجديدة", type=["csv", "xlsx"], key="audit_new")
        base_file = c2.file_uploader("🏪 ملف المتجر الأساسي", type=["csv", "xlsx"], key="audit_base")
        
        if new_file and base_file:
            if st.button("🚀 ابدأ المقارنة (Fuzzy Match 88%)"):
                new_df = load_data_file(new_file)
                base_df = load_data_file(base_file)
                
                if new_df is not None and base_df is not None:
                    name_col = "المنتج" if "المنتج" in base_df.columns else "name"
                    base_names = base_df[name_col].dropna().astype(str).tolist()
                    
                    duplicates = []
                    progress = st.progress(0, "جاري فحص التكرار...")
                    for idx, row in new_df.iterrows():
                        p_name = str(row.get(name_col, row.get("أسم المنتج", "")))
                        match = process.extractOne(p_name, base_names, scorer=fuzz.token_set_ratio)
                        if match and match[1] >= 88:
                            duplicates.append({
                                "المنتج الجديد": p_name,
                                "المنتج المطابق في المتجر": match[0],
                                "نسبة التشابه": f"{int(match[1])}%"
                            })
                        progress.progress((idx + 1) / len(new_df))
                    
                    if duplicates:
                        st.warning(f"⚠️ تم اكتشاف {len(duplicates)} منتج مشبوه مكرر!")
                        st.table(pd.DataFrame(duplicates))
                    else:
                        st.success("✅ ملف المنتجات الجديدة نظيف ولا يوجد تكرار مشبوه.")

    with tabs[1]:
        st.subheader("🏪 مدقق المتجر (Salla Auditor)")
        st.info("ارفع ملف المتجر (بتنسيق سلة) لفحصه واكتشاف النواقص الهيكلية.")
        
        store_file = st.file_uploader("ارفع ملف منتجات سلة", type=["csv", "xlsx"], key="audit_store")
        if store_file:
            if st.button("🔍 فحص الملف (40 عموداً)"):
                df = load_data_file(store_file)
                is_valid, issues = validate_export_product_dataframe(df)
                
                if not is_valid:
                    st.error("❌ تم اكتشاف مشاكل في ملف المتجر:")
                    for issue in issues:
                        st.warning(issue)
                else:
                    st.success("✅ ملف المتجر سليم 100% ومتوافق مع بوابة سلة!")

    with tabs[2]:
        st.subheader("🔍 معالج السيو (SEO Processor)")
        st.info("ارفع ملف سلة لتوليد الحقول الناقصة (SEO HTML) لعدد محدد من المنتجات.")
        
        seo_file = st.file_uploader("ارفع ملف منتجات سلة للتحسين", type=["csv", "xlsx"], key="audit_seo")
        if seo_file:
            df = load_data_file(seo_file)
            limit = st.number_input("عدد المنتجات للمعالجة بـ AI", 1, 50, 5)
            
            if st.button("🪄 تحسين السيو (Anthropic Mode)"):
                p_bar = st.progress(0, "جاري توليد البيانات بـ AI...")
                results = []
                for idx, row in df.head(limit).iterrows():
                    details = f"الاسم: {row.get('أسم المنتج')}\nالماركة: {row.get('الماركة')}"
                    seo_html = ai.generate_seo_description(details)
                    df.at[idx, 'الوصف'] = seo_html
                    p_bar.progress((idx + 1) / limit)
                
                st.success(f"✅ تم تحسين {limit} منتج بنجاح!")
                st.dataframe(df.head(limit))
                
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("💾 تحميل ملف السيو المحدث", csv, "seo_improved.csv", "text/csv")
