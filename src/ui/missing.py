import streamlit as st
import pandas as pd
import os
import io
from ..engines.missing_finder import MissingFinder
from ..engines.salla_exporter import SallaExporter
from ..engines.mahwous_core import validate_export_product_dataframe, apply_strict_pipeline_filters
from ..engines.analysis_orchestrator import load_data_file

def show_missing_products():
    st.title("🔍 المنتجات المفقودة وتحليل الفرص (V27)")
    
    tab_list, tab_quick = st.tabs(["📋 قائمة المفقودات النظيفة", "➕ منتج سريع"])

    with tab_list:
        st.markdown("اكتشف ما يبيعه منافسوك بعد تطبيق **حاجز صفر خطأ (Zero-Error)**.")

        # التكامل: الكشف عن الملف الأخير المكسوب
        latest_scraped_file = "data/competitors_latest.csv"
        has_latest = os.path.exists(latest_scraped_file)

        # 1. قسم الملفات
        c1, c2 = st.columns(2)
        with c1:
            our_file = st.file_uploader("📦 كتالوجنا الحالي", type=["csv", "xlsx"], key="miss_our")
        with c2:
            if has_latest:
                st.success(f"✅ وُجدت بيانات مكسوبة حديثاً: {latest_scraped_file}")
                use_latest = st.checkbox("استخدام البيانات المكسوبة تلقائياً", value=True, key="use_latest_missing")
                comp_file = st.file_uploader("🏢 أو ارفع ملف منافس يدوي", type=["csv", "xlsx"], key="miss_comp") if not use_latest else None
            else:
                comp_file = st.file_uploader("🏢 ملف المنافس / الكشط", type=["csv", "xlsx"], key="miss_comp")
                use_latest = False

        if our_file and (comp_file or use_latest):
            if st.button("🔎 ابحث عن المفقودات (تفعيل الحاجز الآلي)"):
                our_df = load_data_file(our_file)
                comp_df = pd.read_csv(latest_scraped_file) if use_latest else load_data_file(comp_file)
                
                if our_df is not None and comp_df is not None:
                    finder = MissingFinder(our_df, comp_df)
                    with st.spinner("جاري فحص الفجوات وتطبيق الحاجز المزدوج..."):
                        # تشغيل الحاجز تلقائياً
                        missing_df = finder.find_gaps()
                        st.session_state.missing_df_raw = missing_df
                        st.session_state.blocked_df = finder.blocked_items
                        st.success(f"✅ تم العثور على {len(missing_df)} منتج مفقود آمن (بعد حظر {len(finder.blocked_items)} عنصر)!")
                        st.rerun()

        # 2. عرض النتائج النظيفة
        if "missing_df_raw" in st.session_state:
            df = st.session_state.missing_df_raw
            
            st.divider()
            st.subheader(f"📦 المفقودات النظيفة ({len(df)} منتج)")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("🪄 توحيد الأسماء (Anthropic/Gemini)"):
                    finder = MissingFinder(None, None)
                    p_bar = st.progress(0, "جاري التنسيق...")
                    df = finder.normalize_missing_names(df, lambda p: p_bar.progress(p))
                    st.session_state.missing_df_raw = df
                    st.success("✅ تم توحيد الأسماء!")
                    st.rerun()

            with col_btn3:
                if st.button("📥 تصدير لسلة (بوابة التدقيق)", type="primary"):
                    exporter = SallaExporter(df)
                    p_bar = st.progress(0, "جاري تحضير الملف...")
                    csv_data = exporter.export_to_salla_csv(lambda p: p_bar.progress(p))
                    
                    # التحقق الصارم النهائي قبل التحميل
                    latest_df = pd.read_csv(io.StringIO(csv_data))
                    is_valid, issues = validate_export_product_dataframe(latest_df) 
                    
                    if not is_valid:
                        st.error("❌ تم إيقاف التصدير! البيانات لا تطابق معايير سلة:")
                        for issue in issues: st.warning(issue)
                    else:
                        st.download_button(
                            label="💾 تحميل ملف سلة جاهز 100%",
                            data=csv_data,
                            file_name="mahwous_clean_export.csv",
                            mime="text/csv"
                        )
            
            st.dataframe(df[['comp_name', 'normalized_name', 'comp_price', 'comp_brand']], use_container_width=True)

            # 🔴 قسم العناصر المطرودة (Hidden/Expander)
            with st.expander("🛡️ عرض العناصر التي حجبها الحاجز الذكي (للمراجعة)"):
                if "blocked_df" in st.session_state:
                    st.warning("هذه العناصر تم حجبها لأنها قد تكون عينات، أحجام صغيرة، أو منتجات مكررة فعلياً في متجرك.")
                    st.dataframe(st.session_state.blocked_df, use_container_width=True)
                else:
                    st.write("لا توجد عناصر مطرودة حالياً.")

    with tab_quick:
        st.subheader("➕ إضافة منتج سريع لسلة")
        st.info("أضف صفاً واحداً بصيغة سلة (40 عموداً).")
        
        with st.form("quick_product_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("اسم المنتج")
            brand = col2.text_input("الماركة")
            price = col1.number_input("السعر")
            desc = st.text_area("وصف سريع")
            
            submitted = st.form_submit_button("📥 توليد صف سلة وتصديره")
            if submitted:
                 # منطق التوليد (سيمر عبر بوابة validate لاحقاً)
                 st.success("تم تجهيز المنتج للإضافة...")
