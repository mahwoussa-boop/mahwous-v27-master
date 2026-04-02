import streamlit as st
import pandas as pd
from ..engines.ai_core import ai
from .styles import stat_card

def show_ai_tools_ui():
    st.title("🤖 أدوات الذكاء الاصطناعي الفائقة (V27)")
    
    tab_paste, tab_market, tab_verify = st.tabs(["📋 لصق وتحليل", "💹 بحث السوق", "🔍 تحقق من منتجين"])

    with tab_paste:
        st.subheader("تحويل النصوص العشوائية إلى جداول منظمة")
        st.info("الصق أي نص يحتوي على (اسم المنتج، السعر) وسيقوم AI بتحويله لجدول فوراً.")
        
        raw_text = st.text_area("أدخل البيانات هنا (من إكسيل أو نص عشوائي)", height=200)
        if st.button("🚀 تحليل وتحويل"):
            if raw_text:
                with st.spinner("جاري تفكيك البيانات وتنظيمها..."):
                    results = ai.analyze_pasted_data(raw_text)
                    if results:
                        df = pd.DataFrame(results)
                        st.success(f"✅ تم استخراج {len(df)} منتج بنجاح!")
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("📥 تحميل كـ CSV", data=csv, file_name="pasted_data.csv", mime="text/csv")
                    else:
                        st.error("عذراً، لم أستطع استخراج بيانات منظمة من هذا النص.")

    with tab_market:
        st.subheader("محرك البحث السوقي (Gemini Grounding)")
        product_query = st.text_input("اسم المنتج للبحث عن سعره الحقيقي", placeholder="مثلاً: Sauvage Dior 100ml")
        
        if st.button("🔍 ابحث في السوق"):
            if product_query:
                with st.spinner("جاري البحث في سيفورا، نايس ون، وفراجرانتيكا..."):
                    res = ai.search_market_price(product_query)
                    if res:
                        c1, c2 = st.columns(2)
                        c1.markdown(stat_card("نطاق السعر", res.get('market_price_range', 'N/A'), "💰"), unsafe_allow_html=True)
                        c2.markdown(stat_card("التوفر", res.get('availability', 'N/A'), "🏢"), unsafe_allow_html=True)
                        
                        st.markdown(f"⭐ **تقييم المستخدمين:** {res.get('user_rating', 'N/A')}")
                        st.success(f"👨‍🏫 **قرار الخبير:** {res.get('expert_verdict', 'N/A')}")
                    else:
                        st.error("لم أتمكن من الحصول على نتائج دقيقة حالياً.")

    with tab_verify:
        st.subheader("التحقق الذكي من تطابق منتجين")
        col1, col2 = st.columns(2)
        p1 = col1.text_input("المنتج الأول")
        p2 = col2.text_input("المنتج الثاني")
        
        if st.button("🧐 قارن الآن"):
            if p1 and p2:
                with st.spinner("جاري التدقيق المجهري..."):
                    res = ai.verify_match(p1, p2)
                    if res:
                        if res.get('match'):
                            st.success(f"✅ متطابقان بنسبة {res.get('confidence', 0)}%")
                        else:
                            st.error(f"❌ غير متطابقين بنسبة ثقة {res.get('confidence', 0)}%")
                        st.info(f"💡 **السبب:** {res.get('reason', 'N/A')}")
