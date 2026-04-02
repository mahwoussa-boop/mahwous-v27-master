import streamlit as st
import pandas as pd
import os
from ..engines.analysis_orchestrator import AnalysisOrchestrator, load_data_file
from .components import product_result_card
from ..utils.db_manager import db

def show_competitors_analysis():
    st.title("📊 تحليل ومنافسة الأسعار (V27)")
    
    # 🔴 التكامل: الكشف عن الملف الأخير المكسوب
    latest_scraped_file = "data/competitors_latest.csv"
    has_latest = os.path.exists(latest_scraped_file)
    
    # 1. قسم رفع الملفات
    c1, c2 = st.columns(2)
    with c1:
        our_file = st.file_uploader("📦 كتالوج منتجاتنا (CSV/Excel)", type=["csv", "xlsx"])
    with c2:
        if has_latest:
            st.success(f"✅ وُجدت بيانات مكسوبة حديثاً: {latest_scraped_file}")
            use_latest = st.checkbox("استخدام البيانات المكسوبة تلقائياً", value=True)
            comp_file = st.file_uploader("🏢 أو ارفع ملف منافس يدوي", type=["csv", "xlsx"]) if not use_latest else None
        else:
            comp_file = st.file_uploader("🏢 ملف المنافس / الكشط", type=["csv", "xlsx"])
            use_latest = False

    if our_file and (comp_file or use_latest):
        if st.button("🚀 بدء التحليل الذكي"):
            our_df = load_data_file(our_file)
            
            if use_latest:
                comp_df = pd.read_csv(latest_scraped_file)
            else:
                comp_df = load_data_file(comp_file)
            
            if our_df is not None and comp_df is not None:
                orchestrator = AnalysisOrchestrator(our_df, comp_df)
                progress_bar = st.progress(0, "جاري مطابقة المنتجات والتحقق بـ AI...")
                
                results_df = orchestrator.run_analysis(
                    progress_callback=lambda p: progress_bar.progress(p)
                )
                
                st.session_state.analysis_results = results_df
                st.success("✅ اكتمل التحليل بنجاح!")
                db.log_event("analysis", "complete", f"items: {len(results_df)}")
                st.rerun()

    # 2. عرض النتائج (إذا وجدت)
    if "analysis_results" in st.session_state:
        df = st.session_state.analysis_results
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🟢 سعر أقل", "🔴 سعر أعلى", "✅ مطابق", "⚠️ للمراجعة", "⚪ مفقود"
        ])
        
        with tab1: render_results(df[df['status'] == 'lower'])
        with tab2: render_results(df[df['status'] == 'higher'])
        with tab3: render_results(df[df['status'] == 'approved'])
        with tab4: render_results(df[df['status'] == 'review'])
        with tab5: render_results(df[df['status'] == 'missing'])

def render_results(filtered_df):
    if filtered_df.empty:
        st.info("لا توجد منتجات في هذه الفئة حالياً.")
        return
        
    for _, row in filtered_df.iterrows():
        st.markdown(product_result_card(row), unsafe_allow_html=True)
